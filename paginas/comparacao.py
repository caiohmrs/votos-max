"""Página 2 — Comparação: contexto do eleitorado e contraste com os presidenciáveis."""
import pandas as pd
import streamlit as st

from dados import CONTEXTO, filtros, locais, n, presidenciáveis

df = locais()
todos_pres = presidenciáveis(df)          # [(coluna, rótulo)] do mais votado para o menos
nome_col = dict(todos_pres)

st.title("Comparação — contexto e presidenciáveis")
st.caption("Eleições 2026 · votos do Max por local, ao lado dos números do local e dos candidatos a presidente")

f = filtros(df, "comp")

with st.sidebar:
    st.divider()
    st.header("Presidenciáveis")
    escolhidos = st.multiselect(
        "Colunas para comparar",
        [c for c, _ in todos_pres],
        format_func=lambda c: nome_col[c],
        key="comp_pres",
        placeholder="escolha um ou mais candidatos",
    )
    st.caption("A comparação é em votos absolutos, lado a lado (sem percentuais).")

# ------------------------------------------------------------------ indicadores
k = st.columns(5)
k[0].metric("Votos do Max", n(f["votos_max"].sum()))
k[1].metric("Eleitores", n(f["eleitores"].sum()))
k[2].metric("Abstenções", n(f["abstencao"].sum()))
k[3].metric("Brancos", n(f["brancos"].sum()))
k[4].metric("Nulos", n(f["nulos"].sum()))

# ------------------------------------------------------------------ tabela por local
st.subheader("Local por local")
rotulos = {"escola": "escola", "bairro": "bairro", "eleitores": "eleitores",
           "compareceram": "compareceram", "abstencao": "abstenções",
           "brancos": "brancos", "nulos": "nulos", "votos_max": "Max"}
colunas = ["zona", "ra", "local", "escola", "bairro"] + CONTEXTO + ["votos_max"] + list(escolhidos)
tabela = f[colunas].copy()
tabela = tabela.rename(columns={**rotulos, **{c: nome_col[c] for c in escolhidos}})
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
