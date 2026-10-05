"""Página 1 — Votos do Max por local de votação (só os votos do Max).

Colunas: zona, RA, escola e votos do Max.
Os números de contexto (eleitores, abstenções, brancos, nulos) ficam na página Comparação.
"""
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
        max_width=290,
    )
    folium.CircleMarker(
        location=[r["latitude"], r["longitude"]],
        radius=5, color="#b45309", weight=1.5, fill=True, fillColor=AMARELO, fillOpacity=0.85,
        tooltip=f"{r['escola'].title()} — {n(r['votos_max'])} votos", popup=popup,
    ).add_to(m)
st_folium(m, height=560, width=None, returned_objects=[])

# ------------------------------------------------------------------ ranking
st.divider()
st.subheader("Locais por votos do Max")
st.caption("Ordenado do maior para o menor — nada é escondido, aparecem os 622 locais "
           "(filtrados só pelo que você escolher na lateral).")

rank = (f[["zona", "ra", "escola", "votos_max"]]
        .rename(columns={"ra": "RA", "votos_max": "Max"})
        .sort_values("Max", ascending=False)
        .reset_index(drop=True))

modo = st.radio("Como ver", ["Barras na tabela", "Ranking em gráfico"], horizontal=True, key="max_modo")

if modo == "Barras na tabela":
    maior = int(rank["Max"].max()) or 1
    st.dataframe(
        rank, hide_index=True, width="stretch", height=560,
        column_config={
            "zona": st.column_config.TextColumn("zona", width=60),
            "RA": st.column_config.TextColumn("RA", width=230),
            "escola": st.column_config.TextColumn("escola", width=520),
            "Max": st.column_config.ProgressColumn("Max", min_value=0, max_value=maior, format="%d", width=260),
        },
    )
else:
    quantos = st.slider("Quantos locais mostrar", 10, min(200, max(20, len(rank))), 30, step=10)
    top = rank.head(quantos)
    base = alt.Chart(top).encode(
        y=alt.Y("escola:N", sort="-x", title=None, axis=alt.Axis(labelLimit=330)),
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
