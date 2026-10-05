"""Página 2 — Comparação: contexto do eleitorado e contraste com os presidenciáveis.

Tudo na própria página (sem barra lateral), com botão de volta para a votação do Max.
"""
import pandas as pd
import streamlit as st

from dados import (CONTEXTO, botao_pagina, busca_escola, filtra, locais, n,
                   presidenciáveis, seletor_zonas)

df = locais()
todos_pres = presidenciáveis(df)          # [(coluna, rótulo)] do mais votado para o menos
nome_col = dict(todos_pres)

st.title("Comparação — contexto e presidenciáveis")
st.caption("Eleições 2026 · votos do Max por local, ao lado dos números do local e dos candidatos a presidente")

c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
with c1:
    sel_z = seletor_zonas(df, "comp")
with c2:
    botao_pagina("🗳️ Votos do Max", "paginas/votos_max.py", "comp_ir_max")

c3, c4 = st.columns([3, 2], vertical_alignment="bottom")
with c3:
    busca = busca_escola("comp")
with c4:
    escolhidos = st.multiselect(
        "Colunas de presidenciáveis para comparar",
        [c for c, _ in todos_pres],
        format_func=lambda c: nome_col[c],
        key="comp_pres",
        placeholder="escolha um ou mais candidatos",
    )

f = filtra(df, zonas=sel_z, busca=busca)

# ------------------------------------------------------------------ indicadores
k = st.columns(5)
k[0].metric("Votos do Max", n(f["votos_max"].sum()))
k[1].metric("Eleitores", n(f["eleitores"].sum()))
k[2].metric("Abstenções", n(f["abstencao"].sum()))
k[3].metric("Brancos", n(f["brancos"].sum()))
k[4].metric("Nulos", n(f["nulos"].sum()))

# ------------------------------------------------------------------ tabela por local
st.subheader(f"Local por local — {n(len(f))} locais")
rotulos = {"escola": "escola", "bairro": "bairro", "eleitores": "eleitores",
           "compareceram": "compareceram", "abstencao": "abstenções",
           "brancos": "brancos", "nulos": "nulos", "votos_max": "Max"}
colunas = ["zona", "ra", "local", "escola", "bairro"] + CONTEXTO + ["votos_max"] + list(escolhidos)
tabela = f[colunas].copy().rename(columns={**rotulos, **{c: nome_col[c] for c in escolhidos}})
st.dataframe(tabela, hide_index=True, width="stretch", height=430)
st.caption(
    "`compareceram` é o comparecimento do cargo de **deputado distrital** (é o mesmo eleitorado do Max). "
    "Os votos de presidente na mesma linha vêm da urna daquela seção."
)
st.download_button(
    "Baixar CSV (locais filtrados)",
    tabela.to_csv(index=False, sep=";").encode("utf-8-sig"),
    "locais_max_comparacao_2026.csv", "text/csv",
)

# ------------------------------------------------------------------ totais dos presidenciáveis
st.divider()
st.subheader("Presidenciáveis — total no recorte")
total_pres = sum(int(f[c].sum()) for c, _ in todos_pres)
linhas = []
for c, rot in todos_pres:
    v = int(f[c].sum())
    linhas.append({
        "candidato": rot,
        "votos": f"{v:,}".replace(",", "."),
        "% do total de presidente": f"{(100 * v / total_pres if total_pres else 0):.2f}%".replace(".", ","),
    })

st.dataframe(pd.DataFrame(linhas), hide_index=True, width="stretch", height=280)
st.caption("A coluna de porcentagem usa como base a soma dos votos de **todos** os presidenciáveis no recorte "
           "(não é o total oficial de votos válidos).")

with st.expander("Observações sobre os dados"):
    st.markdown(
        "- Fonte: arquivos de urna (BU) publicados pelo TSE + totalização oficial (EA20).\n"
        "- **4 zonas (6, 10, 13 e 16)** somam 10.410 votos de presidente a mais do que a totalização oficial "
        "da zona (0,6% do total do DF) — padrão de votante em trânsito/justificativa. Afeta só as colunas de "
        "presidente; os votos do Max batem exato em 19/19 zonas.\n"
        "- O candidato 28 (Leonardo Avalanche, PRTB) aparece com 57 votos nas urnas do DF mas não existe na "
        "totalização (renunciou em 30/09).\n"
        "- Eleitores, comparecimento, abstenções, brancos e nulos são da eleição de **deputado distrital**."
    )
