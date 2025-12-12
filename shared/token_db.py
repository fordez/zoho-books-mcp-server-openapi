import secrets
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class TokenDB:
    """Base de datos multi-tenant para tokens de Zoho"""

    def __init__(self, db_path: str):
        # Ruta absoluta segura
        self.db_path = Path(db_path).resolve()
        self.local = threading.local()
        self._init_db()

    def _get_conn(self):
        """Thread-safe connection"""
        if not hasattr(self.local, "conn"):
            self.local.conn = sqlite3.connect(
                str(self.db_path), check_same_thread=False, timeout=10.0
            )
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn

    def _init_db(self):
        """Crear tablas si no existen"""
        conn = self._get_conn()

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                access_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                organization_id TEXT NOT NULL,
                api_domain TEXT NOT NULL,
                region TEXT,
                expires_at TEXT NOT NULL,
                connected_at TEXT NOT NULL,
                last_used TEXT,
                email TEXT,
                company_name TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)

        conn.execute("CREATE INDEX IF NOT EXISTS idx_org_id ON users(organization_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_active ON users(is_active)")

        conn.commit()
        print(f"✅ Database initialized at: {self.db_path}")

    def save_user(self, user_id: str, data: Dict) -> None:
        """Guardar o actualizar usuario"""
        conn = self._get_conn()

        cursor = conn.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()

        if exists:
            conn.execute(
                """
                UPDATE users SET
                    access_token = ?, refresh_token = ?, organization_id = ?,
                    api_domain = ?, region = ?, expires_at = ?,
                    email = ?, company_name = ?, is_active = 1
                WHERE user_id = ?
                """,
                (
                    data["access_token"],
                    data["refresh_token"],
                    data["organization_id"],
                    data["api_domain"],
                    data.get("region", ""),
                    data["expires_at"],
                    data.get("email", ""),
                    data.get("company_name", ""),
                    user_id,
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO users
                (user_id, access_token, refresh_token, organization_id,
                 api_domain, region, expires_at, connected_at, email, company_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    data["access_token"],
                    data["refresh_token"],
                    data["organization_id"],
                    data["api_domain"],
                    data.get("region", ""),
                    data["expires_at"],
                    data.get("connected_at", datetime.now().isoformat()),
                    data.get("email", ""),
                    data.get("company_name", ""),
                ),
            )

        conn.commit()
        print(f"💾 Saved user: {user_id}")

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Obtener usuario por user_id"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM users WHERE user_id = ? AND is_active = 1", (user_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        conn.execute(
            "UPDATE users SET last_used = ? WHERE user_id = ?",
            (datetime.now().isoformat(), user_id),
        )
        conn.commit()

        return dict(row)

    def update_tokens(self, user_id: str, access_token: str, expires_at: str) -> None:
        """Actualizar solo tokens (para refresh)"""
        conn = self._get_conn()
        conn.execute(
            """
            UPDATE users
            SET access_token = ?, expires_at = ?, last_used = ?
            WHERE user_id = ?
            """,
            (access_token, expires_at, datetime.now().isoformat(), user_id),
        )
        conn.commit()

    def list_users(self) -> List[Dict]:
        """Listar todos los usuarios activos"""
        conn = self._get_conn()
        cursor = conn.execute("""
            SELECT user_id, organization_id, api_domain, connected_at,
                   last_used, email, company_name
            FROM users
            WHERE is_active = 1
            ORDER BY last_used DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict:
        """Estadísticas"""
        conn = self._get_conn()
        cursor = conn.execute("""
            SELECT
                COUNT(*) as total_users,
                COUNT(CASE WHEN last_used > datetime('now', '-7 days') THEN 1 END) as active_7d,
                COUNT(CASE WHEN last_used > datetime('now', '-30 days') THEN 1 END) as active_30d
            FROM users WHERE is_active = 1
        """)
        row = cursor.fetchone()
        return dict(row) if row else {}


# -------------------------
#   SINGLETON GLOBAL
# -------------------------

_db_instance = None


def get_db(db_path: str = None) -> TokenDB:
    """
    Obtiene instancia singleton de TokenDB.

    Si no se envía db_path, usa automáticamente:
       oauth_page/zoho_tokens.db
    """
    global _db_instance

    if _db_instance is None:
        if db_path is None:
            # ruta del proyecto → oauth_page/zoho_tokens.db
            project_root = Path(__file__).resolve().parents[1]
            db_path = project_root / "oauth_page" / "zoho_tokens.db"

        _db_instance = TokenDB(str(db_path))

    return _db_instance
