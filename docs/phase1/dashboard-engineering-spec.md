# BioMyne Koji Admin Dashboard — Engineering Specification

## Document Status

| Field | Value |
|-------|-------|
| Status | Draft for Engineering Execution |
| Phase | Phase 1 Data Layer + Dashboard MVP |
| Based on | Phase 1 pipeline (operational) + Deep Research Report 2026-07-07 |
| Quality Target | 95+ |
| Last updated | 2026-07-07 |
| Intended reader | Full-stack engineer / AI engineer |
| Research basis | 40+ sources, all high-confidence |

---

## 1. Executive Summary

Phase 1 pipeline is fully operational: `bash ops/scripts/run_pipeline.sh` ingests biotech articles from 10 curated sources, runs LLM analysis, and persists structured results to Supabase. This spec defines the Admin Dashboard that makes that data accessible, manageable, and actionable.

**The dashboard is NOT a Phase 2 feature.** It surfaces Phase 1 data with minimal additional infrastructure — no new backend services, no schema changes, only a typed data access layer (Drizzle ORM) and a Next.js frontend consuming the existing Supabase tables.

**What this spec covers:**
- Drizzle ORM setup and schema aligned to existing Supabase tables
- 7 dashboard pages scoped to Phase 1 data only
- Manual sync trigger with SSE progress streaming
- Cytoscape.js entity relationship visualization
- Zustand stores for UI state
- Dashboard-local runtime configuration: if `DATABASE_URL` is absent, the dashboard uses its own `.env.local` Supabase and pipeline settings while continuing to run in REST mode on the server
- Full implementation order and acceptance criteria

**What this spec explicitly does NOT include:**
- Any Supabase schema changes (tables are frozen from Phase 1)
- Authentication (single-operator Phase 1, add later)
- GraphRAG or Neo4j (deferred per Phase 1 architecture decision)
- Real-time subscription (Phase 2 upgrade candidate)

---

## 2. Problem Statement

Phase 1 intelligence data exists in Supabase but is only accessible via raw SQL console or terminal pipeline output. The operations team has no way to:
- Browse the intelligence feed in a human-readable format
- Monitor pipeline health without querying the database directly
- Manage sources without SQL
- Understand entity relationships across articles
- Trigger a manual pipeline run from a UI

This dashboard closes all five gaps using existing data.

---

## 3. Scope Lock

### 3.1 In Scope

| Page | Purpose | Scope |
|------|---------|-------|
| Overview | KPI cards + today's highlights | Phase 1 data only |
| Intelligence Feed | Article browsing, filtering, detail view | Phase 1 data only |
| Pipeline Monitor | Crawl run history + health charts | Phase 1 data only |
| Sources Manager | CRUD for sources (enable/disable/add/edit) | Drizzle mutations |
| Entity Explorer | Entity list + Cytoscape.js co-occurrence graph | Phase 1 data only |
| Analytics | Trend charts, priority distribution, topic breakdown | Phase 1 data only |
| Settings | Manual sync trigger + SSE progress display | Calls `run_pipeline.sh` |

### 3.2 Out of Scope

- User authentication / multi-tenant RBAC
- Supabase Realtime subscriptions (polling only in Phase 1)
- GraphDB / Neo4j integration
- Article export / report generation
- Notification system (Telegram/Slack from dashboard)
- Automated test suite beyond type safety

---

## 4. Technical Architecture

### 4.1 Tech Stack

| Layer | Technology | Version | Status |
|-------|-----------|---------|--------|
| Framework | Next.js App Router | 16.x | Existing template |
| UI | Shadcn/UI + Tailwind CSS | v4 | Existing template |
| Charts | Recharts | 3.8.x | Existing template |
| Tables | TanStack Table | v8.21 | Existing template |
| State | Zustand | v5 | Existing template |
| Forms/Validation | react-hook-form + Zod | v7 / v4 | Existing template |
| ORM | Drizzle ORM | **0.41.x** (v0.x API — not v1.0) | **New — must install** |
| DB Client | postgres (postgres-js) | 3.x | **New — must install** |
| Entity Viz | Cytoscape.js + react-cytoscapejs | Latest | **New — must install** |
| SSE | Native Next.js ReadableStream | Built-in | No new dep |

### 4.2 Architecture Diagram

```mermaid
flowchart TD
  A[Browser / Admin User] --> B[Next.js App Router]
  B --> C[Server Components / Server Actions]
  B --> D[Route Handlers]
  C --> E[Drizzle ORM]
  D --> E
  E --> F[Supabase Postgres]
  D --> G[SSE Stream]
  G --> A
  D --> H[run_pipeline.sh trigger]
  H --> F
  F --> I[(sources)]
  F --> J[(crawl_runs)]
  F --> K[(articles)]
  F --> L[(entities)]
  F --> M[(article_entities)]
  F --> N[(delivery_logs)]
```

### 4.3 Repository Structure

All dashboard code lives in `BiomyneKoji/biomyne-koji-dashboard/`. This spec only adds to the existing template structure.

```
biomyne-koji-dashboard/
  src/
    lib/
      db/
        client.ts           ← Drizzle client (NEW)
        schema.ts           ← Drizzle schema definitions (NEW)
        relations.ts        ← Drizzle relations (NEW)
        queries/
          articles.ts       ← Article query helpers (NEW)
          crawl-runs.ts     ← Crawl run query helpers (NEW)
          sources.ts        ← Source query helpers (NEW)
          entities.ts       ← Entity query helpers (NEW)
          analytics.ts      ← Aggregation queries (NEW)
    stores/
      sync-store.ts         ← Manual sync Zustand store (NEW)
      feed-filter-store.ts  ← Intelligence Feed filter state (NEW)
    app/(main)/dashboard/
      koji/                 ← All new Koji pages (NEW)
        loading.tsx         ← Shared loading skeleton for Koji routes (NEW)
        error.tsx           ← Shared route error boundary for Koji routes (NEW)
        overview/
          page.tsx
          _components/
        feed/
          page.tsx
          _components/
        pipeline/
          page.tsx
          _components/
        sources/
          page.tsx
          _components/
        entities/
          page.tsx
          _components/
        analytics/
          page.tsx
          _components/
        settings/
          page.tsx
          _components/
    app/api/
      pipeline/
        trigger/
          route.ts          ← POST: start manual run (NEW)
        progress/
          route.ts          ← GET SSE: stream run progress (NEW)
```

---

## 5. Drizzle ORM Setup

### 5.1 Installation

