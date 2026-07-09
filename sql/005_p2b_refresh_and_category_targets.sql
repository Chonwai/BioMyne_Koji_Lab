alter table sources add column if not exists refresh_enabled boolean;
alter table sources add column if not exists refresh_window_days integer;
alter table sources add column if not exists refresh_cadence_hours integer;
alter table sources add column if not exists refresh_priority text;

update sources
set refresh_enabled = false
where refresh_enabled is null;

update sources
set refresh_priority = 'low'
where refresh_priority is null;

alter table sources alter column refresh_enabled set default false;
alter table sources alter column refresh_enabled set not null;
alter table sources alter column refresh_priority set default 'low';
alter table sources alter column refresh_priority set not null;

update sources
set refresh_enabled = true,
    refresh_window_days = 30,
    refresh_cadence_hours = 168,
    refresh_priority = 'high'
where source_type = 'preprint';

update sources
set refresh_enabled = true,
    refresh_window_days = 30,
    refresh_cadence_hours = 720,
    refresh_priority = 'medium'
where source_type = 'journal';

update sources
set refresh_enabled = true,
    refresh_window_days = 7,
    refresh_cadence_hours = 72,
    refresh_priority = 'medium'
where source_type = 'news';

update sources
set refresh_enabled = false,
    refresh_window_days = null,
    refresh_cadence_hours = null,
    refresh_priority = 'low'
where name = 'BioCentury';

alter table articles add column if not exists last_content_changed_at timestamptz;

update articles
set last_content_changed_at = coalesce(last_content_changed_at, last_analyzed_at, last_scraped_at, created_at)
where last_content_changed_at is null;

create table if not exists source_category_targets (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references sources(id) on delete cascade,
  name text not null,
  url text not null,
  priority text not null default 'medium',
  enabled boolean not null default true,
  check_frequency_hours integer not null default 24,
  last_seen_url text,
  last_seen_published_at timestamptz,
  last_checked_at timestamptz,
  last_error text,
  error_type text,
  detected_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (source_id, url)
);

create index if not exists idx_sources_refresh_enabled on sources(refresh_enabled, refresh_priority);
create index if not exists idx_articles_last_content_changed_at on articles(last_content_changed_at);
create index if not exists idx_source_category_targets_source_enabled on source_category_targets(source_id, enabled, priority);
create index if not exists idx_source_category_targets_last_checked_at on source_category_targets(last_checked_at);

insert into source_category_targets (source_id, name, url, priority, enabled, check_frequency_hours)
select id, 'STAT Biotech', 'https://www.statnews.com/category/biotech/', 'high', true, 24
from sources
where name = 'STAT News'
  and not exists (
    select 1 from source_category_targets where source_id = sources.id and url = 'https://www.statnews.com/category/biotech/'
  );

insert into source_category_targets (source_id, name, url, priority, enabled, check_frequency_hours)
select id, 'BioPharma Dive Pharma', 'https://www.biopharmadive.com/topic/pharma/', 'high', true, 24
from sources
where name = 'BioPharma Dive'
  and not exists (
    select 1 from source_category_targets where source_id = sources.id and url = 'https://www.biopharmadive.com/topic/pharma/'
  );

insert into source_category_targets (source_id, name, url, priority, enabled, check_frequency_hours)
select id, 'Nature Biotechnology Articles', 'https://www.nature.com/nbt/articles', 'high', true, 24
from sources
where name = 'Nature Biotechnology'
  and not exists (
    select 1 from source_category_targets where source_id = sources.id and url = 'https://www.nature.com/nbt/articles'
  );

insert into source_category_targets (source_id, name, url, priority, enabled, check_frequency_hours)
select id, 'arXiv q-bio.BM', 'https://arxiv.org/list/q-bio.BM/new', 'high', true, 24
from sources
where name = 'arXiv Quantitative Biology'
  and not exists (
    select 1 from source_category_targets where source_id = sources.id and url = 'https://arxiv.org/list/q-bio.BM/new'
  );

insert into source_category_targets (source_id, name, url, priority, enabled, check_frequency_hours)
select id, 'bioRxiv Recent', 'https://www.biorxiv.org/content/early/recent', 'high', true, 24
from sources
where name = 'bioRxiv'
  and not exists (
    select 1 from source_category_targets where source_id = sources.id and url = 'https://www.biorxiv.org/content/early/recent'
  );

update source_category_targets
set check_frequency_hours = 12,
    updated_at = now()
where source_id in (select id from sources where name = 'bioRxiv')
  and url = 'https://www.biorxiv.org/content/early/recent';

insert into source_category_targets (source_id, name, url, priority, enabled, check_frequency_hours)
select id, 'Fierce Biotech', 'https://www.fiercebiotech.com/biotech', 'medium', true, 24
from sources
where name = 'Fierce Biotech'
  and not exists (
    select 1 from source_category_targets where source_id = sources.id and url = 'https://www.fiercebiotech.com/biotech'
  );

insert into source_category_targets (source_id, name, url, priority, enabled, check_frequency_hours)
select id, 'GEN News', 'https://www.genengnews.com/news/', 'medium', true, 24
from sources
where name = 'GEN – Genetic Engineering & Biotechnology News'
  and not exists (
    select 1 from source_category_targets where source_id = sources.id and url = 'https://www.genengnews.com/news/'
  );

insert into source_category_targets (source_id, name, url, priority, enabled, check_frequency_hours)
select id, 'Endpoints News', 'https://endpoints.news/news/', 'high', true, 24
from sources
where name = 'Endpoints News'
  and not exists (
    select 1 from source_category_targets where source_id = sources.id and url = 'https://endpoints.news/news/'
  );

insert into source_category_targets (source_id, name, url, priority, enabled, check_frequency_hours)
select id, 'BioCentury Realtime Feed', 'https://www.biocentury.com/analysis/articles', 'medium', true, 24
from sources
where name = 'BioCentury'
  and not exists (
    select 1 from source_category_targets where source_id = sources.id and url = 'https://www.biocentury.com/analysis/articles'
  );

update source_category_targets
set name = 'BioCentury Realtime Feed',
    url = 'https://www.biocentury.com/analysis/articles',
    check_frequency_hours = 24,
    updated_at = now()
where source_id in (select id from sources where name = 'BioCentury')
  and url = 'https://www.biocentury.com/biopharma';

insert into source_category_targets (source_id, name, url, priority, enabled, check_frequency_hours)
select id, 'Science Current TOC', 'https://www.science.org/toc/science/current', 'high', true, 24
from sources
where name = 'Science'
  and not exists (
    select 1 from source_category_targets where source_id = sources.id and url = 'https://www.science.org/toc/science/current'
  );

insert into source_category_targets (source_id, name, url, priority, enabled, check_frequency_hours)
select id, 'SynBioBeta Industry News', 'https://www.synbiobeta.com/synthetic-bio-news', 'high', true, 12
from sources
where name = 'SynBioBeta'
  and not exists (
    select 1 from source_category_targets where source_id = sources.id and url = 'https://www.synbiobeta.com/synthetic-bio-news'
  );

update source_category_targets
set name = 'SynBioBeta Industry News',
    url = 'https://www.synbiobeta.com/synthetic-bio-news',
    priority = 'high',
    check_frequency_hours = 12,
    updated_at = now()
where source_id in (select id from sources where name = 'SynBioBeta')
  and url = 'https://www.synbiobeta.com/read';