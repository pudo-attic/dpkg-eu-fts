


EU Budget Reference Data
------------------------

From SQLite-loaded EU budget:

CREATE TABLE fts_reference (name TEXT, label TEXT, description TEXT, legal_basis TEXT)
INSERT INTO fts_reference SELECT DISTINCT title_name AS name, title_label AS label, "", "" FROM budget WHERE volume_name = "Section 3"; 

SELECT DISTINCT title_name AS name, title_label AS label, "" AS description, "" AS legal_basis FROM budget WHERE volume_name = "Section 3";·


INSERT INTO fts_reference SELECT DISTINCT article_name AS name, article_label AS label, article_description AS description, article_legal_basis AS legal_basis FROM budget WHERE volume_name = "Section 3";·
INSERT INTO fts_reference SELECT DISTINCT item_name AS name, item_label AS label, item_description AS description, item_legal_basis AS legal_basis FROM budget WHERE volume_name = "Section 3";·


