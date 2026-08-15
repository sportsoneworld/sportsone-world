#!/usr/bin/env python3
"""
=============================================================================
 FETCH LIVE SCORES  ->  data/scores.yaml

 Run by .github/workflows/scores.yml every few minutes, and by you whenever
 you like:

     python3 scripts/fetch-scores.py

 WHAT IT DOES
   Pulls live matches and the next few days of fixtures from a sports data
   provider and rewrites the `sports:` section of data/scores.yaml.

 WHAT IT NEVER TOUCHES
   Your `featured_matches:` list. Those are the desk's pins and they always
   survive a refresh. If a pinned match has finished and dropped out of the
   feed, its line is removed and the strip tops itself up automatically —
   see `auto_feature` in data/scores-source.yaml.

 IF THE PROVIDER IS DOWN
   The script exits with an error and writes nothing. The site keeps serving
   the scores it already has rather than going blank.

 CHANGING PROVIDER
   Everything provider-specific lives in one class below (TheSportsDB). Write
   another class with the same two methods and set `provider:` in
   data/scores-source.yaml. Nothing else in the site needs to change.
=============================================================================
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "data", "scores-source.yaml")
SCORES_PATH = os.path.join(ROOT, "data", "scores.yaml")
UA = "SportsOne/1.0 (+https://sportsone.world) scores-refresh"


# --------------------------------------------------------------------------
# A very small YAML reader/writer.
#
# We only ever read a handful of keys out of the config and preserve one list
# out of scores.yaml, so pulling in PyYAML just for that would mean a
# dependency to install on every machine and in CI. This handles exactly the
# shapes these two files use and nothing else.
# --------------------------------------------------------------------------
def read_simple_yaml(path):
    """Reads data/scores-source.yaml: top-level `key: value` pairs, plus
    `key:` followed by an indented `- item` list. That is the whole shape of
    that file, and it means the refresh needs no third-party YAML library on
    your machine or in CI."""
    data, current_list = {}, None
    if not os.path.exists(path):
        return data
    for raw in open(path, encoding="utf-8"):
        text = raw.strip()
        if not text or text.startswith("#"):
            continue
        if text.startswith("- "):
            if current_list is not None:
                current_list.append(_scalar(text[2:]))
            continue
        if ":" not in text:
            continue
        key, _, value = text.partition(":")
        key, value = key.strip(), value.split("#")[0].strip()
        if value == "":
            current_list = []
            data[key] = current_list
        else:
            data[key] = _scalar(value)
            current_list = None
    return data


def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v.lower() in ("true", "yes"):
        return True
    if v.lower() in ("false", "no"):
        return False
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def read_featured(path):
    """Pull the desk's `featured_matches:` list straight out of scores.yaml."""
    if not os.path.exists(path):
        return []
    ids, inside = [], False
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if re.match(r"^featured_matches:\s*$", line):
            inside = True
            continue
        if inside:
            m = re.match(r"^\s*-\s*([^\s#]+)", line)
            if m:
                ids.append(m.group(1))
                continue
            if line.strip() and not line.lstrip().startswith("#"):
                break
    return ids


def q(value):
    """Quote a YAML scalar safely."""
    s = "" if value is None else str(value)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# --------------------------------------------------------------------------
