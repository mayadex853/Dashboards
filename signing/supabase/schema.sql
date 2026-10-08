-- HD Sign database schema. Paste into Supabase > SQL Editor and run once.
-- All access goes through the server using the service role key; RLS is enabled
-- with no policies so the public anon key can read nothing.

create table if not exists profile (
  id text primary key,            -- always 'me'
  data jsonb not null default '{}',
  signature text,                 -- PNG data URL
  initials text,                  -- PNG data URL
  created_at timestamptz not null default now(),
  updated_at timestamptz
);

create table if not exists templates (
  id uuid primary key,
  name text not null,
  category text,
  description text,
  pdf_path text not null,
  roles jsonb not null default '[]',
  fields jsonb not null default '[]',
  created_at timestamptz not null default now(),
  updated_at timestamptz
);

create table if not exists envelopes (
  id uuid primary key,
  title text not null,
  status text not null default 'draft',      -- draft | sent | completed | voided
  source text,                               -- template | upload | intake
  template_id uuid references templates(id) on delete set null,
  intake_id uuid,
  original_pdf_path text,
  current_pdf_path text,
  final_pdf_path text,
  original_sha256 text,
  final_sha256 text,
  fields jsonb not null default '[]',
  message text,
  created_at timestamptz not null default now(),
  sent_at timestamptz,
  completed_at timestamptz,
  voided_at timestamptz
);

create table if not exists recipients (
  id uuid primary key,
  envelope_id uuid not null references envelopes(id) on delete cascade,
  role_index int not null,
  name text not null,
  email text not null,
  routing_order int not null default 1,
  is_me boolean not null default false,
  token_hash text,
  status text not null default 'pending',    -- pending | sent | viewed | signed
  sent_at timestamptz,
  viewed_at timestamptz,
  consent_at timestamptz,
  signed_at timestamptz,
  ip text,
  user_agent text,
  created_at timestamptz not null default now()
);
create index if not exists recipients_token_idx on recipients(token_hash);
create index if not exists recipients_env_idx on recipients(envelope_id);

create table if not exists intakes (
  id uuid primary key,
  token_hash text not null,
  category text not null,
  template_id uuid references templates(id) on delete set null,
  signee_name text,
  signee_email text not null,
  deal jsonb not null default '{}',
  answers jsonb,
  status text not null default 'sent',       -- sent | submitted | contracted
  auto_send boolean not null default false,
  message text,
  envelope_id uuid,
  created_at timestamptz not null default now(),
  submitted_at timestamptz
);
create index if not exists intakes_token_idx on intakes(token_hash);

create table if not exists events (
  id uuid primary key,
  envelope_id uuid references envelopes(id) on delete cascade,
  recipient_id uuid,
  type text not null,
  detail jsonb,
  ip text,
  user_agent text,
  created_at timestamptz not null default now()
);
create index if not exists events_env_idx on events(envelope_id);

create table if not exists quick_signs (
  id uuid primary key,
  title text not null,
  pdf_path text not null,
  sha256 text,
  emailed_to text,
  created_at timestamptz not null default now()
);

alter table profile enable row level security;
alter table templates enable row level security;
alter table envelopes enable row level security;
alter table recipients enable row level security;
alter table intakes enable row level security;
alter table events enable row level security;
alter table quick_signs enable row level security;

-- Private storage bucket for all PDFs
insert into storage.buckets (id, name, public)
values ('documents', 'documents', false)
on conflict (id) do nothing;
