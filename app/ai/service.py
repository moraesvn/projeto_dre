from __future__ import annotations
from typing import Any, Iterator

import streamlit as st

from . import config
from .agente_cfo import _create_cfo_agent, load_system_prompt

# Fallback: usamos OpenAI direto se Agno/Agent não estiver disponível
try:  # pragma: no cover
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore


@st.cache_resource(show_spinner=False)
def _get_cached_cfo_agent() -> Any:
    """Uma instância do agente Agno por sessão de app (evita recriar a cada mensagem)."""
    return _create_cfo_agent()


@st.cache_resource(show_spinner=False)
def _get_cached_openai_client() -> Any:
    """Cliente OpenAI reutilizado entre mensagens."""
    if OpenAI is None:
        return None
    return OpenAI(api_key=config.get_api_key())


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
    """Interface única para o chat do app; retorna um iterador de chunks para streaming.
    - Tenta usar o agente Agno em cache (um único chunk com a resposta completa).
    - Caso contrário, OpenAI com stream=True e cliente em cache.
    """
    agent = _get_cached_cfo_agent()

    if agent is not None:
        try:
            prompt = f"{_default_context(filtros)}\n\n{pergunta}"
            result = agent.run(prompt)  # type: ignore[attr-defined]
            yield str(result)
            return
        except Exception:
            pass

    system_prompt = load_system_prompt()
    if OpenAI is None:
        yield "⚠️ IA indisponível: biblioteca 'openai' não encontrada no ambiente."
        return

    client = _get_cached_openai_client()
    if client is None:
        yield "⚠️ IA indisponível: não foi possível criar o cliente OpenAI."
        return

    try:
        stream = client.chat.completions.create(
            model=config.get_model_name(),
            temperature=config.get_temperature(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": _default_context(filtros)},
                {"role": "user", "content": pergunta},
            ],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"⚠️ IA indisponível: {e}"
