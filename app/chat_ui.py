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
            st.rerun()

    # Exibe histórico
    for msg in st.session_state[state_key]:
        with st.chat_message(msg.get("role", "assistant")):
            st.markdown(msg.get("content", ""))

    # Entrada de chat
    prompt = st.chat_input("Pergunte ao assistente sobre dados e processos.")
    if not prompt:
        return

    # Registra e mostra a mensagem do usuário
    st.session_state[state_key].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Resposta do agente (streaming ou string)
    try:
        raw: str | Iterator[str]
        if on_ask is not None:
            raw = on_ask(prompt, filtros)
        else:
            raw = ""
    except Exception as e:  # noqa: BLE001
        raw = f"⚠️ IA indisponível: {e}"

    with st.chat_message("assistant"):
        if isinstance(raw, str):
            resposta = raw
            st.markdown(resposta)
        else:
            it = iter(raw)
            with st.spinner("Analisando os dados…"):
                try:
                    first = next(it)
                except StopIteration:
                    first = None
            if first is None:
                resposta = ""
                st.caption("Sem resposta.")
            else:
                def stream_all() -> Iterator[str]:
                    yield first
                    yield from it

                streamed = st.write_stream(stream_all())
                resposta = streamed if isinstance(streamed, str) else "".join(str(x) for x in streamed)

    st.session_state[state_key].append({"role": "assistant", "content": resposta})
