from __future__ import annotations
from typing import Any, Dict, List, Iterator
from pathlib import Path

from . import config
from .agente_cfo import make_cfo_agent, load_system_prompt

# Fallback: usamos OpenAI direto se Agno/Agent não estiver disponível
try:  # pragma: no cover
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore


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
    - Tenta usar o agente Agno se existir (entrega a resposta em um único chunk).
    - Caso contrário, usa chamada direta ao modelo com stream=True.
    """
    agent = make_cfo_agent()

    # Se tivermos um agente Agno funcional, usamos ele (um único yield com a resposta completa)
    if agent is not None:
        try:
            prompt = f"{_default_context(filtros)}\n\n{pergunta}"
            result = agent.run(prompt)  # type: ignore[attr-defined]
            yield str(result)
            return
        except Exception:
            pass

    # Fallback direto ao LLM (OpenAI) com streaming
    system_prompt = load_system_prompt()
    api_key = config.get_api_key()
    if OpenAI is None:
        yield "⚠️ IA indisponível: biblioteca 'openai' não encontrada no ambiente."
        return

    client = OpenAI(api_key=api_key)
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
