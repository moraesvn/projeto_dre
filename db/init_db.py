import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "db" / "dre.sqlite"

def init_db(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS dre_linhas (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa   TEXT    NOT NULL,
        ano       INTEGER NOT NULL,
        mes_num   INTEGER NOT NULL CHECK (mes_num BETWEEN 1 AND 12),
        mes       TEXT    NOT NULL,
        descricao TEXT    NOT NULL,
        valor     REAL,
        UNIQUE (empresa, ano, mes_num, descricao)
    );
    """

    create_index_periodo = """
    CREATE INDEX IF NOT EXISTS idx_dre_periodo
    ON dre_linhas (empresa, ano, mes_num);
    """

    create_index_desc = """
    CREATE INDEX IF NOT EXISTS idx_dre_desc
    ON dre_linhas (descricao);
    """

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(create_table_sql)
        cur.execute(create_index_periodo)
        cur.execute(create_index_desc)
        conn.commit()

    print(f"✅ Banco inicializado em: {db_path.resolve()}")

if __name__ == "__main__":
    init_db()
