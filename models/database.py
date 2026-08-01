"""
QFD Application - Database Layer
SQLite-based persistent storage for all QFD project data.
"""
import sqlite3
import json
import os
import time
from datetime import datetime


class Database:
    def __init__(self, db_path="qfd_project.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self, path=None):
        if path:
            self.db_path = path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._create_tables()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def _create_tables(self):
        c = self.conn.cursor()

        # Project metadata
        c.execute("""
        CREATE TABLE IF NOT EXISTS project (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            industry TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime')),
            importance_scale INTEGER DEFAULT 5,
            current_phase INTEGER DEFAULT 1,
            settings TEXT DEFAULT '{}'
        )""")

        # Version snapshots
        c.execute("""
        CREATE TABLE IF NOT EXISTS versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            label TEXT DEFAULT '',
            snapshot TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
        )""")

        # VOC items (Customer Requirements)
        c.execute("""
        CREATE TABLE IF NOT EXISTS voc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            phase INTEGER DEFAULT 1,
            parent_id INTEGER DEFAULT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            source TEXT DEFAULT '',
            importance REAL DEFAULT 3.0,
            kano_type TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0,
            improvement_ratio REAL DEFAULT 1.0,
            sales_point REAL DEFAULT 1.0,
            planned_level REAL DEFAULT 0,
            FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
            FOREIGN KEY(parent_id) REFERENCES voc(id) ON DELETE SET NULL
        )""")

        # CTQ items (Technical Requirements)
        c.execute("""
        CREATE TABLE IF NOT EXISTS ctq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            phase INTEGER DEFAULT 1,
            name TEXT NOT NULL,
            unit TEXT DEFAULT '',
            target_value TEXT DEFAULT '',
            current_value TEXT DEFAULT '',
            direction TEXT DEFAULT 'higher_better',
            difficulty REAL DEFAULT 3.0,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
        )""")

        # HOQ Relationship matrix (VOC-CTQ relationships)
        c.execute("""
        CREATE TABLE IF NOT EXISTS hoq_relationship (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            phase INTEGER DEFAULT 1,
            voc_id INTEGER NOT NULL,
            ctq_id INTEGER NOT NULL,
            strength REAL DEFAULT 0,
            symbol TEXT DEFAULT '',
            FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
            FOREIGN KEY(voc_id) REFERENCES voc(id) ON DELETE CASCADE,
            FOREIGN KEY(ctq_id) REFERENCES ctq(id) ON DELETE CASCADE,
            UNIQUE(project_id, phase, voc_id, ctq_id)
        )""")

        # Roof matrix (CTQ-CTQ correlations)
        c.execute("""
        CREATE TABLE IF NOT EXISTS hoq_roof (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            phase INTEGER DEFAULT 1,
            ctq_id_1 INTEGER NOT NULL,
            ctq_id_2 INTEGER NOT NULL,
            correlation TEXT DEFAULT '',
            FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
            FOREIGN KEY(ctq_id_1) REFERENCES ctq(id) ON DELETE CASCADE,
            FOREIGN KEY(ctq_id_2) REFERENCES ctq(id) ON DELETE CASCADE,
            UNIQUE(project_id, phase, ctq_id_1, ctq_id_2)
        )""")

        # Competitors
        c.execute("""
        CREATE TABLE IF NOT EXISTS competitor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            is_self INTEGER DEFAULT 0,
            color TEXT DEFAULT '#4A90D9',
            FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
        )""")

        # Competitor VOC scores
        c.execute("""
        CREATE TABLE IF NOT EXISTS competitor_voc_score (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_id INTEGER NOT NULL,
            voc_id INTEGER NOT NULL,
            score REAL DEFAULT 0,
            FOREIGN KEY(competitor_id) REFERENCES competitor(id) ON DELETE CASCADE,
            FOREIGN KEY(voc_id) REFERENCES voc(id) ON DELETE CASCADE,
            UNIQUE(competitor_id, voc_id)
        )""")

        # Competitor CTQ scores
        c.execute("""
        CREATE TABLE IF NOT EXISTS competitor_ctq_score (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_id INTEGER NOT NULL,
            ctq_id INTEGER NOT NULL,
            value TEXT DEFAULT '',
            FOREIGN KEY(competitor_id) REFERENCES competitor(id) ON DELETE CASCADE,
            FOREIGN KEY(ctq_id) REFERENCES ctq(id) ON DELETE CASCADE,
            UNIQUE(competitor_id, ctq_id)
        )""")

        # AHP pairwise comparison
        c.execute("""
        CREATE TABLE IF NOT EXISTS ahp_comparison (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            phase INTEGER DEFAULT 1,
            voc_id_1 INTEGER NOT NULL,
            voc_id_2 INTEGER NOT NULL,
            value REAL DEFAULT 1.0,
            FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
            UNIQUE(project_id, phase, voc_id_1, voc_id_2)
        )""")

        # FMEA items
        c.execute("""
        CREATE TABLE IF NOT EXISTS fmea_item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            item_name TEXT DEFAULT '',
            failure_mode TEXT DEFAULT '',
            failure_effect TEXT DEFAULT '',
            severity INTEGER DEFAULT 5,
            failure_cause TEXT DEFAULT '',
            occurrence INTEGER DEFAULT 5,
            control_measure TEXT DEFAULT '',
            detection INTEGER DEFAULT 5,
            suggested_action TEXT DEFAULT '',
            responsible TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
        )""")

        # DSM elements + dependency matrix
        c.execute("""
        CREATE TABLE IF NOT EXISTS dsm_element (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS dsm_dependency (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            from_id INTEGER NOT NULL,
            to_id INTEGER NOT NULL,
            marker TEXT DEFAULT 'X',
            FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
            FOREIGN KEY(from_id) REFERENCES dsm_element(id) ON DELETE CASCADE,
            FOREIGN KEY(to_id) REFERENCES dsm_element(id) ON DELETE CASCADE,
            UNIQUE(project_id, from_id, to_id)
        )""")

        self._migrate_schema(c)
        self.conn.commit()

    def _migrate_schema(self, c):
        """One-time additive migrations for columns introduced after initial release."""
        voc_cols = [r[1] for r in c.execute("PRAGMA table_info(voc)").fetchall()]
        if "current_level" not in voc_cols:
            c.execute("ALTER TABLE voc ADD COLUMN current_level REAL DEFAULT 0")
            # Backfill from any existing self-competitor VOC scores so pre-existing
            # projects don't suddenly show Ui=0 after this upgrade.
            c.execute("""
                UPDATE voc SET current_level = (
                    SELECT cvs.score FROM competitor_voc_score cvs
                    JOIN competitor comp ON comp.id = cvs.competitor_id
                    WHERE comp.is_self=1 AND cvs.voc_id = voc.id
                )
                WHERE EXISTS (
                    SELECT 1 FROM competitor_voc_score cvs
                    JOIN competitor comp ON comp.id = cvs.competitor_id
                    WHERE comp.is_self=1 AND cvs.voc_id = voc.id
                )
            """)

    # === Project CRUD ===
    def create_project(self, name, description="", industry="", importance_scale=5):
        c = self.conn.cursor()
        c.execute("INSERT INTO project (name, description, industry, importance_scale) VALUES (?,?,?,?)",
                  (name, description, industry, importance_scale))
        self.conn.commit()
        return c.lastrowid

    def get_project(self, project_id):
        return self.conn.execute("SELECT * FROM project WHERE id=?", (project_id,)).fetchone()

    def update_project(self, project_id, **kwargs):
        if kwargs:
            sets = ", ".join(f"{k}=?" for k in kwargs)
            vals = list(kwargs.values()) + [project_id]
            self.conn.execute(f"UPDATE project SET {sets}, updated_at=datetime('now','localtime') WHERE id=?", vals)
        else:
            self.conn.execute("UPDATE project SET updated_at=datetime('now','localtime') WHERE id=?", (project_id,))
        self.conn.commit()

    def list_projects(self):
        return self.conn.execute("SELECT * FROM project ORDER BY updated_at DESC").fetchall()

    def delete_project(self, project_id):
        self.conn.execute("DELETE FROM project WHERE id=?", (project_id,))
        self.conn.commit()

    # === VOC CRUD ===
    def add_voc(self, project_id, name, phase=1, parent_id=None, **kwargs):
        cols = "project_id, name, phase, parent_id"
        vals = [project_id, name, phase, parent_id]
        for k, v in kwargs.items():
            cols += f", {k}"
            vals.append(v)
        placeholders = ",".join(["?"] * len(vals))
        c = self.conn.cursor()
        c.execute(f"INSERT INTO voc ({cols}) VALUES ({placeholders})", vals)
        self.conn.commit()
        return c.lastrowid

    def get_vocs(self, project_id, phase=1):
        return self.conn.execute(
            "SELECT * FROM voc WHERE project_id=? AND phase=? ORDER BY sort_order, id",
            (project_id, phase)).fetchall()

    def update_voc(self, voc_id, **kwargs):
        if not kwargs:
            return
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [voc_id]
        self.conn.execute(f"UPDATE voc SET {sets} WHERE id=?", vals)
        self.conn.commit()

    def delete_voc(self, voc_id):
        self.conn.execute("DELETE FROM voc WHERE id=?", (voc_id,))
        self.conn.commit()

    # === CTQ CRUD ===
    def add_ctq(self, project_id, name, phase=1, **kwargs):
        cols = "project_id, name, phase"
        vals = [project_id, name, phase]
        for k, v in kwargs.items():
            cols += f", {k}"
            vals.append(v)
        placeholders = ",".join(["?"] * len(vals))
        c = self.conn.cursor()
        c.execute(f"INSERT INTO ctq ({cols}) VALUES ({placeholders})", vals)
        self.conn.commit()
        return c.lastrowid

    def get_ctqs(self, project_id, phase=1):
        return self.conn.execute(
            "SELECT * FROM ctq WHERE project_id=? AND phase=? ORDER BY sort_order, id",
            (project_id, phase)).fetchall()

    def update_ctq(self, ctq_id, **kwargs):
        if not kwargs:
            return
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [ctq_id]
        self.conn.execute(f"UPDATE ctq SET {sets} WHERE id=?", vals)
        self.conn.commit()

    def delete_ctq(self, ctq_id):
        self.conn.execute("DELETE FROM ctq WHERE id=?", (ctq_id,))
        self.conn.commit()

    # === Relationship Matrix ===
    def set_relationship(self, project_id, voc_id, ctq_id, strength, phase=1, symbol=''):
        self.conn.execute("""
            INSERT INTO hoq_relationship (project_id, phase, voc_id, ctq_id, strength, symbol)
            VALUES (?,?,?,?,?,?)
            ON CONFLICT(project_id, phase, voc_id, ctq_id)
            DO UPDATE SET strength=excluded.strength, symbol=excluded.symbol
        """, (project_id, phase, voc_id, ctq_id, strength, symbol))
        self.conn.commit()

    def get_relationships(self, project_id, phase=1):
        return self.conn.execute(
            "SELECT * FROM hoq_relationship WHERE project_id=? AND phase=?",
            (project_id, phase)).fetchall()

    def get_relationship(self, project_id, voc_id, ctq_id, phase=1):
        return self.conn.execute(
            "SELECT * FROM hoq_relationship WHERE project_id=? AND phase=? AND voc_id=? AND ctq_id=?",
            (project_id, phase, voc_id, ctq_id)).fetchone()

    # === Roof Matrix ===
    def set_roof_correlation(self, project_id, ctq_id_1, ctq_id_2, correlation, phase=1):
        # Ensure consistent ordering
        id1, id2 = min(ctq_id_1, ctq_id_2), max(ctq_id_1, ctq_id_2)
        self.conn.execute("""
            INSERT INTO hoq_roof (project_id, phase, ctq_id_1, ctq_id_2, correlation)
            VALUES (?,?,?,?,?)
            ON CONFLICT(project_id, phase, ctq_id_1, ctq_id_2)
            DO UPDATE SET correlation=excluded.correlation
        """, (project_id, phase, id1, id2, correlation))
        self.conn.commit()

    def get_roof_correlations(self, project_id, phase=1):
        return self.conn.execute(
            "SELECT * FROM hoq_roof WHERE project_id=? AND phase=?",
            (project_id, phase)).fetchall()

    # === Competitors ===
    def add_competitor(self, project_id, name, is_self=False, color='#4A90D9'):
        c = self.conn.cursor()
        c.execute("INSERT INTO competitor (project_id, name, is_self, color) VALUES (?,?,?,?)",
                  (project_id, name, 1 if is_self else 0, color))
        comp_id = c.lastrowid
        self.conn.commit()
        if is_self:
            # Backfill this "self" competitor's scores from any VOC/CTQ current
            # values already entered, so VOC/CTQ/CBA/HOQ start out in sync even
            # if the self competitor is created after those values exist.
            for v in self.conn.execute(
                    "SELECT id, current_level FROM voc WHERE project_id=?", (project_id,)).fetchall():
                if v['current_level']:
                    self.set_competitor_voc_score(comp_id, v['id'], v['current_level'])
            for ct in self.conn.execute(
                    "SELECT id, current_value FROM ctq WHERE project_id=?", (project_id,)).fetchall():
                if ct['current_value']:
                    self.set_competitor_ctq_score(comp_id, ct['id'], ct['current_value'])
        return comp_id

    def get_competitors(self, project_id):
        return self.conn.execute(
            "SELECT * FROM competitor WHERE project_id=? ORDER BY is_self DESC, id",
            (project_id,)).fetchall()

    def get_self_competitor(self, project_id):
        return self.conn.execute(
            "SELECT * FROM competitor WHERE project_id=? AND is_self=1 LIMIT 1",
            (project_id,)).fetchone()

    def sync_self_voc_score(self, project_id, voc_id, value):
        """Single entry point for Ui (当前水平) — keeps VOC.current_level and the
        self-competitor's CBA score identical, wherever the edit came from."""
        self.update_voc(voc_id, current_level=value)
        self_comp = self.get_self_competitor(project_id)
        if self_comp:
            self.set_competitor_voc_score(self_comp['id'], voc_id, value)

    def sync_self_ctq_score(self, project_id, ctq_id, value):
        """Single entry point for CTQ current_value — keeps CTQ.current_value and
        the self-competitor's CBA benchmark identical, wherever the edit came from."""
        self.update_ctq(ctq_id, current_value=str(value))
        self_comp = self.get_self_competitor(project_id)
        if self_comp:
            self.set_competitor_ctq_score(self_comp['id'], ctq_id, str(value))

    def delete_competitor(self, comp_id):
        self.conn.execute("DELETE FROM competitor WHERE id=?", (comp_id,))
        self.conn.commit()

    def set_competitor_voc_score(self, competitor_id, voc_id, score):
        self.conn.execute("""
            INSERT INTO competitor_voc_score (competitor_id, voc_id, score)
            VALUES (?,?,?)
            ON CONFLICT(competitor_id, voc_id) DO UPDATE SET score=excluded.score
        """, (competitor_id, voc_id, score))
        self.conn.commit()

    def get_competitor_voc_scores(self, competitor_id):
        return self.conn.execute(
            "SELECT * FROM competitor_voc_score WHERE competitor_id=?",
            (competitor_id,)).fetchall()

    def set_competitor_ctq_score(self, competitor_id, ctq_id, value):
        self.conn.execute("""
            INSERT INTO competitor_ctq_score (competitor_id, ctq_id, value)
            VALUES (?,?,?)
            ON CONFLICT(competitor_id, ctq_id) DO UPDATE SET value=excluded.value
        """, (competitor_id, ctq_id, value))
        self.conn.commit()

    def get_competitor_ctq_scores(self, competitor_id):
        return self.conn.execute(
            "SELECT * FROM competitor_ctq_score WHERE competitor_id=?",
            (competitor_id,)).fetchall()

    # === AHP ===
    def set_ahp_comparison(self, project_id, voc_id_1, voc_id_2, value, phase=1):
        self.conn.execute("""
            INSERT INTO ahp_comparison (project_id, phase, voc_id_1, voc_id_2, value)
            VALUES (?,?,?,?,?)
            ON CONFLICT(project_id, phase, voc_id_1, voc_id_2)
            DO UPDATE SET value=excluded.value
        """, (project_id, phase, voc_id_1, voc_id_2, value))
        self.conn.commit()

    def get_ahp_comparisons(self, project_id, phase=1):
        return self.conn.execute(
            "SELECT * FROM ahp_comparison WHERE project_id=? AND phase=?",
            (project_id, phase)).fetchall()

    # === FMEA ===
    def add_fmea_item(self, project_id, **kwargs):
        cols = "project_id"
        vals = [project_id]
        for k, v in kwargs.items():
            cols += f", {k}"
            vals.append(v)
        placeholders = ",".join(["?"] * len(vals))
        c = self.conn.cursor()
        c.execute(f"INSERT INTO fmea_item ({cols}) VALUES ({placeholders})", vals)
        self.conn.commit()
        return c.lastrowid

    def get_fmea_items(self, project_id):
        return self.conn.execute(
            "SELECT * FROM fmea_item WHERE project_id=? ORDER BY sort_order, id",
            (project_id,)).fetchall()

    def update_fmea_item(self, item_id, **kwargs):
        if not kwargs:
            return
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [item_id]
        self.conn.execute(f"UPDATE fmea_item SET {sets} WHERE id=?", vals)
        self.conn.commit()

    def delete_fmea_item(self, item_id):
        self.conn.execute("DELETE FROM fmea_item WHERE id=?", (item_id,))
        self.conn.commit()

    # === DSM ===
    def add_dsm_element(self, project_id, name, sort_order=0):
        c = self.conn.cursor()
        c.execute("INSERT INTO dsm_element (project_id, name, sort_order) VALUES (?,?,?)",
                  (project_id, name, sort_order))
        self.conn.commit()
        return c.lastrowid

    def get_dsm_elements(self, project_id):
        return self.conn.execute(
            "SELECT * FROM dsm_element WHERE project_id=? ORDER BY sort_order, id",
            (project_id,)).fetchall()

    def delete_dsm_element(self, element_id):
        self.conn.execute("DELETE FROM dsm_element WHERE id=?", (element_id,))
        self.conn.commit()

    def set_dsm_dependency(self, project_id, from_id, to_id, marker):
        self.conn.execute("""
            INSERT INTO dsm_dependency (project_id, from_id, to_id, marker)
            VALUES (?,?,?,?)
            ON CONFLICT(project_id, from_id, to_id) DO UPDATE SET marker=excluded.marker
        """, (project_id, from_id, to_id, marker))
        self.conn.commit()

    def delete_dsm_dependency(self, project_id, from_id, to_id):
        self.conn.execute(
            "DELETE FROM dsm_dependency WHERE project_id=? AND from_id=? AND to_id=?",
            (project_id, from_id, to_id))
        self.conn.commit()

    def get_dsm_dependencies(self, project_id):
        return self.conn.execute(
            "SELECT * FROM dsm_dependency WHERE project_id=?", (project_id,)).fetchall()

    def clear_dsm_dependencies(self, project_id):
        self.conn.execute("DELETE FROM dsm_dependency WHERE project_id=?", (project_id,))
        self.conn.commit()

    # === Version Control ===
    def save_version(self, project_id, label=""):
        """Save a complete snapshot of the project state."""
        snapshot = {
            "project": dict(self.get_project(project_id)),
            "vocs": [dict(r) for r in self.conn.execute("SELECT * FROM voc WHERE project_id=?", (project_id,)).fetchall()],
            "ctqs": [dict(r) for r in self.conn.execute("SELECT * FROM ctq WHERE project_id=?", (project_id,)).fetchall()],
            "relationships": [dict(r) for r in self.conn.execute("SELECT * FROM hoq_relationship WHERE project_id=?", (project_id,)).fetchall()],
            "roof": [dict(r) for r in self.conn.execute("SELECT * FROM hoq_roof WHERE project_id=?", (project_id,)).fetchall()],
            "competitors": [dict(r) for r in self.conn.execute("SELECT * FROM competitor WHERE project_id=?", (project_id,)).fetchall()],
        }
        self.conn.execute(
            "INSERT INTO versions (project_id, label, snapshot) VALUES (?,?,?)",
            (project_id, label, json.dumps(snapshot, ensure_ascii=False)))
        self.conn.commit()

    def get_versions(self, project_id):
        return self.conn.execute(
            "SELECT id, project_id, label, created_at FROM versions WHERE project_id=? ORDER BY created_at DESC",
            (project_id,)).fetchall()

    def get_version_snapshot(self, version_id):
        row = self.conn.execute("SELECT snapshot FROM versions WHERE id=?", (version_id,)).fetchone()
        return json.loads(row["snapshot"]) if row else None

    # === Utility ===
    def export_project_data(self, project_id):
        """Export all project data as dict for serialization."""
        return {
            "project": dict(self.get_project(project_id)),
            "vocs": [dict(r) for r in self.conn.execute("SELECT * FROM voc WHERE project_id=?", (project_id,)).fetchall()],
            "ctqs": [dict(r) for r in self.conn.execute("SELECT * FROM ctq WHERE project_id=?", (project_id,)).fetchall()],
            "relationships": [dict(r) for r in self.conn.execute("SELECT * FROM hoq_relationship WHERE project_id=?", (project_id,)).fetchall()],
            "roof": [dict(r) for r in self.conn.execute("SELECT * FROM hoq_roof WHERE project_id=?", (project_id,)).fetchall()],
            "competitors": [dict(r) for r in self.conn.execute("SELECT * FROM competitor WHERE project_id=?", (project_id,)).fetchall()],
            "competitor_voc_scores": [dict(r) for r in self.conn.execute("""
                SELECT cvs.* FROM competitor_voc_score cvs
                JOIN competitor c ON c.id=cvs.competitor_id WHERE c.project_id=?""", (project_id,)).fetchall()],
            "competitor_ctq_scores": [dict(r) for r in self.conn.execute("""
                SELECT ccs.* FROM competitor_ctq_score ccs
                JOIN competitor c ON c.id=ccs.competitor_id WHERE c.project_id=?""", (project_id,)).fetchall()],
            "ahp": [dict(r) for r in self.conn.execute("SELECT * FROM ahp_comparison WHERE project_id=?", (project_id,)).fetchall()],
        }
