-- PostgreSQL initialization script for Kade Connect
-- This script sets up the database with required extensions and initial data

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create initial database user if not exists
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'kade_user') THEN
      
      CREATE ROLE kade_user LOGIN PASSWORD 'kade_password';
   END IF;
END
$do$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE kade_connect TO kade_user;
GRANT ALL ON SCHEMA public TO kade_user;

-- Create indexes for better performance
-- These will be created after tables are set up by SQLAlchemy

-- Initial seed data for categories
INSERT INTO categories (name) VALUES 
    ('Groceries'),
    ('Dairy'),
    ('Beverages'),
    ('Snacks'),
    ('Household'),
    ('Personal Care')
ON CONFLICT DO NOTHING;

-- Initial seed data for brands (Sri Lankan brands)
INSERT INTO brands (name) VALUES 
    ('Anchor'),
    ('Maliban'),
    ('Munchee'),
    ('Kotmale'),
    ('Pelwatte'),
    ('CBL'),
    ('Keells'),
    ('Prima'),
    ('MD'),
    ('Elephant House')
ON CONFLICT DO NOTHING;