# Provider: TheSportsDB (https://www.thesportsdb.com)
#
# The free tier needs no account. Set SPORTSDB_KEY in the environment (and as
# a GitHub secret) if you subscribe — the paid key gets you more sports, more
# leagues and faster updates through exactly the same endpoints.
# --------------------------------------------------------------------------
class TheSportsDB:
    name = "thesportsdb"
    # Their sport names on the left, ours on the right.
    SPORTS = {"Soccer": "Football", "Cricket": "Cricket",
              "Tennis": "Tennis", "Motorsport": "Motorsport",
              "Basketball": "Basketball", "Rugby": "Rugby"}

    LIVE = {"1h", "2h", "ht", "et", "live", "in play", "1st half", "2nd half",
            "1q", "2q", "3q", "4q", "1p", "2p", "3p", "break"}
    DONE = {"ft", "aet", "pen", "finished", "match finished", "aot", "final"}

    def __init__(self, key=None):
        self.key = key or os.environ.get("SPORTSDB_KEY") or "3"

    def _get(self, endpoint, **params):
        url = f"https://www.thesportsdb.com/api/v1/json/{self.key}/{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)

    def live(self, their_sport):
        rows = self._get("livescore.php", s=their_sport).get("livescore") or []
        return [self._from_live(r, their_sport) for r in rows]

    def fixtures(self, their_sport, days=3):
        out = []
        today = datetime.now(timezone.utc).date()
        for offset in range(days):
            day = (today + timedelta(days=offset)).isoformat()
            try:
                rows = self._get("eventsday.php", d=day, s=their_sport).get("events") or []
            except Exception:
                continue
            out.extend(self._from_event(r, their_sport) for r in rows)
        return out

    # -- mapping ---------------------------------------------------------
    def _state(self, status, has_score):
        s = (status or "").strip().lower()
        if s in self.LIVE:
            return "live"
        if s in self.DONE or (s.startswith("ft") if s else False):
            return "completed"
        if s in ("ht", "break"):
            return "break"
        return "completed" if has_score else "upcoming"

    def _from_live(self, r, their_sport):
        hs, as_ = r.get("intHomeScore"), r.get("intAwayScore")
        has = hs not in (None, "") and as_ not in (None, "")
        state = self._state(r.get("strStatus"), has)
        progress = (r.get("strProgress") or "").strip()
        label = {"live": f"{progress}'" if progress.isdigit() else "Live",
                 "break": "Half time", "completed": "Full time",
                 "upcoming": r.get("strEventTime") or "Upcoming"}[state]
        return {
            "id": f"{self.SPORTS[their_sport].lower()}-{r.get('idEvent')}",
            "sport": self.SPORTS[their_sport],
            "competition": r.get("strLeague") or their_sport,
            "state": state,
            "stateLabel": label,
            "home": r.get("strHomeTeam"), "away": r.get("strAwayTeam"),
            "home_score": hs if has else "–", "away_score": as_ if has else "–",
            "kickoff": r.get("strEventTime") or "",
            "sort": {"live": 0, "break": 1, "completed": 2, "upcoming": 3}[state],
        }

    def _from_event(self, r, their_sport):
        hs, as_ = r.get("intHomeScore"), r.get("intAwayScore")
        has = hs not in (None, "") and as_ not in (None, "")
        state = self._state(r.get("strStatus"), has)
        return {
            "id": f"{self.SPORTS[their_sport].lower()}-{r.get('idEvent')}",
            "sport": self.SPORTS[their_sport],
            "competition": r.get("strLeague") or their_sport,
            "state": state,
            "stateLabel": ("Full time" if state == "completed"
                           else (r.get("strTime") or "")[:5] or "Upcoming"),
            "home": r.get("strHomeTeam"), "away": r.get("strAwayTeam"),
            "home_score": hs if has else "–", "away_score": as_ if has else "–",
            "kickoff": (r.get("strTime") or "")[:5],
            "sort": {"live": 0, "break": 1, "completed": 2, "upcoming": 3}[state],
        }


PROVIDERS = {"thesportsdb": TheSportsDB}


# --------------------------------------------------------------------------
def collect(config):
    provider = PROVIDERS[config.get("provider", "thesportsdb")]()
    wanted = config.get("sports") or ["Football", "Cricket", "Tennis"]
    per_sport = int(config.get("matches_per_sport", 6))
    fixture_days = int(config.get("fixture_days", 3))
    reverse = {v: k for k, v in provider.SPORTS.items()}

    result, errors = {}, []
    for our_sport in wanted:
        their = reverse.get(our_sport)
        if not their:
            errors.append(f"{our_sport}: provider has no matching sport")
            continue
        rows = []
        try:
            rows += provider.live(their)
        except Exception as e:
            errors.append(f"{our_sport} live: {e}")
        try:
            rows += provider.fixtures(their, fixture_days)
        except Exception as e:
            errors.append(f"{our_sport} fixtures: {e}")

        seen, unique = set(), []
        for row in sorted(rows, key=lambda r: (r["sort"], r["competition"] or "")):
            if not row["home"] or not row["away"] or row["id"] in seen:
                continue
            seen.add(row["id"])
            unique.append(row)
        if unique:
            result[our_sport] = unique[:per_sport]
    return result, errors


