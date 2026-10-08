# LogMind (Python edition)

Log file analyzer in pure Python (standard library only, Python 3.8+) with an animated web dashboard.

## Files
- `analyzer.py`        - core analysis (regex, Counter, argparse, file handling) and CLI report
- `generate_sample.py` - sample log generator
- `server.py`          - local web server: serves the dashboard and analyzes uploads at /api/analyze
- `index.html`         - animated dashboard (works standalone too, with a JS fallback parser)
- `sample.log`         - ready-made sample

## Run
    python server.py                       # opens http://localhost:8000
    python analyzer.py sample.log          # text report in the terminal
    python analyzer.py sample.log --top 10 # more rows
    python analyzer.py sample.log --json   # writes report.json (drop it on the dashboard)
    python generate_sample.py 2000 > big.log

Log format: `YYYY-MM-DD HH:MM:SS LEVEL [source] message` (ERROR, WARN, INFO, DEBUG)
