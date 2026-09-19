# P2 Step 1 — sql/006 Apply 指引

**狀態**：REST API 已確認可達（Supabase 已重新激活，`column sources.crawler_provider does not exist` 證實 migration 未 apply）

## 背景
- `supabase` CLI 帳號（`xpdqudvtjmuzadfouebc` org）**無權限**存取 `yihgpsbofjgoxbfypnia` project（回 `Your account does not have the necessary privileges`）
- `.env` 無 `DATABASE_URL`（只有 REST 用的 `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`）
- 需用正確的 org 帳號或 DB 連線字串執行 DDL

## 方法 A：Supabase Dashboard SQL Editor（最快）
1. 登入 supabase.com/dashboard → 選 project `yihgpsbofjgoxbfypnia`
2. 左側 **SQL Editor** → New query
3. 貼上 `sql/006_crawl4ai_migration.sql` 內容：
```sql
alter table sources add column if not exists crawler_provider text not null default 'local';

update sources set crawler_provider = 'firecrawl_cloud'
where name in ('Endpoints News', 'BioCentury', 'Science');
```
4. Run → 應回 `ALTER TABLE` + `UPDATE 3`

## 方法 B：提供 DATABASE_URL 給我執行
若你給我 `DATABASE_URL`（`postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres` 格式，**不要貼在對話** — 加到 `.env` 或 `/tmp/dburl.txt` 後告訴我路徑），我用 psql 執行。

## 驗證（apply 後）
```bash
curl -s "$SUPABASE_URL/rest/v1/sources?select=name,crawler_provider" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
# 期望：11 個 source，其中 Endpoints News/BioCentury/Science = firecrawl_cloud，其餘 local
```
