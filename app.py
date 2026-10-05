"""Painel de consulta da votação — Max Maciel 50100 (Deputado Distrital, DF).

Duas páginas:
  1. Votos do Max     — mapa dos locais de votação e os votos do Max em cada um.
  2. Comparação       — eleitores, abstenções, brancos, nulos e o contraste com os presidenciáveis.
"""
import streamlit as st

st.set_page_config(page_title="Votação do Max Maciel — DF 2026", page_icon="🗳️", layout="wide")

paginas = [
    st.Page("paginas/votos_max.py", title="Votos do Max", icon="🗳️", default=True),
    st.Page("paginas/comparacao.py", title="Comparação", icon="📊"),
]
st.navigation(paginas).run()