```bash
# ⚠️ Pin to v0.41.x — this spec uses v0.x relations() API (NOT v1.0 defineRelations)
pnpm add drizzle-orm@^0.41 postgres
pnpm add -D drizzle-kit
```

Add to `package.json` scripts:
```json
"db:generate": "drizzle-kit generate",
"db:migrate": "drizzle-kit migrate",
"db:introspect": "drizzle-kit introspect",
"db:studio": "drizzle-kit studio"
```

### 5.2 Environment Variables

Add to `.env.local` (dashboard repo):
```env
# Supabase Transaction Pooler (port 6543) — for Next.js App Router / Serverless
DATABASE_URL=postgres://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

# Supabase anon key for client-side operations (optional Phase 1)
NEXT_PUBLIC_SUPABASE_URL=https://[project-ref].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[anon-key]
SUPABASE_SERVICE_ROLE_KEY=[service-role-key]
PIPELINE_SCRIPT_PATH=/absolute/path/to/biomyne-koji/ops/scripts/run_pipeline.sh
```

**Critical:** Must use Transaction Pooler (port **6543**), not Direct Connection (5432), for Next.js App Router server components.

### 5.3 Drizzle Client

```typescript
// src/lib/db/client.ts
import { drizzle } from 'drizzle-orm/postgres-js'
import postgres from 'postgres'
import * as schema from './schema'

// Transaction pooler: prepare must be false (pgBouncer limitation)
const client = postgres(process.env.DATABASE_URL!, {
  prepare: false,  // ⚠️ Required — Transaction mode doesn't support named prepared statements
  max: 1,          // Serverless: single connection per lambda
})

export const db = drizzle(client, { schema })
export type DB = typeof db
```

### 5.4 Schema Definition

```typescript
// src/lib/db/schema.ts
import {
  pgTable, uuid, text, timestamp, integer, boolean,
  jsonb, real, unique,
} from 'drizzle-orm/pg-core'

// ─── Sources ──────────────────────────────────────────────
export const sources = pgTable('sources', {
  id:              uuid('id').defaultRandom().primaryKey(),
  name:            text('name').notNull(),
  url:             text('url').notNull(),
  domain:          text('domain'),
  sourceType:      text('source_type'),
  enabled:         boolean('enabled').default(true),
  crawlFrequency:  text('crawl_frequency').default('daily'),
  extractionMode:  text('extraction_mode'),
  createdAt:       timestamp('created_at', { withTimezone: true }).defaultNow(),
  updatedAt:       timestamp('updated_at', { withTimezone: true }).defaultNow(),
})

// ─── Crawl Runs ───────────────────────────────────────────
export const crawlRuns = pgTable('crawl_runs', {
  id:           uuid('id').defaultRandom().primaryKey(),
  runType:      text('run_type').notNull(),
  startedAt:    timestamp('started_at', { withTimezone: true }).notNull(),
  completedAt:  timestamp('completed_at', { withTimezone: true }),
  status:       text('status').notNull(), // 'running' | 'completed' | 'partial_success' | 'failed'
  sourceCount:  integer('source_count').default(0),
  articleCount: integer('article_count').default(0),
  errorCount:   integer('error_count').default(0),
  notes:        text('notes'),
})

// ─── Articles ─────────────────────────────────────────────
export const articles = pgTable('articles', {
  id:             uuid('id').defaultRandom().primaryKey(),
  sourceId:       uuid('source_id').references(() => sources.id),
  crawlRunId:     uuid('crawl_run_id').references(() => crawlRuns.id),
  url:            text('url').notNull(),
  title:          text('title'),
  publishedAt:    timestamp('published_at', { withTimezone: true }),
  rawMarkdown:    text('raw_markdown'),
  summary:        text('summary'),
  topicTags:      jsonb('topic_tags').$type<string[]>().default([]),
  priorityLevel:  text('priority_level').notNull(), // 'low' | 'medium' | 'high'
  confidenceScore: real('confidence_score'),
  status:         text('status').notNull(), // 'processed' | 'failed' | 'needs_review'
  analysisNotes:  text('analysis_notes'),
  createdAt:      timestamp('created_at', { withTimezone: true }).defaultNow(),
  updatedAt:      timestamp('updated_at', { withTimezone: true }).defaultNow(),
})

// ─── Entities ─────────────────────────────────────────────
export const entities = pgTable('entities', {
  id:            uuid('id').defaultRandom().primaryKey(),
  name:          text('name').notNull(),
  entityType:    text('entity_type').notNull(), // 'company' | 'researcher' | 'drug' | 'compound' | 'institution' | 'regulator'
  canonicalName: text('canonical_name'),
  createdAt:     timestamp('created_at', { withTimezone: true }).defaultNow(),
  updatedAt:     timestamp('updated_at', { withTimezone: true }).defaultNow(),
}, (t) => [unique().on(t.name, t.entityType)])

// ─── Article Entities (Junction) ──────────────────────────
export const articleEntities = pgTable('article_entities', {
  id:              uuid('id').defaultRandom().primaryKey(),
  articleId:       uuid('article_id').notNull().references(() => articles.id, { onDelete: 'cascade' }),
  entityId:        uuid('entity_id').notNull().references(() => entities.id, { onDelete: 'cascade' }),
  roleInArticle:   text('role_in_article'),
  mentionCount:    integer('mention_count').default(1),
  confidenceScore: real('confidence_score'),
})

// ─── Delivery Logs ────────────────────────────────────────
export const deliveryLogs = pgTable('delivery_logs', {
  id:             uuid('id').defaultRandom().primaryKey(),
  crawlRunId:     uuid('crawl_run_id').notNull().references(() => crawlRuns.id),
  channelType:    text('channel_type').notNull(),
  destination:    text('destination').notNull(),
  deliveredAt:    timestamp('delivered_at', { withTimezone: true }),
  status:         text('status').notNull(),
  messagePreview: text('message_preview'),
})
```

### 5.5 Relations

> **Version note:** `relations` is the correct API for drizzle-orm `^0.41` (v0.x). Do NOT use `defineRelations` — that is a v1.0 API breaking change.

