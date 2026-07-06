create index if not exists idx_articles_source_id on articles(source_id);
create index if not exists idx_articles_crawl_run_id on articles(crawl_run_id);
create index if not exists idx_articles_priority_level on articles(priority_level);
create index if not exists idx_articles_published_at on articles(published_at);
create index if not exists idx_article_entities_article_id on article_entities(article_id);
create index if not exists idx_article_entities_entity_id on article_entities(entity_id);
create index if not exists idx_sources_enabled on sources(enabled);
