import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from rapidfuzz import fuzz

_non_alnum = re.compile(r"[^a-z0-9+#.\-\s]")


def read_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def tokenize_for_fuzz(text: str) -> str:
    text = (text or "").lower()
    text = _non_alnum.sub(" ", text)
    return " ".join(t for t in text.split() if len(t) > 1)


def load_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_jobs(local: str | None, url: str | None, here: Path) -> list[dict[str, Any]]:
    if local:
        with open(local, "r", encoding="utf-8") as f:
            return json.load(f)
    if url:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return resp.json()
    # default to sample from JS tool to avoid duplication
    with open(here.parent / "resume" / "jobs_sample.json", "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_serpapi_google_jobs(query: str, location: str | None, api_key: str, limit: int) -> list[dict[str, Any]]:
    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "api_key": api_key,
    }
    if location:
        params["location"] = location
    resp = requests.get("https://serpapi.com/search.json", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("jobs_results", []) or []

    results: list[dict[str, Any]] = []
    for it in items[:limit]:
        title = it.get("title") or ""
        company = it.get("company_name") or it.get("company") or ""
        loc = it.get("location") or ""
        desc = it.get("description") or ""
        url = None
        # Prefer direct apply_links if present
        apply_options = it.get("apply_options") or []
        if apply_options and isinstance(apply_options, list):
            # pick first
            url = apply_options[0].get("link") or apply_options[0].get("apply_link")
        if not url:
            related = it.get("related_links") or []
            if related:
                url = related[0].get("link")
        if not url:
            url = it.get("job_id")  # fallback id reference
        results.append({
            "title": title,
            "company": company,
            "location": loc,
            "description": desc,
            "url": url,
            "source": "serpapi_google_jobs"
        })
    return results


# ---------- Free sources (no API key required) ----------

def _query_match(text: str, query: str) -> bool:
    if not query:
        return True
    q_tokens = [t for t in tokenize_for_fuzz(query).split() if t]
    hay = tokenize_for_fuzz(text)
    return all(t in hay for t in q_tokens)


def fetch_remotive(query: str | None, limit: int) -> list[dict[str, Any]]:
    # Docs: https://remotive.com/api/remote-jobs
    params: dict[str, Any] = {}
    if query:
        params["search"] = query
    resp = requests.get("https://remotive.com/api/remote-jobs", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    jobs = data.get("jobs", []) or []
    results: list[dict[str, Any]] = []
    for it in jobs:
        title = it.get("title") or ""
        company = it.get("company_name") or ""
        loc = it.get("candidate_required_location") or it.get("location") or "Remote"
        desc = it.get("description") or ""
        url = it.get("url") or ""
        results.append({
            "title": title,
            "company": company,
            "location": loc,
            "description": desc,
            "url": url,
            "source": "remotive"
        })
        if len(results) >= limit:
            break
    return results


def fetch_remoteok(query: str | None, limit: int) -> list[dict[str, Any]]:
    # Docs: https://remoteok.com/api
    headers = {"User-Agent": "Mozilla/5.0 (compatible; JobMatcher/1.0)"}
    resp = requests.get("https://remoteok.com/api", headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    results: list[dict[str, Any]] = []
    for it in data:
        # First element can be legal notice (dict with 'legal')
        if isinstance(it, dict) and it.get("position"):
            title = it.get("position") or ""
            company = it.get("company") or ""
            loc = it.get("location") or "Remote"
            desc = it.get("description") or ""
            url = it.get("url") or it.get("apply_url") or ""
            combined = f"{title}\n{company}\n{loc}\n{desc}"
            if _query_match(combined, query or ""):
                results.append({
                    "title": title,
                    "company": company,
                    "location": loc,
                    "description": desc,
                    "url": url,
                    "source": "remoteok"
                })
                if len(results) >= limit:
                    break
    return results


def fetch_arbeitnow(query: str | None, limit: int) -> list[dict[str, Any]]:
    # Docs: https://www.arbeitnow.com/api/job-board-api
    resp = requests.get("https://www.arbeitnow.com/api/job-board-api", timeout=30)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("data", []) or []
    results: list[dict[str, Any]] = []
    for it in items:
        title = it.get("title") or it.get("position") or ""
        company = it.get("company") or ""
        loc = it.get("location") or "Remote"
        desc = it.get("description") or ""
        url = it.get("url") or ""
        combined = f"{title}\n{company}\n{loc}\n{desc}"
        if _query_match(combined, query or ""):
            results.append({
                "title": title,
                "company": company,
                "location": loc,
                "description": desc,
                "url": url,
                "source": "arbeitnow"
            })
            if len(results) >= limit:
                break
    return results


FREE_SOURCES = {
    "remotive": fetch_remotive,
    "remoteok": fetch_remoteok,
    "arbeitnow": fetch_arbeitnow,
}


def score_job(job: dict[str, Any], resume_text: str) -> float:
    title = job.get("title", "")
    fields = "\n".join([
        job.get("title", ""),
        job.get("company", ""),
        job.get("location", ""),
        job.get("description", ""),
    ])
    # token-set fuzzy similarity
    sim = fuzz.token_set_ratio(tokenize_for_fuzz(resume_text), tokenize_for_fuzz(fields))
    # boost relevant titles
    if re.search(r"mlops|machine\s+learning|data\s+engineer|full\s*stack|python", title.lower()):
        sim += 10
    return float(sim)


def resolve_from_config(cfg: dict[str, Any]) -> dict[str, Any]:
    # Normalize common fields
    fetch = cfg.get("fetch", {})
    mode = fetch.get("mode")  # "free" | "serpapi" | "json" | "url"
    source = fetch.get("source")  # e.g., remotive
    query = fetch.get("query")
    location = fetch.get("location")
    jobs_path = fetch.get("jobs")
    jobs_url = fetch.get("jobs_url")
    serpapi_key = fetch.get("serpapi_key") or os.getenv("SERPAPI_KEY")

    return {
        "resume": cfg.get("resume"),
        "top": int(cfg.get("top", 10)),
        "mode": mode,
        "source": source,
        "query": query,
        "location": location,
        "jobs": jobs_path,
        "jobs_url": jobs_url,
        "serpapi_key": serpapi_key,
        "output": cfg.get("output", {}),
    }


def main() -> None:
    here = Path(__file__).parent
    parser = argparse.ArgumentParser(description="Score and list top matching jobs for a given resume.")
    parser.add_argument("--resume", default=str(here.parent / "resume" / "input" / "resume.txt"), help="Path to resume text file")
    parser.add_argument("--jobs", default=None, help="Path to jobs JSON (array)")
    parser.add_argument("--jobs-url", dest="jobs_url", default=None, help="HTTP URL returning JSON jobs array")
    parser.add_argument("--top", type=int, default=10, help="Top N results")
    # Config support
    parser.add_argument("--config", default=None, help="Path to config JSON (overrides defaults)")
    # Free sources (no API key)
    parser.add_argument("--free-source", choices=list(FREE_SOURCES.keys()), default=None, help="Use a free jobs source (no API key)")
    # SerpAPI options (Google Jobs)
    parser.add_argument("--serpapi-key", default=os.getenv("SERPAPI_KEY"), help="SerpAPI key (optional)")
    parser.add_argument("--query", default=None, help="Search query, e.g., 'Python MLOps Engineer'")
    parser.add_argument("--location", default=None, help="Search location (used by some sources)")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    parser.add_argument("--out", default=str(here / "output" / f"matched_jobs_{ts}.json"), help="Output JSON path")
    args = parser.parse_args()

    # Load and merge config if provided (or if default exists)
    cfg_path = Path(args.config) if args.config else (here / "config.json")
    cfg_data: dict[str, Any] | None = None
    if cfg_path.exists():
        try:
            cfg_data = load_json(cfg_path)
        except Exception:
            cfg_data = None
    resolved_cfg: dict[str, Any] = resolve_from_config(cfg_data) if cfg_data else {}

    # Merge precedence: CLI > config > defaults
    resume_path = args.resume or resolved_cfg.get("resume") or str(here.parent / "resume" / "input" / "resume.txt")
    top_n = args.top if args.top else int(resolved_cfg.get("top", 10))

    # Source selection
    free_source = args.free_source or resolved_cfg.get("source") if resolved_cfg.get("mode") == "free" else args.free_source
    query = args.query or resolved_cfg.get("query")
    location = args.location or resolved_cfg.get("location")
    serpapi_key = args.serpapi_key or resolved_cfg.get("serpapi_key")
    jobs_arg = args.jobs or resolved_cfg.get("jobs")
    jobs_url_arg = args.jobs_url or resolved_cfg.get("jobs_url")

    # Output handling (configurable dir/prefix)
    out_cfg = resolved_cfg.get("output", {}) if resolved_cfg else {}
    out_path = args.out
    if out_cfg:
        out_dir = out_cfg.get("dir")
        prefix = out_cfg.get("prefix", "matched_jobs")
        if out_dir:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = str(Path(here / out_dir / f"{prefix}_{stamp}.json"))

    resume_text = read_text(Path(resume_path))

    jobs: list[dict[str, Any]]
    # Priority: explicit free source -> SerpAPI (if key+query) -> JSON/url/local sample
    if free_source and query:
        fetcher = FREE_SOURCES.get(free_source)
        if not fetcher:
            raise SystemExit(f"Unknown free source: {free_source}")
        jobs = fetcher(query, top_n)
    elif serpapi_key and query:
        jobs = fetch_serpapi_google_jobs(query, location, serpapi_key, top_n)
    else:
        jobs = load_jobs(jobs_arg, jobs_url_arg, here)

    scored = []
    for job in jobs:
        s = score_job(job, resume_text)
        scored.append({**job, "score": round(s, 2)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[: top_n]

    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(top, f, indent=2)

    print("Top matches:")
    for j in top:
        line = f"- [{j['score']}] {j.get('title','')} @ {j.get('company','')} ({j.get('location','')})"
        if j.get("url"):
            line += f" - {j['url']}"
        print(line)
    print("Saved to:", os.path.abspath(out_file))


if __name__ == "__main__":
    main()
