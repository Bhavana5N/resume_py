# Python Resume Tools

Python CLIs to tailor a resume to a job description (.docx) and fetch matched jobs.

## Setup

```bash
cd resume_py
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Tailor resume to JD (generate .docx)

```bash
# JD file (create one): ../resume/input/jd.txt
python tailor.py --jd ../resume/input/jd.txt \
  --resume ../resume/input/resume.txt \
  --out output/tailored.docx \
  --name "Bhavana Nare"
```

- Output: `resume_py/output/tailored.docx`

## Match jobs for resume (fuzzy scoring)

### Config-based (recommended)
Edit `resume_py/config.json`:
```json
{
  "resume": "../resume/input/resume.txt",
  "top": 15,
  "fetch": {
    "mode": "free",
    "source": "remoteok",
    "query": "Python MLOps Engineer",
    "location": null
  },
  "output": { "dir": "output", "prefix": "matches_daily" }
}
```
Run:
```bash
python match.py --config config.json
```
This will fetch the latest 15 jobs from the configured source/query and score them against your resume, saving to `output/matches_daily_<timestamp>.json`.

### Free sources (no API key)
```bash
python match.py --resume ../resume/input/resume.txt --free-source remotive --query "Python MLOps Engineer" --top 15
```

### SerpAPI (optional)
```bash
export SERPAPI_KEY=YOUR_KEY
python match.py --config config.json --query "Python MLOps Engineer site:linkedin.com/jobs"
```

## Schedule daily (macOS/Linux)
- Using cron (runs every day at 8am):
```bash
crontab -e
# add line (adjust path and venv):
0 8 * * * cd /Users/bhavananare/github/webapp/resume_py && /Users/bhavananare/github/webapp/resume_py/.venv/bin/python match.py --config /Users/bhavananare/github/webapp/resume_py/config.json >> /Users/bhavananare/github/webapp/resume_py/output/cron.log 2>&1
```

## Notes
- Config takes precedence unless CLI flags are provided for specific fields.
- Free sources are public boards; fields vary. Results are filtered by keywords client-side.
- Matching uses RapidFuzz token-set ratio + title boosts; tune by changing your query and resume content.