```typescript
// src/lib/db/relations.ts
import { relations } from 'drizzle-orm'  // v0.x API — correct for drizzle-orm ^0.41
import { sources, crawlRuns, articles, entities, articleEntities, deliveryLogs } from './schema'

export const sourcesRelations = relations(sources, ({ many }) => ({
  articles: many(articles),
}))

export const crawlRunsRelations = relations(crawlRuns, ({ many }) => ({
  articles: many(articles),
  deliveryLogs: many(deliveryLogs),
}))

export const articlesRelations = relations(articles, ({ one, many }) => ({
  source: one(sources, { fields: [articles.sourceId], references: [sources.id] }),
  crawlRun: one(crawlRuns, { fields: [articles.crawlRunId], references: [crawlRuns.id] }),
  articleEntities: many(articleEntities),
}))

export const articleEntitiesRelations = relations(articleEntities, ({ one }) => ({
  article: one(articles, { fields: [articleEntities.articleId], references: [articles.id] }),
  entity: one(entities, { fields: [articleEntities.entityId], references: [entities.id] }),
}))

export const entitiesRelations = relations(entities, ({ many }) => ({
  articleEntities: many(articleEntities),
}))

export const deliveryLogsRelations = relations(deliveryLogs, ({ one }) => ({
  crawlRun: one(crawlRuns, { fields: [deliveryLogs.crawlRunId], references: [crawlRuns.id] }),
}))
```

### 5.6 Drizzle Config

```typescript
// drizzle.config.ts (root of dashboard repo)
import { defineConfig } from 'drizzle-kit'

export default defineConfig({
  schema: './src/lib/db/schema.ts',
  out:    './src/lib/db/migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
})
```

**Migration strategy:** BioMyne already has hand-crafted SQL migrations in `biomyne-koji/sql/`. Do NOT run `drizzle-kit push` (it overwrites schema). For Phase 1 dashboard:
1. Run `npx drizzle-kit introspect` once to verify schema alignment
2. Dashboard makes zero schema changes; Drizzle is read-write for `sources` only, read-only for all other tables
3. If future schema changes needed: `npx drizzle-kit generate` → review → `npx drizzle-kit migrate`

---

## 6. Page Specifications

### Page 1: Overview (`/dashboard/koji/overview`)

**Purpose:** Daily intelligence health-check at a glance. Users see system status and today's top signals in under 10 seconds.

**Layout:** F-pattern — KPI rail (top) → Area chart (mid-left) → Recent articles table (mid-right) → Source status list (bottom)

#### KPI Cards (5)

| Card | Metric | Data Source | Update |
|------|--------|-------------|--------|
| Today's Articles | COUNT articles WHERE published_at >= today | `articles` | On load |
| High-Priority | COUNT articles WHERE priority_level = 'high' + today | `articles` | On load |
| M&A / Funding Signals | COUNT articles WHERE topic_tags @> '["M&A"]' OR '["funding"]' | `articles` | On load |
| Active Sources | COUNT sources WHERE enabled = true / total | `sources` | On load |
| Needs Review | COUNT articles WHERE status = 'needs_review' | `articles` | On load |

Each card includes: primary number, delta vs yesterday, trend indicator (↑↓→).

#### Charts

- **Article Ingestion (7 days):** Recharts `<AreaChart>` — x: day, y: article_count, series: processed/failed
- **Priority Split (today):** Recharts `<PieChart>` or 3-segment progress bar — low/medium/high counts

#### Recent Articles Section

- Last 5 high-priority articles (TanStack Table, 5 rows only, no pagination)
- Columns: Source, Title (truncated), Priority badge, Published

#### Last Run Status

- Single `<Card>`: last `crawl_runs` row — status badge, started_at, duration, article_count, error_count

#### Data Queries

```typescript
// src/lib/db/queries/analytics.ts
import { db } from '@/lib/db/client'
import { articles, sources } from '@/lib/db/schema'
import { and, count, eq, gte, lt, sql } from 'drizzle-orm'

export async function getOverviewKPIs() {
  const todayStart = new Date()
  todayStart.setHours(0, 0, 0, 0)
  const yesterdayStart = new Date(todayStart)
  yesterdayStart.setDate(yesterdayStart.getDate() - 1)

  const [today, yesterday, [{ enabledCount }], [{ reviewCount }]] = await Promise.all([
    db.select({
      total: count(),
      high: count(sql`CASE WHEN ${articles.priorityLevel} = 'high' THEN 1 END`),
      mAndA: count(sql`CASE WHEN ${articles.topicTags}::text ILIKE '%M&A%' OR ${articles.topicTags}::text ILIKE '%funding%' THEN 1 END`),
    }).from(articles).where(gte(articles.createdAt, todayStart)),

    db.select({ total: count() }).from(articles)
      .where(and(gte(articles.createdAt, yesterdayStart), lt(articles.createdAt, todayStart))),

    db.select({ enabledCount: count() }).from(sources).where(eq(sources.enabled, true)),

    db.select({ reviewCount: count() }).from(articles).where(eq(articles.status, 'needs_review')),
  ])

  return {
    today: today[0],
    yesterday: yesterday[0],
    activeSources: { enabled: enabledCount },
    needsReview: { count: reviewCount },
  }
}
```

---

### Page 2: Intelligence Feed (`/dashboard/koji/feed`)

**Purpose:** Primary daily workflow — browse, filter, and review all processed articles. This is where most operator time is spent.

**Layout:** Filter Bar (sticky top) → Article Table (TanStack) → Article Detail Modal (Shadcn `<Dialog>`)

#### Filter Bar Components

| Filter | Type | Zustand Key |
|--------|------|-------------|
| Date Range | `date-range-picker.tsx` (existing) | `dateRange` |
| Priority | Multi-select (Shadcn `<Select>`) | `priorities` |
| Source | Multi-select dropdown | `sourceIds` |
| Topic Tag | Text input + badge list | `topicTags` |
| Status | Toggle group (processed / needs_review / failed) | `status` |
| Search | Debounced text input | `searchText` |

All filters stored in `useFeedFilterStore` (Zustand). Filter state applied client-side via TanStack Table `getFilteredRowModel()` for small datasets, server-side for large.

#### Article Table Columns

| Column | Content | Width | Sortable |
|--------|---------|-------|---------|
| Priority | Badge (high=red, medium=amber, low=grey) | 80px | Yes |
| Title | Text, click to open detail modal | Flex | Yes |
| Source | Source name pill | 120px | Yes |
| Topic Tags | Top 2 tags as small badges | 160px | No |
| Published | Relative time (e.g. "2h ago") | 100px | Yes |
| Status | Badge (processed / needs_review / failed) | 100px | Yes |
| Actions | "View" button | 80px | No |

#### Article Detail Modal

