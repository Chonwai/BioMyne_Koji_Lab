-- 006: Crawl4AI migration — source-level provider routing
-- Adds crawler_provider to sources for routing between local Crawl4AI and Firecrawl Cloud.

alter table sources add column if not exists crawler_provider text not null default 'local';

-- Seed the 3 hard sources that must keep using Firecrawl Cloud (routing decision, see docs/phase1/crawl4ai-migration-engineering-spec.md §4.3)
update sources set crawler_provider = 'firecrawl_cloud'
where name in ('Endpoints News', 'BioCentury', 'Science');
