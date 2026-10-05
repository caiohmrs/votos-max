"""Página 1 — Votos do Max por local de votação (só os votos do Max).

Os números de contexto (eleitores, abstenções, brancos, nulos) ficam na página Comparação.
"""
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dados import filtros, locais, n

df = locais()

st.title("Votação do Max Maciel 50100 — Deputado Distrital (DF)")
st.caption("Eleições 2026 · votos por local de votação (arquivos de urna do TSE)")

f = filtros(df, "max")

k1, k2 = st.columns([1, 3])
k1.metric("Votos do Max", n(f["votos_max"].sum()))
k2.metric("Locais de votação", n(len(f)))

esq, dir_ = st.columns([1.55, 1])

with esq:
    st.subheader(f"Mapa dos locais — {n(len(f))} de {n(len(df))}")
    m = folium.Map(location=[-15.80, -47.93], zoom_start=10, tiles="OpenStreetMap", control_scale=True)
    for _, r in f.iterrows():
        if pd.isna(r["latitude"]) or pd.isna(r["longitude"]):
            continue
        popup = folium.Popup(
            f"""<div style="font-family:system-ui;font-size:12px;line-height:1.5">
            <b>{r['escola'].title()}</b><br>
            {str(r['bairro']).title()} · zona {int(r['zona'])} · local {int(r['local'])}<br>
            {str(r['endereco']).title()}<br><br>
            <b>Max: {n(r['votos_max'])} votos</b>
            </div>""",
            max_width=290,
        )
        folium.CircleMarker(
            location=[r["latitude"], r["longitude"]],
            radius=5, color="#b45309", weight=1.5, fill=True, fillColor="#f59e0b", fillOpacity=0.85,
            tooltip=f"{r['escola'].title()} — {n(r['votos_max'])} votos", popup=popup,
        ).add_to(m)
    st_folium(m, height=520, width=None, returned_objects=[])

with dir_:
    st.subheader("Top 15 locais")
    top = f.nlargest(15, "votos_max")[["escola", "bairro", "votos_max"]]
    st.dataframe(
        top.rename(columns={"escola": "escola", "bairro": "bairro", "votos_max": "Max"}),
        hide_index=True, width="stretch", height=520,
    )

st.divider()
st.subheader("Todos os locais")
st.caption("Clique no cabeçalho de uma coluna para ordenar. Baixe a lista se quiser levar para outro lugar.")

tabela = f[["zona", "ra", "local", "escola", "bairro", "votos_max"]].copy()
st.dataframe(
    tabela.rename(columns={"zona": "zona", "ra": "RA", "local": "local", "escola": "escola",
                           "bairro": "bairro", "votos_max": "Max"}),
    hide_index=True, width="stretch", height=420,
)
st.download_button(
    "Baixar CSV (locais filtrados)",
    tabela.rename(columns={"votos_max": "Max"}).to_csv(index=False, sep=";").encode("utf-8-sig"),
    "locais_max_2026.csv", "text/csv",
)

with st.expander("Observações"):
    st.markdown(
        "- Fonte: arquivos de urna (BU) publicados pelo TSE + totalização oficial (EA20) — "
        "a votação de cada local é a soma das suas seções.\n"
        "- Os votos do Max **batem exato** com a totalização oficial nas 19 zonas (92.234 em 2026).\n"
        "- Eleitores, abstenções, brancos e nulos estão na página **Comparação**."
    )
