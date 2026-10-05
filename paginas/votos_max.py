"""Página 1 — Votos do Max por local de votação (só os votos do Max).

Tudo na própria página (sem barra lateral): filtro de zona no topo, botão para a
comparação, mapa e a lista em cartões (padrão) ou tabela, com a busca por escola acima.
"""
import html

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dados import LARANJA, botao_pagina, busca_escola, cabecalho, filtra, locais, n, seletor_zonas

df = locais()

cabecalho("Votação do Max Maciel 50100",
          "Deputado Distrital · DF · Eleições 2026 — votos por local de votação (arquivos de urna do TSE)")

# topo: filtro de zona + botão para a comparação
c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
with c1:
    sel_z = seletor_zonas(df, "max")
with c2:
    botao_pagina("📊 Abrir a comparação", "paginas/comparacao.py", "max_ir_comp")

f = filtra(df, zonas=sel_z)

k1, k2 = st.columns([1, 3])
k1.metric("Votos do Max", n(f["votos_max"].sum()))
k2.metric("Locais de votação", n(len(f)))

# ------------------------------------------------------------------ mapa
st.subheader(f"Mapa dos locais — {n(len(f))} de {n(len(df))}")
m = folium.Map(location=[-15.80, -47.93], zoom_start=10, tiles="OpenStreetMap", control_scale=True)
for _, r in f.iterrows():
    if pd.isna(r["latitude"]) or pd.isna(r["longitude"]):
        continue
    popup = folium.Popup(
        f"""<div style="font-family:system-ui;font-size:12px;line-height:1.5">
        <b>{r['escola'].title()}</b><br>
        {str(r['bairro']).title()} · zona {int(r['zona'])}<br>
        {str(r['endereco']).title()}<br><br>
        <b>Max: {n(r['votos_max'])} votos</b>
        </div>""",
        max_width=260,
    )
    folium.CircleMarker(
        location=[r["latitude"], r["longitude"]],
        radius=5, color="#b34700", weight=1.5, fill=True, fillColor=LARANJA, fillOpacity=0.85,
        tooltip=f"{r['escola'].title()} — {n(r['votos_max'])} votos", popup=popup,
    ).add_to(m)
# use_container_width garante que o mapa caiba na largura da tela (o padrão de 500px estourava no celular)
st_folium(m, height=440, use_container_width=True, returned_objects=[])

# ------------------------------------------------------------------ lista
st.divider()
st.subheader("Locais por votos do Max")

cb, cv = st.columns([3, 2], vertical_alignment="bottom")
with cb:
    busca = busca_escola("max")
with cv:
    modo = st.radio("Como ver", ["Cartões", "Tabela"], horizontal=True, key="max_modo")

lista = filtra(f, busca=busca)
st.caption(f"Mostrando **{n(len(lista))}** de {n(len(f))} locais, do maior para o menor — "
           "a busca filtra esta lista (o mapa acima continua com a zona inteira).")

rank = (lista[["zona", "ra", "escola", "votos_max"]]
        .rename(columns={"ra": "RA", "votos_max": "Max"})
        .sort_values("Max", ascending=False)
        .reset_index(drop=True))

if modo == "Cartões":
    partes = []
    for _, r in rank.iterrows():
        partes.append(
            f'<div class="loc"><div class="n"><b>{html.escape(str(r["escola"]))}</b>'
            f'<span>{html.escape(str(r["RA"]))} · zona {int(r["zona"])}</span></div>'
            f'<div class="v">{n(r["Max"])}</div></div>'
        )
    st.markdown("".join(partes), unsafe_allow_html=True)
else:
    st.dataframe(rank, hide_index=True, width="stretch", height=560)

st.download_button(
    "Baixar CSV",
    rank.to_csv(index=False, sep=";").encode("utf-8-sig"),
    "locais_max_2026.csv", "text/csv",
)

with st.expander("Observações"):
    st.markdown(
        "- Fonte: arquivos de urna (BU) publicados pelo TSE + totalização oficial (EA20) — "
        "a votação de cada local é a soma das suas seções.\n"
        "- Os votos do Max **batem exato** com a totalização oficial nas 19 zonas (92.234 em 2026).\n"
        "- Eleitores, abstenções, brancos e nulos estão na página **Comparação**."
    )
