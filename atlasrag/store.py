import sqlite3
import json
import hashlib
from pathlib import Path
from .text import chunks, hashed_vector

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, title TEXT NOT NULL, source TEXT NOT NULL, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS passages (id TEXT PRIMARY KEY, document_id TEXT NOT NULL, ordinal INTEGER NOT NULL, text TEXT NOT NULL, vector TEXT NOT NULL, FOREIGN KEY(document_id) REFERENCES documents(id));
CREATE INDEX IF NOT EXISTS idx_passage_document ON passages(document_id);
"""
class Store:
    def __init__(self, path):
        self.path = str(path)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        try:
            self.db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS passage_fts USING fts5(id UNINDEXED, text, tokenize='porter unicode61')")
            self.fts = True
        except sqlite3.OperationalError:
            self.fts = False
        self.db.commit()

    def close(self):
        self.db.close()

    def add(self, title, source, body, chunk_size=110, overlap=20):
        if not title.strip() or not body.strip():
            raise ValueError("Title and body required")
        doc_id = hashlib.sha256((source+"\0"+title).encode()).hexdigest()[:16]
        with self.db:
            ids = [r[0] for r in self.db.execute("SELECT id FROM passages WHERE document_id=?", (doc_id,))]
            if self.fts:
                for pid in ids:
                    self.db.execute("DELETE FROM passage_fts WHERE id=?", (pid,))
            self.db.execute("DELETE FROM passages WHERE document_id=?", (doc_id,))
            self.db.execute("INSERT OR REPLACE INTO documents VALUES (?,?,?,?)", (doc_id,title,source,body))
            for i, passage in enumerate(chunks(body,chunk_size,overlap)):
                pid = f"{doc_id}:{i}"
                self.db.execute("INSERT INTO passages VALUES (?,?,?,?,?)",(pid,doc_id,i,passage,json.dumps(hashed_vector(passage))))
                if self.fts:
                    self.db.execute("INSERT INTO passage_fts(id,text) VALUES (?,?)",(pid,passage))
        return doc_id

    def passages(self):
        return self.db.execute("SELECT p.id,p.document_id,p.ordinal,p.text,p.vector,d.title,d.source FROM passages p JOIN documents d ON p.document_id=d.id ORDER BY p.id").fetchall()

    def fts_ids(self, query, limit=50):
        if not self.fts:
            return []
        from .text import tokens
        terms = tokens(query)
        if not terms:
            return []
        match = " OR ".join('"'+t+'"' for t in terms)
        return [(r[0],float(r[1])) for r in self.db.execute("SELECT id,bm25(passage_fts) FROM passage_fts WHERE passage_fts MATCH ? ORDER BY bm25(passage_fts) LIMIT ?",(match,limit))]
