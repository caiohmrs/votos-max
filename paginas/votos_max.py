"""Página 1 — Votos do Max por local de votação (só os votos do Max).

Colunas: zona, RA, escola e votos do Max.
Modos de visualização: Tabela (padrão), Cartões (bom no celular) e Ranking em gráfico.
Os números de contexto (eleitores, abstenções, brancos, nulos) ficam na página Comparação.
"""
import html

import altair as alt
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dados import filtros, locais, n

AMARELO = "#f59e0b"

df = locais()
f = filtros(df, "max")

st.title("Votação do Max Maciel 50100 — Deputado Distrital (DF)")
st.caption("Eleições 2026 · votos por local de votação (arquivos de urna do TSE)")

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
        radius=5, color="#b45309", weight=1.5, fill=True, fillColor=AMARELO, fillOpacity=0.85,
        tooltip=f"{r['escola'].title()} — {n(r['votos_max'])} votos", popup=popup,
    ).add_to(m)
# use_container_width garante que o mapa caiba na largura da tela (o padrão de 500px estourava no celular)
st_folium(m, height=440, use_container_width=True, returned_objects=[])

# ------------------------------------------------------------------ lista
st.divider()
st.subheader("Locais por votos do Max")
st.caption("Ordenado do maior para o menor — nada é escondido, aparecem os 622 locais "
           "(filtrados só pelo que você escolher na lateral).")

rank = (f[["zona", "ra", "escola", "votos_max"]]
        .rename(columns={"ra": "RA", "votos_max": "Max"})
        .sort_values("Max", ascending=False)
        .reset_index(drop=True))

modo = st.radio(
    "Como ver", ["Tabela", "Cartões (celular)", "Ranking em gráfico"],
    horizontal=True, key="max_modo",
)

if modo == "Tabela":
    # sem largura fixa por coluna: no celular a tabela encolhe e rola em vez de ser cortada
    st.dataframe(rank, hide_index=True, width="stretch", height=560)

elif modo == "Cartões (celular)":
    quantos = st.slider("Quantos locais mostrar", 10, max(10, len(rank)), min(50, max(10, len(rank))), step=10)
    partes = []
    for _, r in rank.head(quantos).iterrows():
        partes.append(
            f'<div style="display:flex;align-items:center;gap:12px;padding:10px 12px;margin-bottom:6px;'
            f'border:1px solid rgba(128,128,128,.28);border-radius:10px">'
            f'<div style="flex:1;min-width:0">'
            f'<div style="font-weight:600;line-height:1.25;overflow-wrap:anywhere">{html.escape(str(r["escola"]))}</div>'
            f'<div style="font-size:12px;opacity:.65">{html.escape(str(r["RA"]))} · zona {int(r["zona"])}</div>'
            f'</div>'
            f'<div style="font-weight:700;font-size:19px;white-space:nowrap">{n(r["Max"])}</div>'
            f'</div>'
        )
    st.markdown("".join(partes), unsafe_allow_html=True)

else:
    quantos = st.slider("Quantos locais mostrar no gráfico", 10, min(200, max(20, len(rank))), 30, step=10)
    top = rank.head(quantos)
    base = alt.Chart(top).encode(
        y=alt.Y("escola:N", sort="-x", title=None, axis=alt.Axis(labelLimit=300)),
        x=alt.X("Max:Q", title="votos do Max"),
    )
    barras = base.mark_bar(color=AMARELO, cornerRadiusEnd=3).encode(
        tooltip=[alt.Tooltip("escola:N", title="escola"), alt.Tooltip("RA:N", title="RA"),
                 alt.Tooltip("zona:N", title="zona"), alt.Tooltip("Max:Q", title="votos do Max")],
    )
    valores = base.mark_text(align="left", dx=4, fontSize=11, color="#888").encode(text="Max:Q")
    st.altair_chart((barras + valores).properties(height=max(320, 26 * quantos)))

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
