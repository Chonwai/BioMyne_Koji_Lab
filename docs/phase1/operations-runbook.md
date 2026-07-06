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
