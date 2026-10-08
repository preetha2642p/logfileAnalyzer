#!/usr/bin/env python3
"""LogMind analyzer: errors, warnings, frequent events and activity statistics.

Log format: YYYY-MM-DD HH:MM:SS LEVEL [source] message
Usage:  python analyzer.py app.log [--top 10] [--json]
"""
import argparse, json, re, sys
from collections import Counter
from pathlib import Path

LINE = re.compile(r"^(\d{4}-\d\d-\d\d)\s+(\d\d):\d\d:\d\d\s+(ERROR|WARN(?:ING)?|INFO|DEBUG)\s+\[([^\]]+)\]\s+(.*)$")
LEVELS = ("ERROR", "WARN", "INFO", "DEBUG")


def analyze(text: str, top: int = 5, max_lines: int = 2000) -> dict:
    levels, hours, events, sources = Counter(), [0] * 24, Counter(), Counter()
    lines, skipped = [], 0
    for raw in text.splitlines():
        if not raw.strip():
            continue
        m = LINE.match(raw)
        if not m:
            skipped += 1
            continue
        _, hour, lvl, src, msg = m.groups()
        lvl = "WARN" if lvl.startswith("WARN") else lvl
        levels[lvl] += 1
        hours[int(hour)] += 1
        events[re.sub(r"\d+", "N", msg)] += 1          # group "after 30s" with "after 45s"
        sources[src] += 1
        lines.append({"l": lvl, "raw": raw, "t": raw[:19], "s": src, "m": msg})
    errors = [{"t": x["t"], "src": x["s"], "msg": x["m"]} for x in lines if x["l"] == "ERROR"][-top:]
    return {
        "total": len(lines), "skipped": skipped,
        "first": lines[0]["t"] if lines else "-", "last": lines[-1]["t"] if lines else "-",
        "levels": {k: levels[k] for k in LEVELS}, "hours": hours,
        "events": events.most_common(top), "sources": sources.most_common(top),
        "errors": errors, "lines": lines[:max_lines],
    }


def print_report(r: dict, path: str) -> None:
    rate = r["levels"]["ERROR"] * 100 / r["total"] if r["total"] else 0
    print(f"=============== LOGMIND REPORT ===============\nFile  : {path}")
    print(f"Span  : {r['first']} -> {r['last']}\nLines : {r['total']} ({r['skipped']} skipped)")
    print("----------------- LEVELS ---------------------")
    for k, v in r["levels"].items():
        print(f"{k:<6}{v:>6}" + (f"  ({rate:.1f}%)" if k == "ERROR" else ""))
    print("------------- FREQUENT EVENTS ----------------")
    for msg, n in r["events"]:
        print(f"{n:>6}  {msg}")
    print("---------------- TOP SOURCES -----------------")
    for s, n in r["sources"]:
        print(f"{n:>6}  {s}")
    print("--------------- BUSIEST HOURS ----------------")
    for h, n in sorted(enumerate(r["hours"]), key=lambda x: -x[1])[:3]:
        print(f"{h:02d}:00  {n} events")
    print("-------------- RECENT ERRORS -----------------")
    for e in r["errors"]:
        print(f"{e['t']} [{e['src']}] {e['msg']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="LogMind log analyzer")
    ap.add_argument("logfile"); ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--json", action="store_true", help="write report.json for the dashboard")
    a = ap.parse_args()
    p = Path(a.logfile)
    if not p.is_file():
        print(f"Error: cannot read '{a.logfile}'", file=sys.stderr); return 1
    r = analyze(p.read_text(encoding="utf-8", errors="replace"), a.top)
    if a.json:
        r.pop("lines"); Path("report.json").write_text(json.dumps(r)); print("Wrote report.json")
    else:
        print_report(r, a.logfile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
