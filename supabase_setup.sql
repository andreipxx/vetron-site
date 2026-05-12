-- VETRON profiles table
create table if not exists public.profiles (
  id uuid references auth.users on delete cascade primary key,
  name text not null,
  email text not null,
  fuel_type text default 'benzina',
  plan text default 'trial',
  created_at timestamptz default now()
);

-- RLS
alter table public.profiles enable row level security;

-- Users can read their own profile
create policy "Users can view own profile" on public.profiles
  for select using (auth.uid() = id);

-- Users can update their own profile
create policy "Users can update own profile" on public.profiles
  for update using (auth.uid() = id);

-- Users can insert their own profile (on signup)
create policy "Users can insert own profile" on public.profiles
  for insert with check (auth.uid() = id);

-- Auto-create profile on signup via trigger
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, name, email)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'name', ''),
    new.email
  );
  return new;
end;
$$ language plpgsql security definer;

-- Trigger
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