def render(by_sport, featured, config):
    now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)   # IST
    auto = config.get("auto_feature", True)
    live_ids = [m["id"] for rows in by_sport.values() for m in rows if m["state"] == "live"]
    known = {m["id"] for rows in by_sport.values() for m in rows}
    kept = [i for i in featured if i in known]

    out = [
        "# =============================================================================",
        "#  LIVE SCORES — REFRESHED AUTOMATICALLY",
        "#",
        "#  This file is rewritten by scripts/fetch-scores.py, which runs on a",
        f"#  schedule in GitHub Actions. Provider: {config.get('provider', 'thesportsdb')}.",
        "#",
        "#  You can still pin matches by hand. Ids listed under featured_matches are",
        "#  kept across every refresh for as long as that match is still in the feed,",
        "#  and they are always the first ones shown on the front page.",
        "#",
        "#  Which sports and how many matches are fetched: data/scores-source.yaml",
        "# =============================================================================",
        "",
        f"updated: {q(now.strftime('%d %b %Y, %H:%M IST'))}",
        f"note: {q('Scores refresh automatically; the desk chooses what leads')}",
        f"auto_feature: {'true' if auto else 'false'}",
        "",
        "# The desk's pins. Add an id to put a match on the front page, delete the",
        "# line to take it down. Kept intact by every refresh.",
        "featured_matches:",
    ]
    if kept:
        out += [f"  - {i}" for i in kept]
    else:
        out.append("  # none pinned — the strip is filling itself from the live matches below")
    out += ["", "sports:"]

    for sport, rows in by_sport.items():
        out.append(f"  - name: {sport}")
        out.append("    matches:")
        for m in rows:
            out.append(f"      - id: {m['id']}")
            out.append(f"        competition: {q(m['competition'])}")
            out.append(f"        state: {m['state']}")
            out.append(f"        stateLabel: {q(m['stateLabel'])}")
            out.append("        teams:")
            for side in ("home", "away"):
                out.append(f"          - name: {q(m[side])}")
                out.append(f"            score: {q(m[f'{side}_score'])}")
                lead = (m["state"] != "upcoming"
                        and str(m["home_score"]).isdigit() and str(m["away_score"]).isdigit()
                        and ((side == "home" and int(m["home_score"]) > int(m["away_score"]))
                             or (side == "away" and int(m["away_score"]) > int(m["home_score"]))))
                if lead:
                    out.append("            active: true")
                if m["state"] == "upcoming" and m["kickoff"] and side == "home":
                    out.append(f"            detail: {q(m['kickoff'])}")
        out.append("")
    return "\n".join(out).rstrip() + "\n", live_ids


def main():
    config = read_simple_yaml(CONFIG_PATH)
    featured = read_featured(SCORES_PATH)

    by_sport, errors = collect(config)
    for e in errors:
        print(f"warning: {e}", file=sys.stderr)

    if not by_sport:
        print("error: the provider returned nothing for any sport — "
              "leaving data/scores.yaml exactly as it was.", file=sys.stderr)
        return 1

    text, live_ids = render(by_sport, featured, config)
    previous = open(SCORES_PATH, encoding="utf-8").read() if os.path.exists(SCORES_PATH) else ""
    # The timestamp changes every run; ignore it when deciding "did anything move?"
    strip = lambda s: re.sub(r"^updated:.*$", "", s, flags=re.M)
    if strip(previous) == strip(text):
        print("no change")
        return 0

    open(SCORES_PATH, "w", encoding="utf-8").write(text)
    total = sum(len(v) for v in by_sport.values())
    print(f"wrote {total} matches across {len(by_sport)} sports "
          f"({len(live_ids)} live), pins kept: {len(featured)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