Triggered by clicking row or "View" button. Shadcn `<Dialog>` containing:
- Title + Source + Published timestamp
- AI Summary (full text, styled with `<Prose>`)
- Topic tags as colored badges
- Priority level indicator
- Entity list: each entity name + type + mention_count (linked to Entity Explorer)
- "Mark Needs Review" toggle (Server Action updating `articles.status`)
- Link to original URL (new tab)

#### Server Action: Update Article Status

```typescript
// src/app/(main)/dashboard/koji/feed/_actions/update-status.ts
'use server'
import { db } from '@/lib/db/client'
import { articles } from '@/lib/db/schema'
import { eq } from 'drizzle-orm'
import { revalidatePath } from 'next/cache'

export async function updateArticleStatus(
  articleId: string,
  status: 'processed' | 'needs_review'
) {
  await db.update(articles)
    .set({ status, updatedAt: new Date() })
    .where(eq(articles.id, articleId))
  revalidatePath('/dashboard/koji/feed')
}
```

---

### Page 3: Pipeline Monitor (`/dashboard/koji/pipeline`)

**Purpose:** Operator visibility into crawl run health. Modeled on Langfuse's trace list + detail pattern.

**Layout:** Health KPI rail (top) → 7-day success rate chart (mid) → Run History Table (main)

#### Health KPIs (4 cards)

| Card | Metric |
|------|--------|
| Last Run Status | Status badge + timestamp + duration |
| 7-Day Success Rate | COUNT(success) / COUNT(*) × 100 |
| Avg Articles / Run | AVG(article_count) last 7 runs |
| Total Errors (7d) | SUM(error_count) last 7 days |

#### 7-Day Trend Chart

Recharts `<AreaChart>`:
- X: date (last 7 days)
- Y1: article_count (stacked area, blue)
- Y2: error_count (stacked area, red)

#### Run History Table

TanStack Table, 20 rows, paginated.

Columns: Run ID (truncated), Type (scheduled/manual), Started At, Duration, Status badge, Sources, Articles, Errors, Detail action.

Clicking a row expands inline (or opens Sheet) showing `notes` text.

Red row highlight if `status = 'failed'`, amber if `status = 'partial_success'`.

#### Data Query

```typescript
// src/lib/db/queries/crawl-runs.ts
import { db } from '@/lib/db/client'
import { crawlRuns } from '@/lib/db/schema'
import { asc, desc, gte } from 'drizzle-orm'
import { subDays } from 'date-fns'  // already in stack

export async function getRecentCrawlRuns(limit = 20, offset = 0) {
  return db.select().from(crawlRuns)
    .orderBy(desc(crawlRuns.startedAt))
    .limit(limit)
    .offset(offset)
}

export async function getPipelineHealthKPIs() {
  const sevenDaysAgo = subDays(new Date(), 7)
  return db.select({
    status:       crawlRuns.status,
    articleCount: crawlRuns.articleCount,
    errorCount:   crawlRuns.errorCount,
    startedAt:    crawlRuns.startedAt,
    completedAt:  crawlRuns.completedAt,
  }).from(crawlRuns)
    .where(gte(crawlRuns.startedAt, sevenDaysAgo))
    .orderBy(asc(crawlRuns.startedAt))
}
```

---

### Page 4: Sources Manager (`/dashboard/koji/sources`)

**Purpose:** Full CRUD interface for `sources` table — the primary operator control plane for what gets ingested.

**Layout:** Header with "Add Source" button → Sources Table (TanStack, inline editable)

#### Sources Table Columns

| Column | Content | Editable |
|--------|---------|---------|
| Enabled | Shadcn `<Switch>` toggle (optimistic update) | Yes |
| Name | Text | Yes (inline) |
| URL | Link (truncated) | Yes (inline) |
| Domain | Text badge | Yes |
| Type | Select (news/blog/journal/company) | Yes |
| Frequency | Select (daily/weekly) | Yes |
| Extraction Mode | Text | Yes |
| Actions | Edit / Delete buttons | — |

#### CRUD Operations

All implemented as Server Actions:

**Toggle Enable:**
```typescript
'use server'
export async function toggleSourceEnabled(id: string, enabled: boolean) {
  await db.update(sources).set({ enabled, updatedAt: new Date() }).where(eq(sources.id, id))
  revalidatePath('/dashboard/koji/sources')
}
```

**Add Source (Dialog form):**
- Shadcn `<Dialog>` with react-hook-form + Zod validation
- Fields: name, url, domain, source_type, crawl_frequency, extraction_mode, enabled
- Validation: URL must be unique, all required fields present
- On submit: Server Action → `db.insert(sources).values(...)` → `revalidatePath`

**Edit Source (same Dialog, pre-filled):**
- Server Action → `db.update(sources).set({...}).where(eq(sources.id, id))`

**Delete Source (with confirmation):**
- Shadcn `<AlertDialog>` for confirmation
- Server Action → `db.delete(sources).where(eq(sources.id, id))`
- Guard: refuse if source has articles (foreign key protection)

#### Zod Schema for Source Form

```typescript
// src/lib/db/queries/sources.ts
export const SourceFormSchema = z.object({
  name:           z.string().min(1, 'Name required').max(100),
  url:            z.url('Must be a valid URL'),
  domain:         z.string().min(1, 'Domain required'),
  sourceType:     z.enum(['news', 'blog', 'journal', 'company', 'preprint']),
  crawlFrequency: z.enum(['daily', 'weekly']).default('daily'),
  extractionMode: z.string().optional(),
  enabled:        z.boolean().default(true),
})
```

---

### Page 5: Entity Explorer (`/dashboard/koji/entities`)

**Purpose:** Understand the entity landscape extracted from articles. Two views: List and Network Graph.

**Layout:** View toggle (List / Graph) at top → either Entity List Table OR Cytoscape.js network → Right-side Entity Detail Panel (slides in on selection)

#### View 1: Entity List Table

TanStack Table columns: Name, Type (color-coded badge), Mention Count (across all articles), Canonical Name, First Seen, Actions.

Default sort: mention_count DESC.

Filters: Entity Type multi-select, Name search.

Clicking a row → populates Entity Detail Panel on the right.

#### View 2: Entity Network Graph (Cytoscape.js)

**Installation:**
```bash
pnpm add cytoscape react-cytoscapejs cytoscape-cola
pnpm add -D @types/cytoscape
```

**Graph Data Construction (server-side):**

Entities are co-occurrence linked when two entities appear in the same article. Edge weight = number of shared articles.

