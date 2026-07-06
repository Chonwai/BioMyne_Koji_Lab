create extension if not exists pgcrypto;

create table if not exists sources (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  url text not null unique,
  domain text not null,
  source_type text not null,
  enabled boolean not null default true,
  crawl_frequency text not null default 'daily',
  extraction_mode text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists crawl_runs (
  id uuid primary key default gen_random_uuid(),
  run_type text not null,
  started_at timestamptz not null,
  completed_at timestamptz,
  status text not null,
  source_count integer not null default 0,
  article_count integer not null default 0,
  error_count integer not null default 0,
  notes text
);

create table if not exists articles (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references sources(id),
  crawl_run_id uuid not null references crawl_runs(id),
  url text not null unique,
  title text,
  published_at timestamptz,
  raw_markdown text,
  summary text,
  topic_tags jsonb not null default '[]'::jsonb,
  priority_level text not null,
  confidence_score numeric(4,3),
  status text not null,
  analysis_notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists entities (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  entity_type text not null,
  canonical_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (name, entity_type)
);

create table if not exists article_entities (
  id uuid primary key default gen_random_uuid(),
  article_id uuid not null references articles(id) on delete cascade,
  entity_id uuid not null references entities(id) on delete cascade,
  role_in_article text,
  mention_count integer not null default 1,
  confidence_score numeric(4,3)
);

create table if not exists delivery_logs (
  id uuid primary key default gen_random_uuid(),
  crawl_run_id uuid not null references crawl_runs(id),
  channel_type text not null,
  destination text not null,
  delivered_at timestamptz,
  status text not null,
  message_preview text
);
