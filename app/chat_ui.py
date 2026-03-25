from __future__ import annotations
from typing import Callable, Any
import streamlit as st

# Tipo de callback opcional: recebe (pergunta:str, filtros:Any) -> str (resposta do agente)
OnAsk = Callable[[str, Any], str]


def render_chat(area_key: str, filtros: Any, on_ask: OnAsk | None = None) -> None:
    """
    Renderiza um chat simples com histórico.
    - `area_key` diferencia o histórico por página (ex.: "financeiro").
    - `filtros` é repassado ao agente/callback.
    - `on_ask` (opcional) permite injetar uma função que chama o agente.
      Se não for passado, tenta usar `ai.generate_insights` como fallback.
    """
    state_key = f"chat_{area_key}_messages"
    if state_key not in st.session_state:
        st.session_state[state_key] = []

    st.subheader("💬 Fale com o CFO assistente")

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
    prompt = st.chat_input("Pergunte ao CFO sobre os dados deste período…")
    if not prompt:
        return

    # Registra e mostra a mensagem do usuário
    st.session_state[state_key].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Resposta do agente
    try:
        if on_ask is not None:
            resposta = on_ask(prompt, filtros)
    except Exception as e:  # noqa: BLE001
        resposta = f"⚠️ IA indisponível: {e}"

    st.session_state[state_key].append({"role": "assistant", "content": resposta})
    with st.chat_message("assistant"):
        st.markdown(resposta)
