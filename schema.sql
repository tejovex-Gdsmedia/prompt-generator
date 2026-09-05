-- ============================================================
--  schema.sql — PostgreSQL / Supabase Database Setup Script
--
--  Run this in your Supabase Dashboard -> SQL Editor
-- ============================================================

-- Step 1: Create the users table
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Create the prompts table
CREATE TABLE IF NOT EXISTS prompts (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER REFERENCES users(id) ON DELETE CASCADE,
    user_input       TEXT NOT NULL,
    category         VARCHAR(50) NOT NULL,
    generated_prompt TEXT NOT NULL,
    is_favorite      INTEGER DEFAULT 0,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
--  Tables are ready for PromptGen!
-- ============================================================

