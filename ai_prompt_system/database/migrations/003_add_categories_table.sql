-- Migration: 003
-- Description: Add categories table and update rule tables
-- Date: 2025-07-06

-- UP Migration

-- 1. Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    color TEXT DEFAULT '#6B7280',
    icon TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Insert default categories
INSERT OR IGNORE INTO categories (name, description, color) VALUES
('instruction', '基本指令和操作指導', '#3B82F6'),
('format', '格式化和結構規則', '#10B981'),
('constraint', '約束和限制條件', '#F59E0B'),
('pattern', '模式和範本', '#8B5CF6'),
('creative_writing', '創意寫作相關', '#EF4444'),
('general', '一般用途', '#6B7280'),
('debugging', '除錯和問題解決', '#F97316'),
('optimization', '優化和效能改善', '#06B6D4'),
('review', '檢查和審核', '#84CC16'),
('explanation', '解釋和說明', '#EC4899');

-- 3. Add category_id columns to existing tables
ALTER TABLE primitive_rules ADD COLUMN category_id INTEGER REFERENCES categories(id);
ALTER TABLE semantic_rules ADD COLUMN category_id INTEGER REFERENCES categories(id);
ALTER TABLE task_rules ADD COLUMN category_id INTEGER REFERENCES categories(id);

-- 4. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_primitive_rules_category_id ON primitive_rules(category_id);
CREATE INDEX IF NOT EXISTS idx_semantic_rules_category_id ON semantic_rules(category_id);
CREATE INDEX IF NOT EXISTS idx_task_rules_category_id ON task_rules(category_id);
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);

-- 5. Add triggers to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_categories_timestamp
    AFTER UPDATE ON categories
    BEGIN
        UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- DOWN Migration (Rollback)

-- 1. Remove triggers
DROP TRIGGER IF EXISTS update_categories_timestamp;

-- 2. Remove indexes
DROP INDEX IF EXISTS idx_categories_name;
DROP INDEX IF EXISTS idx_task_rules_category_id;
DROP INDEX IF EXISTS idx_semantic_rules_category_id;
DROP INDEX IF EXISTS idx_primitive_rules_category_id;

-- 3. Drop categories table
DROP TABLE IF EXISTS categories;
