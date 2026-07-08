# BioMyne Koji Phase 1 Operations Runbook

## 1. Pause Scheduled Runs Safely

1. Stop the active worker profile.
2. Confirm no run is currently in progress.
3. Record the pause reason and timestamp.
4. Resume only after the blocking issue is resolved.

## 2. Check Ollama Status

```bash
curl http://localhost:11434/api/tags
```

Expected: a list of locally available models.

## 3. Check Firecrawl Connectivity

```bash
curl -H "Authorization: Bearer $FIRECRAWL_API_KEY" https://api.firecrawl.dev/v1/credits
```

Expected: current credit information or a valid authenticated response.

## 4. Inspect Latest Failed Runs

Use Supabase SQL editor:

```sql
select * from crawl_runs
where status <> 'success'
order by started_at desc
limit 10;
```

## 5. Recover from Partial Failure

1. identify failed sources and failed articles
2. retry source-level failures first
3. retry article analysis for rows marked `failed` or `needs_review`
4. verify whether a digest resend is needed

## 6. Roll Back One Bad Run

1. mark delivery logs as superseded or rolled back
2. soft-mark invalid article rows
3. preserve trace and logs for audit
4. do not hard-delete evidence during Phase 1

## 7. Tune Crawl Breadth Safely

When coverage is too shallow, tune discovery breadth in this order:

1. increase `MAX_ARTICLES_PER_SOURCE` for all sources
2. add `MAX_ARTICLES_PER_SOURCE_OVERRIDES` for priority sources such as `STAT News` or `Nature Biotechnology`
3. widen Firecrawl map breadth with `DISCOVERY_MAP_LIMIT_MULTIPLIER` / `DISCOVERY_MAP_MIN_LIMIT`
4. only then lower `DISCOVERY_MIN_CANDIDATE_SCORE` or `DISCOVERY_DATE_SCORE_BONUS`

Recommended starting point:

```bash
MAX_ARTICLES_PER_SOURCE=15
MAX_ARTICLES_PER_SOURCE_OVERRIDES="STAT News=20,Nature Biotechnology=18,Science=10"
DISCOVERY_MAP_LIMIT_MULTIPLIER=20
DISCOVERY_MAP_MIN_LIMIT=80
DISCOVERY_MIN_CANDIDATE_SCORE=4
DISCOVERY_DATE_SCORE_BONUS=4
```

If Firecrawl credits tighten, reduce map breadth before reducing the per-source article cap for the highest-value sources.

Do not leave `DISCOVERY_MAP_LIMIT_MULTIPLIER=20` untouched without watching credit usage. At 11 sources, broad map expansion can materially increase Firecrawl consumption per run.