```typescript
// src/lib/db/queries/entities.ts
export async function getEntityGraphData() {
  // Get all article-entity pairs
  const pairs = await db.select({
    articleId: articleEntities.articleId,
    entityId:  articleEntities.entityId,
    entityName: entities.name,
    entityType: entities.entityType,
    mentionCount: articleEntities.mentionCount,
  }).from(articleEntities)
    .innerJoin(entities, eq(articleEntities.entityId, entities.id))

  // Build co-occurrence edges in memory
  const articleToEntities = new Map<string, typeof pairs>()
  for (const pair of pairs) {
    const existing = articleToEntities.get(pair.articleId) ?? []
    articleToEntities.set(pair.articleId, [...existing, pair])
  }

  const edgeWeights = new Map<string, number>()
  for (const entities of articleToEntities.values()) {
    for (let i = 0; i < entities.length; i++) {
      for (let j = i + 1; j < entities.length; j++) {
        const key = [entities[i].entityId, entities[j].entityId].sort().join('|')
        edgeWeights.set(key, (edgeWeights.get(key) ?? 0) + 1)
      }
    }
  }

  // Aggregate node mention counts
  const nodeMentions = new Map<string, { name: string; type: string; count: number }>()
  for (const pair of pairs) {
    const existing = nodeMentions.get(pair.entityId)
    nodeMentions.set(pair.entityId, {
      name: pair.entityName,
      type: pair.entityType,
      count: (existing?.count ?? 0) + pair.mentionCount,
    })
  }

  return {
    nodes: Array.from(nodeMentions.entries()).map(([id, data]) => ({
      id, label: data.name, type: data.type, weight: data.count,
    })),
    edges: Array.from(edgeWeights.entries()).map(([key, weight]) => {
      const [source, target] = key.split('|')
      return { source, target, weight }
    }),
  }
}
```

**EntityGraph Component:**

```typescript
// src/app/(main)/dashboard/koji/entities/_components/EntityGraph.tsx
'use client'
import dynamic from 'next/dynamic'

// Cytoscape must be dynamically imported (no SSR)
const CytoscapeComponent = dynamic(
  () => import('react-cytoscapejs').then(m => m.default),
  { ssr: false, loading: () => <Skeleton className="h-[500px] w-full rounded-lg" /> }
)

const NODE_COLORS: Record<string, string> = {
  company:     '#3b82f6',  // blue
  drug:        '#10b981',  // green
  researcher:  '#f59e0b',  // amber
  compound:    '#8b5cf6',  // purple
  institution: '#ec4899',  // pink
  regulator:   '#ef4444',  // red
}

export function EntityGraph({ nodes, edges, onEntityClick, filterType }: EntityGraphProps) {
  const [activeFilter, setActiveFilter] = useState<string | null>(filterType ?? null)

  const visibleNodeIds = useMemo(() => {
    const filtered = !activeFilter ? nodes : nodes.filter(n => n.type === activeFilter)
    return new Set(filtered.map(n => n.id))
  }, [nodes, activeFilter])

  const elements = useMemo(() => [
    ...nodes
      .filter(n => visibleNodeIds.has(n.id))
      .map(n => ({
        data: { id: n.id, label: n.label, type: n.type, weight: n.weight }
      })),
    ...edges
      .filter(e => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target))
      .map(e => ({
        data: { source: e.source, target: e.target, weight: Math.min(e.weight * 2, 10) }
      })),
  ], [nodes, edges, visibleNodeIds])

  const stylesheet = useMemo(() => [
    {
      selector: 'node',
      style: {
        'background-color': (ele: cytoscape.NodeSingular) =>
          NODE_COLORS[ele.data('type') as string] ?? '#94a3b8',
        'width': (ele: cytoscape.NodeSingular) => Math.max(20, Math.min(ele.data('weight') * 3, 60)),
        'height': (ele: cytoscape.NodeSingular) => Math.max(20, Math.min(ele.data('weight') * 3, 60)),
        'label': 'data(label)',
        'font-size': 11,
        'text-wrap': 'wrap',
        'text-max-width': 80,
        'text-valign': 'bottom',
        'text-halign': 'center',
        'color': '#1e293b',
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 'data(weight)',
        'line-color': '#cbd5e1',
        'opacity': 0.5,
        'curve-style': 'bezier',
      }
    },
    {
      selector: ':selected',
      style: { 'border-width': 3, 'border-color': '#1d4ed8' }
    },
    {
      selector: 'node.faded, edge.faded',
      style: { 'opacity': 0.15 }
    },
  ], [])

  return (
    <div className="relative h-[550px] w-full overflow-hidden rounded-lg border bg-muted/20">
      {/* Entity Type Filter */}
      <div className="absolute top-3 left-3 z-10 flex gap-1.5 flex-wrap">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <button
            key={type}
            onClick={() => setActiveFilter(prev => prev === type ? null : type)}
            className="flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium border"
            style={{ borderColor: color, color, backgroundColor: `${color}15` }}
          >
            {type}
          </button>
        ))}
      </div>

      <CytoscapeComponent
        elements={elements}
        style={{ width: '100%', height: '100%' }}
        stylesheet={stylesheet}
        layout={{
          name: 'cola',
          animate: true,
          maxSimulationTime: 2000,
          nodeSpacing: 30,
        } as cytoscape.LayoutOptions}
        cy={(cy) => {
          cy.on('tap', 'node', (evt) => {
            const nodeId = evt.target.data('id') as string
            onEntityClick?.(nodeId)
            // Dim non-neighbors
            cy.elements().addClass('faded')
            evt.target.closedNeighborhood().removeClass('faded')
          })
          cy.on('tap', (evt) => {
            if (evt.target === cy) {
              cy.elements().removeClass('faded')
              onEntityClick?.(null)
            }
          })
        }}
      />
    </div>
  )
}
```

#### Entity Detail Panel (right side sheet)

Shadcn `<Sheet>` sliding from right on entity click:
- Entity name + type badge + canonical name
- Total mention count
- Entity type description
- Related articles list (last 10, sorted by mention_count DESC)
  - Each: title, source, published date, priority badge
  - Clicking article → opens article modal

---

### Page 6: Analytics (`/dashboard/koji/analytics`)

**Purpose:** Trend visualization for intelligence quality and coverage. Business intelligence layer on top of Phase 1 data.

**Layout:** Date Range Picker (sticky header) → Chart Grid (2-column)

All charts respond to the global date range filter.

#### Chart 1: Article Ingestion Over Time (Area Chart)

```
X: date (day)
Y: article count
Series: processed (blue), failed (red), needs_review (amber)
Component: Recharts <AreaChart> with <Tooltip> and <Legend>
```

