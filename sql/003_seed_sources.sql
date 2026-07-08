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

insert into sources (name, url, domain, source_type, enabled, crawl_frequency, extraction_mode)
select 'arXiv Quantitative Biology', 'https://arxiv.org/archive/q-bio', 'biotech', 'preprint', true, 'daily', 'rss_feed'
where not exists (
  select 1 from sources where url = 'https://arxiv.org/archive/q-bio'
);

insert into sources (name, url, domain, source_type, enabled, crawl_frequency, extraction_mode)
select 'bioRxiv', 'https://www.biorxiv.org/', 'biotech', 'preprint', true, 'daily', 'rss_feed'
where not exists (
  select 1 from sources where url = 'https://www.biorxiv.org/'
);

insert into sources (name, url, domain, source_type, enabled, crawl_frequency, extraction_mode)
select 'Fierce Biotech', 'https://www.fiercebiotech.com/', 'biotech', 'news', true, 'daily', 'homepage_links'
where not exists (
  select 1 from sources where url = 'https://www.fiercebiotech.com/'
);

insert into sources (name, url, domain, source_type, enabled, crawl_frequency, extraction_mode)
select 'GEN – Genetic Engineering & Biotechnology News', 'https://www.genengnews.com/', 'biotech', 'news', true, 'daily', 'homepage_links'
where not exists (
  select 1 from sources where url = 'https://www.genengnews.com/'
);

insert into sources (name, url, domain, source_type, enabled, crawl_frequency, extraction_mode)
select 'Endpoints News', 'https://endpoints.news/', 'biotech', 'news', true, 'daily', 'homepage_links'
where not exists (
  select 1 from sources where url = 'https://endpoints.news/'
);

insert into sources (name, url, domain, source_type, enabled, crawl_frequency, extraction_mode)
select 'BioCentury', 'https://www.biocentury.com/', 'biotech', 'news', true, 'daily', 'homepage_links'
where not exists (
  select 1 from sources where url = 'https://www.biocentury.com/'
);

insert into sources (name, url, domain, source_type, enabled, crawl_frequency, extraction_mode)
select 'Science', 'https://www.science.org/', 'biotech', 'journal', true, 'daily', 'rss_feed'
where not exists (
  select 1 from sources where url = 'https://www.science.org/'
);

insert into sources (name, url, domain, source_type, enabled, crawl_frequency, extraction_mode)
select 'SynBioBeta', 'https://www.synbiobeta.com/', 'biotech', 'news', true, 'daily', 'homepage_links'
where not exists (
  select 1 from sources where url = 'https://www.synbiobeta.com/'
);
