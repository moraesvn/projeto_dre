import sqlite3
from pathlib import Path
import pandas as pd

# Caminho absoluto para .../PROJETO/db/dre.sqlite (independe de onde o notebook roda)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "db" / "dre.sqlite"
# ------------------------------
# 1. Validação de metadados
# ------------------------------
def validar_metadados(ano: int, empresa: str) -> tuple[int, str]:
    """
    Valida ano e empresa antes de inserir no BD.
    """
    ano = int(ano)
    if ano < 2000 or ano > 2100:
        raise ValueError(f"Ano inválido: {ano}")

    empresa = str(empresa).strip().upper()
    if empresa not in {"SP", "SC"}:
        raise ValueError(f"Empresa inválida: {empresa}. Use 'SP' ou 'SC'.")

    return ano, empresa


# ------------------------------
# 2. Inserção no BD (idempotente)
# ------------------------------
def insert_dre_linhas(df: pd.DataFrame, db_path: Path = DB_PATH) -> None:
    """
    Insere o DataFrame no banco SQLite.
    Usa upsert (ON CONFLICT) para evitar duplicatas.
    Espera colunas: empresa, ano, mes_num, mes, descricao, valor
    """
    insert_sql = """
    INSERT INTO dre_linhas (empresa, ano, mes_num, mes, descricao, valor)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(empresa, ano, mes_num, descricao)
    DO UPDATE SET valor = excluded.valor;
    """

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.executemany(
            insert_sql,
            df[["empresa", "ano", "mes_num", "mes", "descricao", "valor"]].itertuples(index=False, name=None),
        )
        conn.commit()

    print(f"✅ Inseridas {len(df)} linhas em {db_path}")


def delete_dre_periodo(empresa: str, ano: int, db_path: Path = DB_PATH) -> int:
    """Remove todas as linhas do par (empresa, ano). Retorna quantidade apagada."""
    ano, empresa = validar_metadados(ano, empresa)
    sql = "DELETE FROM dre_linhas WHERE empresa = ? AND ano = ?;"
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(sql, (empresa, ano))
        conn.commit()
        return int(cur.rowcount)


def substituir_dre_periodo(
    df: pd.DataFrame,
    ano: int,
    empresa: str,
    db_path: Path = DB_PATH,
) -> tuple[int, int]:
    """
    Valida metadados, apaga o período (empresa, ano) e insere o DataFrame.
    Retorna (linhas_apagadas, linhas_inseridas).
    """
    ano, empresa = validar_metadados(ano, empresa)
    removidas = delete_dre_periodo(empresa, ano, db_path=db_path)
    insert_dre_linhas(df, db_path=db_path)
    return removidas, len(df)