Data: `SELECT date_trunc('day', created_at), status, COUNT(*) FROM articles GROUP BY 1, 2`

#### Chart 2: Priority Distribution (Stacked Bar Chart)

```
X: date (last 7 or 30 days)
Y: count
Series: high (red), medium (amber), low (grey)
Component: Recharts <BarChart> stacked
```

#### Chart 3: Top Mentioned Companies (Horizontal Bar)

```
X: mention count
Y: entity name (top 10 companies)
Component: Recharts <BarChart layout="vertical">
Click bar → navigate to Entity Explorer filtered to that entity
```

Data: `SELECT entities.name, SUM(mention_count) FROM article_entities JOIN entities ON ... WHERE entity_type = 'company' GROUP BY 1 ORDER BY 2 DESC LIMIT 10`

#### Chart 4: Topic Tag Frequency (Treemap)

```
Data: flatten all topic_tags jsonb arrays, count frequency per tag
Component: Recharts <Treemap>
Cell size proportional to count
```

Server-side aggregation needed (jsonb_array_elements):
```sql
SELECT tag::text, COUNT(*) as count
FROM articles, jsonb_array_elements_text(topic_tags) AS tag
GROUP BY 1
ORDER BY 2 DESC
LIMIT 30
```

#### Chart 5: Confidence Score Distribution (Histogram)

```
X: score bucket (0.0-0.2, 0.2-0.4, ..., 0.8-1.0)
Y: article count
Component: Recharts <BarChart>
```

#### Chart 6: Source Coverage per Run (Heatmap-style)

Simple grid: sources as rows, last 14 runs as columns, cell = ✅ success / ⚠️ partial / ❌ failed.
Data joins `crawl_runs` and `articles` grouped by source.

---

### Page 7: Settings (`/dashboard/koji/settings`)

**Purpose:** Manual pipeline trigger + system configuration.

**Layout:** Two-section cards — "Pipeline Control" + "Source Manifest"

#### Section 1: Pipeline Control

```
┌───────────────────────────────────────────────────────┐
│  Manual Intelligence Sync                              │
│  ─────────────────────────────────────────────────── │
│  Last run: 2026-07-07 14:32 · Success · 42 articles   │
│                                                        │
│  [▶ Start Sync Now]  (disabled while running)          │
│                                                        │
│  ● Syncing...                                          │
│  ━━━━━━━━━━░░░░░░░░  45%                              │
│  12 articles analyzed · 0 errors                       │
│                                                        │
└───────────────────────────────────────────────────────┘
```

#### Section 2: System Information

Read-only display:
- Total articles in database
- Total entities
- Active sources count / total
- Supabase project URL (masked)
- Last delivery log entry

---

## 7. Manual Sync Architecture

### 7.1 API Route: Trigger

> **Security note:** `PIPELINE_SCRIPT_PATH` must be a pre-validated absolute path. The route does NOT accept the path from the request body (OWASP command injection prevention).
>
> **Next.js 16 note:** Fire-and-forget operations MUST use `after()` from `'next/server'`. Without it, the runtime can be torn down before the async work completes in serverless environments.

```typescript
// src/app/api/pipeline/trigger/route.ts
import { NextResponse } from 'next/server'
import { after } from 'next/server'  // ← Required for deferred work in Next.js 15+
import { exec } from 'node:child_process'
import { promisify } from 'node:util'
import path from 'node:path'
import { db } from '@/lib/db/client'
import { crawlRuns } from '@/lib/db/schema'
import { eq } from 'drizzle-orm'

const execAsync = promisify(exec)

// Validate and resolve script path at startup — not at request time
const SCRIPT_PATH = process.env.PIPELINE_SCRIPT_PATH
if (!SCRIPT_PATH) {
  console.error('[pipeline] PIPELINE_SCRIPT_PATH is not set — manual sync will be disabled')
}

export async function POST() {
  if (!SCRIPT_PATH) {
    return NextResponse.json(
      { error: 'Pipeline script path not configured on server' },
      { status: 503 }
    )
  }

  // 1. Check for active run (duplicate prevention via DB state lock)
  const active = await db.select({ id: crawlRuns.id })
    .from(crawlRuns)
    .where(eq(crawlRuns.status, 'running'))
    .limit(1)

  if (active.length > 0) {
    return NextResponse.json(
      { error: 'Pipeline already running', runId: active[0].id },
      { status: 409 }
    )
  }

  // 2. Use after() to defer execution until after response is sent
  // This keeps the deferred work alive even if the runtime would otherwise shut down
  after(
    execAsync(`bash ${path.resolve(SCRIPT_PATH)}`)
      .then(() => console.log('[pipeline] manual run completed'))
      .catch((err: Error) => console.error('[pipeline] manual run failed:', err.message))
  )

  // 3. Return immediately — client subscribes to progress via SSE
  return NextResponse.json({ status: 'triggered' })
}
```

**Environment variable required:**
```env
PIPELINE_SCRIPT_PATH=/absolute/path/to/biomyne-koji/ops/scripts/run_pipeline.sh
```

### 7.2 API Route: SSE Progress Stream

```typescript
// src/app/api/pipeline/progress/route.ts
import { db } from '@/lib/db/client'
import { crawlRuns } from '@/lib/db/schema'
import { desc, eq } from 'drizzle-orm'

const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))

export async function GET() {
  const encoder = new TextEncoder()
  let aborted = false

  const stream = new ReadableStream({
    async start(controller) {
      const send = (data: object) => {
        if (!aborted) controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`))
      }

      // Keep-alive ping every 20s (prevents proxy timeout)
      const keepAlive = setInterval(() => {
        if (!aborted) controller.enqueue(encoder.encode(': ping\n\n'))
      }, 20_000)

      // Poll latest crawl_run every 2 seconds
      let maxPolls = 300 // 10 minute max
      while (!aborted && maxPolls-- > 0) {
        const [latest] = await db.select()
          .from(crawlRuns)
          .orderBy(desc(crawlRuns.startedAt))
          .limit(1)

        send({
          status:       latest?.status ?? 'unknown',
          articleCount: latest?.articleCount ?? 0,
          errorCount:   latest?.errorCount ?? 0,
          startedAt:    latest?.startedAt,
        })

        if (latest?.status && latest.status !== 'running') {
          clearInterval(keepAlive)
          controller.close()
          return
        }
        await sleep(2000)
      }

      clearInterval(keepAlive)
      controller.close()
    },
    cancel() { aborted = true },
  })

  return new Response(stream, {
    headers: {
      'Content-Type':  'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection':    'keep-alive',
      'X-Accel-Buffering': 'no',  // Nginx buffering disable
    },
  })
}
```

### 7.3 Zustand Sync Store

```typescript
// src/stores/sync-store.ts
import { create } from 'zustand'

