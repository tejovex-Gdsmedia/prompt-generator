-- ============================================================
--  schema.sql — Database Setup Script
--
--  Run this file in MySQL to create the database and table.
--
--  How to run:
--  1. Open MySQL Workbench or the MySQL command line
--  2. Run:  SOURCE /full/path/to/schema.sql;
--     OR    Copy-paste all lines below and execute them
-- ============================================================


-- Step 1: Create the database (skip if it already exists)
CREATE DATABASE IF NOT EXISTS promptgen_db;

-- Step 2: Switch to using our new database
USE promptgen_db;

-- Step 3: Create the prompts table
--   id               → auto-numbered unique ID for each row
--   user_input       → the text the user typed (their goal/task)
--   category         → the selected category (Coding, Study, etc.)
--   generated_prompt → the full AI prompt we built for them
--   created_at       → automatically set to the current date & time
CREATE TABLE IF NOT EXISTS prompts (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    user_input       TEXT         NOT NULL,
    category         VARCHAR(50)  NOT NULL,
    generated_prompt TEXT         NOT NULL,
    created_at       DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
--  That's it! Your database is ready.
--  Now update config.py with your MySQL credentials and run:
--  python run.py
-- ============================================================
