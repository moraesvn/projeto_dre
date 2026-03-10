from __future__ import annotations
from typing import Callable, Any, Iterator, Union
import streamlit as st

# Callback: (pergunta, filtros) -> str ou Iterator[str] (streaming)
OnAsk = Callable[[str, Any], Union[str, Iterator[str]]]


def render_chat(area_key: str, filtros: Any, on_ask: OnAsk | None = None) -> None:
    """
    Renderiza um chat simples com histórico.
    - `area_key` diferencia o histórico por página (ex.: "financeiro").
    - `filtros` é repassado ao agente/callback.
    - `on_ask` (opcional) pode retornar str ou um iterador de chunks para streaming.
    """
    state_key = f"chat_{area_key}_messages"
    if state_key not in st.session_state:
        st.session_state[state_key] = []

    st.subheader("💬 Chat com o CEO assistente (IA)")

    # Botões utilitários
    col_a, col_b = st.columns([1, 6])
    with col_a:
        if st.button("Limpar conversa", use_container_width=True):
            st.session_state[state_key] = []
            st.experimental_rerun()

    # Exibe histórico
    for msg in st.session_state[state_key]:
        with st.chat_message(msg.get("role", "assistant")):
            st.markdown(msg.get("content", ""))

    # Entrada de chat
    prompt = st.chat_input("Pergunte ao CEO assistente sobre dados e processos.")
    if not prompt:
        return

    # Registra e mostra a mensagem do usuário
    st.session_state[state_key].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Resposta do agente (streaming ou string)
    try:
        if on_ask is not None:
            result = on_ask(prompt, filtros)
        else:
            result = ""
    except Exception as e:  # noqa: BLE001
        result = f"⚠️ IA indisponível: {e}"

    # Exibe em tempo real: se for iterador, usa write_stream; senão markdown
    with st.chat_message("assistant"):
        if isinstance(result, str):
            resposta = result
            st.markdown(resposta)
        else:
            parts: list[str] = []

            def stream_and_collect() -> Iterator[str]:
                for chunk in result:
                    parts.append(chunk)
                    yield chunk

            st.write_stream(stream_and_collect())
            resposta = "".join(parts)

    st.session_state[state_key].append({"role": "assistant", "content": resposta})