interface SyncState {
  status: 'idle' | 'running' | 'completed' | 'partial_success' | 'failed'
  articleCount: number
  errorCount: number
  startedAt: Date | null
  triggerSync: () => Promise<void>
  stopListening: () => void
  _evtSource: EventSource | null
}

export const useSyncStore = create<SyncState>((set, get) => ({
  status: 'idle',
  articleCount: 0,
  errorCount: 0,
  startedAt: null,
  _evtSource: null,

  triggerSync: async () => {
    const res = await fetch('/api/pipeline/trigger', { method: 'POST' })

### 7.4 Active Run Hydration Rule

The Settings page must also handle the case where an operator opens the dashboard while a manual run is already in progress.

Required behavior:

- if the latest `crawl_runs` row is already `in_progress` or `running`, the client sync store must auto-hydrate into live tracking mode on page load
- the `Start Sync Now` button must be disabled while that active run is being tracked
- SSE progress tracking should resume from the active run instead of falsely showing `idle`

This behavior was validated during the 2026-07-08 hardening pass.

### 7.5 Dashboard-Local Environment Rule

The current recommended runtime setup is no longer sibling env autodetection.

Required behavior:

- dashboard secrets live in `biomyne-koji-dashboard/.env.local`
- `env.server.ts` reads from `process.env` only
- same-machine deployment is preserved through `PIPELINE_SCRIPT_PATH`, not by reading the pipeline repo's env file at runtime

This change eliminated the previous Turbopack NFT warning tied to sibling env/script tracing.

    if (res.status === 409) {
      // Already running — just subscribe to progress
      set({ status: 'running' })
    } else if (!res.ok) {
      const err = await res.json()
      throw new Error(err.error ?? 'Trigger failed')
    } else {
      set({ status: 'running', articleCount: 0, errorCount: 0, startedAt: new Date() })
    }

    // Subscribe to SSE progress
    const evtSource = new EventSource('/api/pipeline/progress')
    set({ _evtSource: evtSource })

    evtSource.onmessage = (e) => {
      const data = JSON.parse(e.data)
      set({
        status:       data.status,
        articleCount: data.articleCount,
        errorCount:   data.errorCount,
        startedAt:    data.startedAt ? new Date(data.startedAt) : get().startedAt,
      })
      if (data.status !== 'running') {
        evtSource.close()
        set({ _evtSource: null })
      }
    }
    evtSource.onerror = () => {
      set({ status: 'failed' })
      evtSource.close()
      set({ _evtSource: null })
    }
  },

  stopListening: () => {
    get()._evtSource?.close()
    set({ _evtSource: null })
  },
}))
```

---

## 8. Feed Filter Zustand Store

```typescript
// src/stores/feed-filter-store.ts
import { create } from 'zustand'
import { subDays } from 'date-fns'

interface DateRange { from: Date; to: Date }

interface FeedFilterState {
  dateRange: DateRange
  priorities: Array<'low' | 'medium' | 'high'>
  sourceIds: string[]
  topicTags: string[]
  statuses: Array<'processed' | 'needs_review' | 'failed'>
  searchText: string
  setDateRange: (range: DateRange) => void
  togglePriority: (p: 'low' | 'medium' | 'high') => void
  toggleSource: (id: string) => void
  setSearchText: (text: string) => void
  reset: () => void
}

const DEFAULT_FILTERS = {
  dateRange: { from: subDays(new Date(), 7), to: new Date() },
  priorities: ['low', 'medium', 'high'] as const,
  sourceIds: [],
  topicTags: [],
  statuses: ['processed', 'needs_review', 'failed'] as const,
  searchText: '',
}

