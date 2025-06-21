import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from config import DB_FILE, ARTICLES

DB_PATH = Path(DB_FILE)
DB_DIR = DB_PATH.parent


def init_db() -> None:
    """Initialize SQLite database and create tables if needed."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                article_id INTEGER,
                product_name TEXT,
                total_stock INTEGER,
                warehouses INTEGER,
                details TEXT
            )
            """
        )
        conn.commit()


def insert_stock_history(data: Dict[str, Any], date: Optional[str] = None) -> None:
    """Insert scraped data into the database."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        for art_id, product_name in ARTICLES.items():
            item = data.get(product_name)
            if isinstance(item, dict):
                total = item.get("total_stock")
                wh = item.get("warehouses")
                details = json.dumps(item.get("details", {}), ensure_ascii=False)
            else:
                total = None
                wh = None
                details = json.dumps({"info": item}, ensure_ascii=False)
            conn.execute(
                """
                INSERT INTO stock_history
                (date, article_id, product_name, total_stock, warehouses, details)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (date, art_id, product_name, total, wh, details),
            )
        conn.commit()


def fetch_stock_by_date(date: Optional[str] = None) -> Dict[str, Any]:
    """Fetch stock information for a specific date."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    result: Dict[str, Any] = {}
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            SELECT product_name, total_stock, warehouses, details
            FROM stock_history WHERE date = ?
            """,
            (date,),
        )
        for product_name, total, wh, details_json in cur.fetchall():
            details = json.loads(details_json)
            if total is not None:
                result[product_name] = {
                    "total_stock": total,
                    "warehouses": wh,
                    "details": details,
                }
            else:
                result[product_name] = details.get("info", "No data")
    return result


def fetch_stock_range(days: int = 7) -> Dict[str, Dict[str, int]]:
    """Return stock data aggregated by date for the last `days` days."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)
    data: Dict[str, Dict[str, int]] = {}
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            SELECT product_name, date, total_stock, details
            FROM stock_history
            WHERE date BETWEEN ? AND ?
            ORDER BY date
            """,
            (start_date.isoformat(), end_date.isoformat()),
        )
        for product_name, date_str, total, details_json in cur.fetchall():
            qty = 0
            if total is not None:
                qty = total
            else:
                details = json.loads(details_json)
                qty = details.get("info") if isinstance(details, dict) else 0
            data.setdefault(product_name, {})[date_str] = qty
    return data

# Initialize DB on module import
init_db()
