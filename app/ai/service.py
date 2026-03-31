from __future__ import annotations
from typing import Any, Iterator

import streamlit as st

from .agente_cfo import _create_cfo_agent


@st.cache_resource(show_spinner=False)
def _get_cached_cfo_agent() -> Any:
    """Uma instância do agente Agno por sessão de app (evita recriar a cada mensagem)."""
    return _create_cfo_agent()


def _default_context(filtros: Any) -> str:
    """Contexto padrão (não restritivo) para orientar respostas quando a pergunta não especificar escopo.
    Apenas para dar um default amigável; o agente pode ignorar se o usuário pedir outro recorte.
    """
    emp = getattr(filtros, "empresas", []) or []
    anos = getattr(filtros, "anos", []) or []
    mes_ini = getattr(filtros, "mes_ini", 1)
    mes_fim = getattr(filtros, "mes_fim", 12)
    return (
        f"Contexto default do app (pode ser ignorado se o usuário pedir outro recorte):\n"
        f"Empresas: {', '.join(emp) if emp else 'todas'} | "
        f"Anos: {', '.join(map(str, anos)) if anos else 'todos'} | "
        f"Meses: {mes_ini}–{mes_fim}."
    )


def ask_cfo(pergunta: str, filtros: Any) -> Iterator[str]:
    """Interface única para o chat: apenas o agente Agno (em cache). Retorna chunks para streaming."""
    agent = _get_cached_cfo_agent()

    if agent is None:
        yield (
            "⚠️ IA indisponível: o agente Agno não pôde ser criado. "
            "Confira se o pacote `agno` está instalado, a API do exemplo (`from agno import Agent`) "
            "é compatível com sua versão e se as variáveis do modelo (ex.: `OPENAI_API_KEY`) estão definidas."
        )
        return

    try:
        prompt = f"{_default_context(filtros)}\n\n{pergunta}"
        result = agent.run(prompt)  # type: ignore[attr-defined]
        yield str(result)
    except Exception as e:  # noqa: BLE001
        yield f"⚠️ Erro ao executar o agente: {e}"
