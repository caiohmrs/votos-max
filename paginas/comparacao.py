"""Página 2 — Comparação: votos do Max contra os presidenciáveis escolhidos, brancos, nulos e abstenções.

Visão principal em cartões (um por local), com barra proporcional em cada linha para
comparar de imediato. A tabela completa fica como visão alternativa.
"""
import html

import pandas as pd
import streamlit as st

from dados import (AZUL, CINZA, CONTEXTO, LARANJA, botao_pagina, busca_escola, cabecalho,
                   filtra, locais, n, presidenciáveis, seletor_zonas)

df = locais()
todos_pres = presidenciáveis(df)          # [(coluna, rótulo)] do mais votado para o menos
nome_col = dict(todos_pres)

cabecalho("Comparação — Max x presidenciáveis",
          "Eleições 2026 · votos do Max por local, lado a lado com os presidenciáveis escolhidos, "
          "abstenções, brancos e nulos")

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
        "Presidenciáveis para comparar",
        [c for c, _ in todos_pres],
        format_func=lambda c: nome_col[c],
        key="comp_pres",
        placeholder="escolha um ou mais candidatos",
    )

f = filtra(df, zonas=sel_z, busca=busca)

k = st.columns(5)
k[0].metric("Votos do Max", n(f["votos_max"].sum()))
k[1].metric("Eleitores", n(f["eleitores"].sum()))
k[2].metric("Abstenções", n(f["abstencao"].sum()))
k[3].metric("Brancos", n(f["brancos"].sum()))
k[4].metric("Nulos", n(f["nulos"].sum()))

# ------------------------------------------------------------------ local por local
st.divider()
st.subheader(f"Local por local — {n(len(f))} locais")
modo = st.radio("Como ver", ["Cartões", "Tabela"], horizontal=True, key="comp_modo")
st.caption("🟡 Max · 🔵 presidenciável escolhido · ⚪ abstenções, brancos e nulos — a barra de cada linha "
           "é proporcional ao maior número do cartão. Eleitores e comparecimento ficam na visão em Tabela.")

if modo == "Cartões":
    if not escolhidos:
        st.info("Escolha um ou mais presidenciáveis acima para comparar com o Max — por enquanto os cartões "
                "mostram só o Max, abstenções, brancos e nulos.")
    blocos = []
    for _, r in f.sort_values("votos_max", ascending=False).iterrows():
        valores = [("Max", int(r["votos_max"]), LARANJA, True)]
        valores += [(nome_col[c], int(r[c]), AZUL, False) for c in escolhidos]
        valores += [("Abstenções", int(r["abstencao"]), CINZA, False),
                    ("Brancos", int(r["brancos"]), CINZA, False),
                    ("Nulos", int(r["nulos"]), CINZA, False)]
        maior = max(v for _, v, _, _ in valores) or 1
        linhas = "".join(
            f'<div class="l"><div class="r">{html.escape(rot)}</div>'
            f'<div class="b"><i style="width:{100 * val / maior:.1f}%;background:{cor}"></i></div>'
            f'<div class="v{" f" if forte else ""}">{n(val)}</div></div>'
            for rot, val, cor, forte in valores
        )
        blocos.append(
            f'<div class="cmp"><div class="e">{html.escape(str(r["escola"]))}</div>'
            f'<div class="s">{html.escape(str(r["ra"]))} · zona {int(r["zona"])}</div>{linhas}</div>'
        )
    st.markdown("".join(blocos), unsafe_allow_html=True)
else:
    rotulos = {"escola": "escola", "bairro": "bairro", "eleitores": "eleitores",
               "compareceram": "compareceram", "abstencao": "abstenções",
               "brancos": "brancos", "nulos": "nulos", "votos_max": "Max"}
    colunas = ["zona", "ra", "local", "escola", "bairro"] + CONTEXTO + ["votos_max"] + list(escolhidos)
    tabela = f[colunas].copy().rename(columns={**rotulos, **{c: nome_col[c] for c in escolhidos}})
    st.dataframe(tabela, hide_index=True, width="stretch", height=430)
    st.caption("`compareceram` é o comparecimento do cargo de **deputado distrital** (mesmo eleitorado do Max). "
               "Os votos de presidente na mesma linha vêm da urna daquela seção.")

st.download_button(
    "Baixar CSV (locais filtrados)",
    f[["zona", "ra", "escola", "eleitores", "compareceram", "abstencao", "brancos", "nulos", "votos_max"]
      + list(escolhidos)].to_csv(index=False, sep=";").encode("utf-8-sig"),
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
