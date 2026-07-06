insert into sources (name, url, domain, source_type, enabled, crawl_frequency, extraction_mode)
select 'STAT News', 'https://www.statnews.com/', 'biotech', 'news', true, 'daily', 'homepage_links'
where not exists (
  select 1 from sources where url = 'https://www.statnews.com/'
);

insert into sources (name, url, domain, source_type, enabled, crawl_frequency, extraction_mode)
select 'BioPharma Dive', 'https://www.biopharmadive.com/', 'biotech', 'news', true, 'daily', 'homepage_links'
where not exists (
  select 1 from sources where url = 'https://www.biopharmadive.com/'
);

insert into sources (name, url, domain, source_type, enabled, crawl_frequency, extraction_mode)
select 'Nature Biotechnology', 'https://www.nature.com/nbt/', 'biotech', 'journal', true, 'daily', 'article_listing'
where not exists (
  select 1 from sources where url = 'https://www.nature.com/nbt/'
);
