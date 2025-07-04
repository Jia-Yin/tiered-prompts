-- Main rule tables
CREATE TABLE IF NOT EXISTS primitive_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    description TEXT,
    category TEXT CHECK(category IN ('instruction', 'format', 'constraint', 'pattern')),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS semantic_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    content_template TEXT NOT NULL,
    description TEXT,
    category TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    prompt_template TEXT NOT NULL,
    description TEXT,
    language TEXT,
    framework TEXT,
    domain TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Relationship tables
CREATE TABLE IF NOT EXISTS semantic_primitive_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    semantic_rule_id INTEGER NOT NULL,
    primitive_rule_id INTEGER NOT NULL,
    weight REAL DEFAULT 1.0,
    order_index INTEGER DEFAULT 0,
    is_required BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (semantic_rule_id) REFERENCES semantic_rules(id) ON DELETE CASCADE,
    FOREIGN KEY (primitive_rule_id) REFERENCES primitive_rules(id) ON DELETE CASCADE,
    UNIQUE(semantic_rule_id, primitive_rule_id)
);

CREATE TABLE IF NOT EXISTS task_semantic_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_rule_id INTEGER NOT NULL,
    semantic_rule_id INTEGER NOT NULL,
    weight REAL DEFAULT 1.0,
    order_index INTEGER DEFAULT 0,
    is_required BOOLEAN DEFAULT TRUE,
    context_override TEXT, -- JSON object
    FOREIGN KEY (task_rule_id) REFERENCES task_rules(id) ON DELETE CASCADE,
    FOREIGN KEY (semantic_rule_id) REFERENCES semantic_rules(id) ON DELETE CASCADE,
    UNIQUE(task_rule_id, semantic_rule_id)
);

-- Versioning table
CREATE TABLE IF NOT EXISTS rule_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_type TEXT NOT NULL,
    rule_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    content_snapshot TEXT NOT NULL,
    change_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(rule_type, rule_id, version_number)
);

-- Tagging tables
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS rule_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_type TEXT NOT NULL,
    rule_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE(rule_type, rule_id, tag_id)
);

-- Migration table
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    description TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Triggers for updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_primitive_rules_updated_at
AFTER UPDATE ON primitive_rules
FOR EACH ROW
BEGIN
    UPDATE primitive_rules SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_semantic_rules_updated_at
AFTER UPDATE ON semantic_rules
FOR EACH ROW
BEGIN
    UPDATE semantic_rules SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_task_rules_updated_at
AFTER UPDATE ON task_rules
FOR EACH ROW
BEGIN
    UPDATE task_rules SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
