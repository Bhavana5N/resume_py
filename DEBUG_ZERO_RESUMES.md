# Debug Guide: Zero Resumes Generated

## Your Situation

```
🔍 FILTERING STAGES:
  1️⃣  Total jobs fetched: 109
  2️⃣  After score filter (>= 40.0): 3
  3️⃣  Sponsorship check: Blocked: 0 | Passed: 3
  4️⃣  Resumes created: 0 ❌
```

**Problem:** 3 jobs passed all filters but **0 resumes were generated**

---

## Root Cause Analysis

### Stage 1: Score Filter Too Strict ⚠️
```
109 jobs fetched → 3 jobs passed score filter (97% removed!)
```

This means **most jobs scored below 40**. The score threshold is too high.

**Fix:** Lower `min_score` in `config.json`
```json
{
  "min_score": 30,           // Lower from 40
  "tailor_threshold": 30     // Lower from 40
}
```

---

### Stage 2: Resume Generation Failed 🔴
```
3 jobs passed all filters → 0 resumes created
```

Even though jobs passed filters, NO resumes were created. This means jobs failed at the **resume generation stage**.

---

## Possible Reasons for Zero Resumes

### Reason 1: Job Descriptions Are Empty/Too Short
```
[cover] 1/3: Meta - Software Engineer | Score: 103.2 | JD length: 0 chars
```

Jobs with no descriptions cannot generate tailored resumes.

**Check:** Look for `JD length: 0 chars` or `JD length: 10 chars` in logs

**Fix:** If jobs have URLs, system tries to:
1. Fetch from URL (`[fetch]` logs)
2. Use LLM extractor (`[extractor]` logs)
3. Create minimal JD (`[fallback]` logs)

If all fail, job is skipped.

---

### Reason 2: auto_tailor_resume is False
```json
{
  "auto_tailor_resume": false  // ❌ DISABLE RESUME GENERATION
}
```

If this is `false`, the system **won't generate resumes**!

**Fix:**
```json
{
  "auto_tailor_resume": true   // ✅ Enable resume generation
}
```

---

### Reason 3: use_job_app_gen or use_llm_resumer is False
```json
{
  "openai": {
    "enabled": false           // ❌ OpenAI disabled
  }
}
```

If OpenAI is disabled AND neither `use_job_app_gen` nor `use_llm_resumer` is enabled, resumes won't be generated.

**Fix:**
```json
{
  "openai": {
    "enabled": true,           // ✅ Enable OpenAI
    "model": "gpt-4o-mini"
  }
}
```

---

### Reason 4: Jobs Have No URLs
```
❌ NO URL in job data
```

Jobs without URLs cannot be processed for description fetching.

**Fix:** Check if Selenium scraping is working properly

---

### Reason 5: LLM Generation Failed Silently
```
[ERROR] Failed to generate application package for Meta: API Error
```

The resume generation tried but failed (API error, timeout, etc.)

**Fix:** Check logs for:
- `[ERROR]`
- `[jobgen] ⚠️`
- `[llm] ⚠️`

---

## Step-by-Step Debugging

### Step 1: Check Configuration
```bash
grep -A5 "auto_tailor\|openai\|min_score\|use_job_app_gen" config.json
```

**Must have:**
```json
{
  "auto_tailor_resume": true,
  "min_score": 30,
  "tailor_threshold": 30,
  "openai": {
    "enabled": true,
    "model": "gpt-4o-mini"
  }
}
```

---

### Step 2: Run with Debug Logging
```bash
python match.py --config config.json 2>&1 | tee debug.log
```

Then search for issues:

```bash
# Find all errors
grep "\[ERROR\]\|\[skip\]" debug.log

# Find score distribution
grep "Average score\|Max score\|Min score" debug.log

# Find resume generation issues
grep "\[jobgen\]\|\[llm\]\|\[cover\]" debug.log | head -20

# Find description extraction
grep "\[fetch\]\|\[extractor\]\|\[fallback\]\|JD length" debug.log
```

---

### Step 3: Update Configuration

**Minimum working config:**
```json
{
  "min_score": 30,
  "tailor_threshold": 30,
  "top_per_company_limit": 2,
  "target_roles": [],
  "auto_tailor_resume": true,
  "openai": {
    "enabled": true,
    "model": "gpt-4o-mini"
  }
}
```

---

## Solution Checklist

- [ ] **Score threshold too high?**
  - Lower `min_score` to 30 or lower
  - Run: `grep "Average score\|Max score" debug.log`

- [ ] **auto_tailor_resume disabled?**
  - Set `"auto_tailor_resume": true`

- [ ] **OpenAI disabled?**
  - Set `"openai.enabled": true`

- [ ] **Job descriptions empty?**
  - Check for `JD length: 0 chars`
  - Verify URLs are being fetched
  - Check `[fetch]`, `[extractor]`, `[fallback]` logs

- [ ] **LLM generation failing?**
  - Search logs for `[ERROR]` or `[llm]` warnings
  - Check OpenAI API key is valid
  - Check API quota/rate limits

- [ ] **Parallelization timeout?**
  - Set `"parallel_workers": 1` (disable parallel)
  - Or increase timeout values

---

## Quick Fix: Recommended Config

Copy this to `config.json`:

```json
{
  "resume": "input/resume.yml",
  "top": 15,
  "country": "usa",
  "fetch_limit": 100,
  "min_score": 30,              // ⬇️ LOWERED from 40
  "tailor_threshold": 30,       // ⬇️ LOWERED from 40
  "top_per_company": false,
  "top_per_company_limit": 2,   // ⬆️ INCREASED from 1
  "parallel_workers": 1,         // ⬇️ DISABLE PARALLEL
  "auto_tailor_resume": true,   // ✅ MUST BE TRUE
  "openai": {
    "enabled": true,            // ✅ MUST BE TRUE
    "model": "gpt-4o-mini"
  },
  "target_roles": [],           // Empty = all roles
  "target_locations": [],       // Empty = all locations
  "save_fetched": true,
  "selenium_only": true,
  "companies": ["meta", "google", "amazon"]  // Start with 3
}
```

---

## Run Again

```bash
python match.py --config config.json 2>&1 | tee debug.log

# Check results
tail -30 debug.log
```

**Expected output:**
```
📊 JOB FILTERING & RESUME GENERATION SUMMARY
  1️⃣  Total jobs fetched: 109
  2️⃣  After score filter (>= 30.0): 50+
  3️⃣  Sponsorship check: Passed: 50+
  4️⃣  Resumes created: 10+ ✅
```

---

## Still Having Issues?

1. **Share debug log snippet:**
   ```bash
   grep "\[ERROR\]\|\[jobgen\]\|\[cover\]" debug.log | head -30
   ```

2. **Check if OpenAI API key is valid:**
   ```bash
   echo $OPENAI_API_KEY
   ```

3. **Check if descriptions are being fetched:**
   ```bash
   grep "JD length" debug.log | head -10
   ```

4. **Disable LLM features temporarily:**
   ```json
   {
     "use_job_desc_extractor": false,
     "use_llm_parser": false,
     "openai.enabled": true
   }
   ```


