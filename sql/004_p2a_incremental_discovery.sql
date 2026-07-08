create table if not exists source_discovery_state (
  source_id uuid primary key references sources(id) on delete cascade,
  cursor_type text,
  last_discovery_at timestamptz,
  last_cursor_published_at timestamptz,
  last_cursor_url text,
  last_map_at timestamptz,
  last_sitemap_checkpoint jsonb not null default '{}'::jsonb,
  last_successful_discovery_at timestamptz,
  cooldown_until timestamptz,
  error_count integer not null default 0,
  last_error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table articles add column if not exists normalized_url text;
alter table articles add column if not exists content_hash text;
alter table articles add column if not exists discovery_method text;
alter table articles add column if not exists last_scraped_at timestamptz;
alter table articles add column if not exists analysis_version text;
alter table articles add column if not exists analysis_fingerprint jsonb not null default '{}'::jsonb;
alter table articles add column if not exists last_analyzed_at timestamptz;

update articles
set normalized_url = coalesce(normalized_url, url),
    last_scraped_at = coalesce(last_scraped_at, created_at),
    last_analyzed_at = coalesce(last_analyzed_at, created_at),
    analysis_fingerprint = coalesce(analysis_fingerprint, '{}'::jsonb)
where normalized_url is null
   or last_scraped_at is null
   or last_analyzed_at is null
   or analysis_fingerprint = '{}'::jsonb;

alter table articles alter column normalized_url set not null;

create unique index if not exists idx_articles_normalized_url on articles(normalized_url);
create index if not exists idx_articles_url on articles(url);
create index if not exists idx_articles_content_hash on articles(content_hash);
create index if not exists idx_articles_discovery_method on articles(discovery_method);
create index if not exists idx_articles_last_scraped_at on articles(last_scraped_at);
create index if not exists idx_source_discovery_state_last_discovery_at on source_discovery_state(last_discovery_at);

update entities
set canonical_name = lower(trim(name))
where canonical_name is null;

create index if not exists idx_entities_canonical_name on entities(canonical_name, entity_type);