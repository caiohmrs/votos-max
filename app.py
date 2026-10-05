"""Painel de consulta da votação — Max Maciel 50100 (Deputado Distrital, DF).

Tela 1: mapa dos locais de votação (bolinha fixa no local da escola) + números do Max.
Os presidenciáveis entram na Tela 2 (contraste).
"""
import os

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "dados", "locais_max_2026.csv")

st.set_page_config(page_title="Votação do Max Maciel — DF 2026", page_icon="🗳️", layout="wide")


@st.cache_data(show_spinner=False)
def carrega():
    df = pd.read_csv(DADOS, sep=";", dtype={"zona": str})
    # latitude/longitude vêm no formato brasileiro ("-15,8033115")
    for c in ("latitude", "longitude"):
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(".", "", regex=False).str.replace(",", "."), errors="coerce")
    for c in df.columns:
        if c.startswith("pres_") or c in ("n_secoes", "eleitores", "compareceram", "abstencao", "brancos", "nulos", "votos_max", "local"):
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    return df


df = carrega()
pres_cols = [c for c in df.columns if c.startswith("pres_")]


def n(v):
    return f"{int(v):,}".replace(",", ".")


# ---------------------------------------------------------------- cabeçalho
st.title("Votação do Max Maciel 50100 — Deputado Distrital (DF)")
st.caption("Eleições 2026 · votação por local de votação (arquivos de urna do TSE)")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Votos do Max", n(df["votos_max"].sum()))
k2.metric("Locais de votação", n(len(df)))
k3.metric("Abstenções", n(df["abstencao"].sum()))
k4.metric("Brancos", n(df["brancos"].sum()))
k5.metric("Nulos", n(df["nulos"].sum()))

# ---------------------------------------------------------------- barra lateral
with st.sidebar:
    st.header("Filtros")
    zonas = sorted(df["zona"].unique(), key=lambda z: int(z))
    rotulos_z = {z: f"zona {int(z):02d} · {df.loc[df['zona'] == z, 'ra'].iloc[0]}" for z in zonas}
    sel_z = st.multiselect("Zona / RA", zonas, format_func=lambda z: rotulos_z[z], default=[])
    busca = st.text_input("Escola ou bairro contém", "")
    st.divider()
    st.caption(
        "Bolinha fixa no local da escola (todas do mesmo tamanho, como você pediu). "
        "Clique numa bolinha para ver os números do local."
    )

f = df.copy()
if sel_z:
    f = f[f["zona"].isin(sel_z)]
if busca.strip():
    q = busca.strip().upper()
    f = f[f["escola"].str.upper().str.contains(q, regex=False) | f["bairro"].str.upper().str.contains(q, regex=False)]

# ---------------------------------------------------------------- mapa
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
            <b>Max: {n(r['votos_max'])} votos</b><br>
            eleitores: {n(r['eleitores'])}<br>
            abstenções: {n(r['abstencao'])}<br>
            brancos: {n(r['brancos'])} · nulos: {n(r['nulos'])}
            </div>""", max_width=290)
        folium.CircleMarker(
            location=[r["latitude"], r["longitude"]],
            radius=5, color="#b45309", weight=1.5, fill=True, fillColor="#f59e0b", fillOpacity=0.85,
            tooltip=f"{r['escola'].title()} — {n(r['votos_max'])} votos", popup=popup,
        ).add_to(m)
    st_folium(m, height=520, width=None, returned_objects=[])

with dir_:
    st.subheader("Top 15 locais")
    top = f.nlargest(15, "votos_max")[["escola", "bairro", "votos_max", "abstencao", "brancos", "nulos"]]
    st.dataframe(
        top.rename(columns={"escola": "escola", "bairro": "bairro", "votos_max": "Max",
                            "abstencao": "abstenções", "brancos": "brancos", "nulos": "nulos"}),
        hide_index=True, width="stretch", height=520,
    )

# ---------------------------------------------------------------- tabela completa
st.divider()
st.subheader("Todos os locais")
st.caption("Clique no cabeçalho de uma coluna para ordenar. Baixe a lista se quiser levar para outro lugar.")
tabela = f[["zona", "ra", "local", "escola", "bairro", "eleitores", "compareceram",
            "abstencao", "brancos", "nulos", "votos_max"]].copy()
st.dataframe(
    tabela.rename(columns={"zona": "zona", "ra": "RA", "local": "local", "escola": "escola",
                           "bairro": "bairro", "eleitores": "eleitores", "compareceram": "compareceram",
                           "abstencao": "abstenções", "brancos": "brancos", "nulos": "nulos", "votos_max": "Max"}),
    hide_index=True, width="stretch", height=420,
)
st.download_button("Baixar CSV (locais filtrados)", tabela.to_csv(index=False, sep=";").encode("utf-8-sig"),
                   "locais_max_2026.csv", "text/csv")

with st.expander("Observações sobre os dados"):
    st.markdown(
        "- Fonte: arquivos de urna (BU) publicados pelo TSE e o arquivo de totalização (EA20) — "
        "a votação de cada local é a soma das suas seções.\n"
        "- **4 zonas (6, 10, 13 e 16)** somam 10.410 votos de presidente a mais do que a totalização oficial "
        "da zona (0,6% do total do DF) — padrão de votante em trânsito/justificativa. Isso afeta as colunas "
        "de presidente, não os votos do Max, que batem exato em 19/19 zonas.\n"
        "- O candidato 28 (Leonardo Avalanche, PRTB) aparece com 57 votos nas urnas do DF mas não existe na "
        "totalização (renunciou em 30/09).\n"
        "- 2018 e 2022 ainda não entraram nesta tela."
    )
