"""Tools expostas ao agente Agno (CFO)."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from agno.tools import tool

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = _PROJECT_ROOT / "db" / "dre.sqlite"

_MAX_ROWS = 500

_FORBIDDEN = (
    "INSERT ",
    "UPDATE ",
    "DELETE ",
    "DROP ",
    "CREATE ",
    "ALTER ",
    "ATTACH ",
    "DETACH ",
    "REPLACE ",
    "TRUNCATE ",
    "PRAGMA ",
    "VACUUM",
    "BEGIN ",
    "COMMIT",
    "ROLLBACK",
)


def _validate_readonly_select(sql: str) -> str | None:
    """Retorna mensagem de erro ou None se OK."""
    q = sql.strip().rstrip(";").strip()
    if not q:
        return "Consulta vazia."
    upper = q.upper()
    if not upper.startswith("SELECT"):
        return "Apenas consultas SELECT são permitidas (leitura)."
    if ";" in q:
        return "Use uma única instrução SQL (sem ponto e vírgula no meio)."
    for token in _FORBIDDEN:
        if token in upper:
            return f"Comando não permitido (contém '{token.strip()}')."
    return None


@tool(
    name="consultar_dre_sqlite",
    description=(
        "Executa uma consulta SQL somente leitura na tabela DRE (SQLite). "
        "Use SELECT na tabela `dre_linhas` (colunas: empresa, ano, mes_num, mes, descricao, valor). "
        "Máximo de 500 linhas retornadas."
    ),
)
def consultar_dre_sqlite(sql: str) -> str:
    """Roda um SELECT validado contra `dre.sqlite` e devolve JSON (lista de objetos)."""
    err = _validate_readonly_select(sql)
    if err:
        return json.dumps({"erro": err}, ensure_ascii=False)

    q = sql.strip().rstrip(";").strip()

    if not DB_PATH.is_file():
        return json.dumps(
            {"erro": f"Banco não encontrado em {DB_PATH}"},
            ensure_ascii=False,
        )

    db_uri = DB_PATH.resolve().as_uri() + "?mode=ro"
    try:
        with sqlite3.connect(db_uri, uri=True) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(q)
            rows = cur.fetchmany(_MAX_ROWS + 1)
    except sqlite3.Error as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)

    truncated = len(rows) > _MAX_ROWS
    if truncated:
        rows = rows[:_MAX_ROWS]

    data = [dict(r) for r in rows]
    out: dict = {"linhas": data, "total_retornado": len(data)}
    if truncated:
        out["aviso"] = f"Resultado limitado a {_MAX_ROWS} linhas."
    return json.dumps(out, ensure_ascii=False, default=str)
