-- AI Registry — Supabase schema
-- Run this in the Supabase SQL editor for the dedicated AI Registry project.

-- ── Registry entries ──────────────────────────────────────────────────────
create table if not exists registry_entries (
    id                  text primary key,
    created_at          timestamptz not null default now(),
    payload             jsonb not null,
    -- columns extracted from payload for cheap filtering/listing
    title               text,
    organization        text,
    business_area       text,
    lifecycle_phase     text,
    status              text,
    data_classification text
);
create index if not exists idx_entries_created on registry_entries (created_at desc);
create index if not exists idx_entries_phase   on registry_entries (lifecycle_phase);

-- ── Lifecycle documents ───────────────────────────────────────────────────
create table if not exists documents (
    id           text primary key,
    entry_id     text not null references registry_entries(id) on delete cascade,
    phase        int  not null,
    artifact     text not null,
    file_name    text,
    storage_path text,
    status       text not null default 'UPLOADED'
                 check (status in ('UPLOADED','IN-REVIEW','APPROVED')),
    uploaded_at  timestamptz not null default now(),
    reviewed_at  timestamptz
);
create index if not exists idx_documents_entry on documents (entry_id);

-- ── Business / IT approvals (one row per entry+phase+team) ─────────────────
create table if not exists approvals (
    id         text primary key,
    entry_id   text not null references registry_entries(id) on delete cascade,
    phase      int  not null,
    team       text not null check (team in ('BUSINESS','IT')),
    status     text not null default 'PENDING'
               check (status in ('PENDING','APPROVED')),
    approver   text,
    decided_at timestamptz,
    unique (entry_id, phase, team)
);
create index if not exists idx_approvals_entry on approvals (entry_id);

-- ── Storage bucket for uploaded documents ─────────────────────────────────
-- In the Supabase dashboard: Storage -> New bucket -> name "airegistry-documents".
-- (Or run the line below.)
-- insert into storage.buckets (id, name, public) values
--   ('airegistry-documents','airegistry-documents', false)
--   on conflict (id) do nothing;

-- ── Row Level Security ─────────────────────────────────────────────────────
-- The server uses the service_role key, which bypasses RLS. If you instead use
-- the anon key, enable RLS and add permissive policies, e.g.:
-- alter table registry_entries enable row level security;
-- create policy "anon all" on registry_entries for all
--   using (true) with check (true);