export const useFeedFilterStore = create<FeedFilterState>((set) => ({
  ...DEFAULT_FILTERS,
  setDateRange: (range) => set({ dateRange: range }),
  togglePriority: (p) => set((s) => ({
    priorities: s.priorities.includes(p)
      ? s.priorities.filter(x => x !== p)
      : [...s.priorities, p],
  })),
  toggleSource: (id) => set((s) => ({
    sourceIds: s.sourceIds.includes(id)
      ? s.sourceIds.filter(x => x !== id)
      : [...s.sourceIds, id],
  })),
  setSearchText: (searchText) => set({ searchText }),
  reset: () => set(DEFAULT_FILTERS),
}))
```

---

## 9. Navigation Updates

Update `src/navigation/sidebar/sidebar-items.ts` to replace generic template items with Koji-specific navigation:

```typescript
// Add this group to sidebarItems:
{
  id: 99,
  label: 'Koji Intelligence',
  items: [
    { id: 'koji-overview',  title: 'Overview',     url: '/dashboard/koji/overview',  icon: Gauge },
    { id: 'koji-feed',      title: 'Intel Feed',   url: '/dashboard/koji/feed',      icon: Newspaper },
    { id: 'koji-pipeline',  title: 'Pipeline',     url: '/dashboard/koji/pipeline',  icon: Activity },
    { id: 'koji-sources',   title: 'Sources',      url: '/dashboard/koji/sources',   icon: Database },
    { id: 'koji-entities',  title: 'Entities',     url: '/dashboard/koji/entities',  icon: Network },
    { id: 'koji-analytics', title: 'Analytics',    url: '/dashboard/koji/analytics', icon: ChartBar },
    { id: 'koji-settings',  title: 'Settings',     url: '/dashboard/koji/settings',  icon: Settings },
  ],
}
```

App name update in `src/config/app-config.ts`:
```typescript
name: "Koji Intelligence"
```

---

## 10. Implementation Order

Follow this order strictly. Do not jump to Phase 3 before Phase 1 is passing smoke tests.

### Phase 1 — Foundation (Days 1-2)

1. Install `drizzle-orm`, `postgres`, `drizzle-kit`
2. Create `lib/db/client.ts`, `lib/db/schema.ts`, `lib/db/relations.ts`
3. Run `npx drizzle-kit introspect` — verify schema matches Supabase exactly
4. Create one test query (e.g., fetch 5 sources) and verify it returns real data
5. Set up `drizzle.config.ts`
6. Create `src/app/(main)/dashboard/koji/` folder structure

### Phase 2 — Read Layer (Days 3-4)

7. Build Overview page with KPI cards (no charts yet, just numbers)
8. Build Sources Manager (list only, no CRUD yet)
9. Build Pipeline Monitor (run history table only)
10. Verify all three pages load without error with real Supabase data

### Phase 3 — Intelligence Feed (Days 5-6)

11. Build Intelligence Feed table with TanStack Table
12. Add Filter Bar with `useFeedFilterStore`
13. Build Article Detail Modal
14. Add "Mark Needs Review" Server Action

### Phase 4 — Analytics + Overview Charts (Days 7-8)

15. Add Recharts to Overview (Area chart + Pie)
16. Build Analytics page: Priority Distribution, Ingestion Over Time, Top Companies
17. Add Topic Treemap chart

### Phase 5 — Entity Explorer (Days 9-10)

18. Install `cytoscape`, `react-cytoscapejs`, `cytoscape-cola`
19. Build Entity List table
20. Build EntityGraph component with dynamic import (no SSR)
21. Build Entity Detail Panel (Shadcn Sheet)

### Phase 6 — Sources CRUD + Settings (Days 11-12)

22. Add Source form (Dialog + react-hook-form + Zod)
23. Implement all Server Actions for Sources CRUD
24. Build Settings page
25. Implement API routes: `POST /api/pipeline/trigger`, `GET /api/pipeline/progress`
26. Build `useSyncStore` and connect to Settings UI

### Phase 7 — Polish (Days 13-14)

27. Update `sidebar-items.ts` with Koji navigation
28. Update `app-config.ts` branding
29. Add loading skeletons to all pages (Shadcn `<Skeleton>`)
30. Add error boundaries
31. Verify mobile responsiveness

---

## 11. Acceptance Criteria

### Functional

- [ ] All 7 pages load without error against real Supabase data
- [ ] Intelligence Feed shows all processed articles, filterable by priority/date/source
- [ ] Article detail modal shows full summary + entities
- [ ] "Mark Needs Review" updates article status (confirm in Supabase)
- [ ] Sources CRUD: add, edit, toggle enable, delete all work end-to-end
- [ ] Delete is blocked if source has associated articles (FK guard)
- [ ] Entity Graph renders with nodes and edges from real `article_entities` data
- [ ] Clicking a node in the graph opens the Entity Detail Panel
- [ ] Settings "Start Sync" triggers pipeline run (confirm new `crawl_runs` row in Supabase)
- [ ] SSE progress shows updating article count while pipeline runs
- [ ] Concurrent sync trigger returns 409 and subscribes to existing run
- [ ] If Settings opens during an active run, the page auto-hydrates into live tracking mode instead of showing `idle`

### Data Integrity

- [ ] No article duplication from repeated page loads
- [ ] All DB writes use `updatedAt: new Date()` where applicable
- [ ] Server Actions call `revalidatePath` after mutations

### Performance

- [ ] Overview page loads KPIs in under 1 second (parallel Promise.all queries)
- [ ] Intelligence Feed renders 50+ rows without lag
- [ ] Entity Graph renders up to 200 nodes without freezing
- [ ] No N+1 queries in any page load

### UX

- [ ] All loading states have Skeleton placeholders
- [ ] Error states show meaningful messages (not raw JS errors)
- [ ] Mobile breakpoints: all pages usable on iPad-width (768px+)

### Validation Note — 2026-07-08 Hardening Pass

The implementation has already passed these post-build checks:

- shared Koji route `loading.tsx` and `error.tsx` are present
- `npm run build` passes after hardening changes
- Settings page manual sync was validated end-to-end from dashboard UI to Supabase persistence
- active-run hydration was validated: an existing `in_progress` crawl run correctly bootstrapped the client into `Live` tracking mode and disabled duplicate triggering
- the previous Turbopack NFT warning was eliminated by moving runtime secrets into dashboard-local `.env.local`

---

## 12. Open Questions (Require Owner Decision Before Phase 5)

| Question | Default Recommendation | Owner |
|----------|----------------------|-------|
| Is Supabase Realtime enabled? If yes, can replace SSE polling with Realtime subscription | Phase 1 shipped with SSE polling; Realtime remains an optional upgrade | Engineering owner |
| What is `PIPELINE_SCRIPT_PATH` in dashboard deployment environment? | Same-machine Mac Studio deployment may auto-detect sibling `../biomyne-koji/ops/scripts/run_pipeline.sh` | Engineering owner |
| Should the dashboard be deployed to Vercel or same Mac Studio as pipeline? | **Answered:** Mac Studio localhost, same host as pipeline | Engineering/Ops owner |
| Should `raw_markdown` column be displayed in article detail, or only `summary`? | **Answered:** show `raw_markdown` first, with summary as a secondary tab | Product owner |

---

## 13. Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Cytoscape.js SSR error (window undefined) | Use `dynamic(() => import(...), { ssr: false })` |
| Transaction Pooler `prepare: false` forgotten | Include in client.ts with comment; add to PR checklist |
| `run_pipeline.sh` path differs in deployment | Require `PIPELINE_SCRIPT_PATH` env var, fail fast if missing |
| Entity graph too slow with many nodes | Start with 200-node limit; add count guard before rendering |
| Sources delete with FK children | Handle DB FK constraint error in Server Action, show user-friendly message |
| JSONB `topic_tags` query performance | Add GIN index on `topic_tags` if tag filtering is slow (minor Supabase console task) |

---

## 14. Definition of Done

Phase 1 Dashboard is done when ALL items are true:

- [ ] Drizzle ORM connects to Supabase and all 6 tables are queryable
- [ ] All 7 pages are accessible from sidebar navigation
- [ ] Intelligence Feed shows real articles with filters working
- [ ] Sources CRUD is fully functional
- [ ] Entity Explorer network graph renders real co-occurrence data
- [ ] Manual sync works end-to-end with SSE progress display
- [ ] Analytics charts show meaningful trends from real data
- [ ] No console errors on any page
- [ ] Loading skeletons prevent CLS on all pages
- [ ] Engineering owner has tested on actual Supabase data for ≥ 1 day of pipeline runs

Current implementation status as of 2026-07-08:

- route-level loading skeletons: implemented
- route-level error boundary: implemented
- UI-triggered manual sync: validated through a successful `crawl_runs` row (`932da5bb-2645-49a9-90e0-ec712451726d`) with `status=success`, `article_count=6`, `error_count=0`
- runtime warning status: cleared after moving to dashboard-local env configuration
