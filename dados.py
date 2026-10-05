"""Carregamento e filtros dos dados do painel — compartilhado pelas páginas.

Colunas de contexto (eleitores, compareceram, abstenções, brancos, nulos) ficam
disponíveis aqui, mas só são mostradas na página de Comparação.
"""
import os

import pandas as pd
import streamlit as st

AQUI = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = os.path.join(AQUI, "dados", "locais_max_2026.csv")

# números de contexto — aparecem apenas na página de Comparação
CONTEXTO = ["eleitores", "compareceram", "abstencao", "brancos", "nulos"]


@st.cache_data(show_spinner=False)
def locais() -> pd.DataFrame:
    df = pd.read_csv(ARQUIVO, sep=";", dtype={"zona": str})
    # latitude/longitude vêm no formato brasileiro ("-15,8033115")
    for c in ("latitude", "longitude"):
        df[c] = pd.to_numeric(
            df[c].astype(str).str.replace(".", "", regex=False).str.replace(",", "."), errors="coerce"
        )
    numericas = [c for c in df.columns if c.startswith("pres_")] + CONTEXTO + ["n_secoes", "local", "votos_max"]
    for c in numericas:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    return df


def presidenciáveis(df: pd.DataFrame):
    """Lista [(coluna, rótulo)] dos presidenciáveis, do mais votado para o menos."""
    cols = [c for c in df.columns if c.startswith("pres_")]
    cols.sort(key=lambda c: -int(df[c].sum()))
    return [(c, rotulo_pres(c)) for c in cols]


def rotulo_pres(coluna: str) -> str:
    """'pres_22_FLAVIO BOLSONARO' -> '22 · Flavio Bolsonaro'"""
    resto = coluna[5:]
    num, _, nome = resto.partition("_")
    return f"{num} · {nome.title()}"


def n(v) -> str:
    return f"{int(v):,}".replace(",", ".")


def filtros(df: pd.DataFrame, prefixo: str, com_presidentes: bool = False):
    """Barra lateral de filtros (manuais, nunca automáticos). Devolve o DataFrame filtrado."""
    with st.sidebar:
        st.header("Filtros")
        zonas = sorted(df["zona"].unique(), key=lambda z: int(z))
        rotulos = {z: f"zona {int(z):02d} · {df.loc[df['zona'] == z, 'ra'].iloc[0]}" for z in zonas}
        sel_z = st.multiselect("Zona / RA", zonas, format_func=lambda z: rotulos[z], key=f"{prefixo}_zonas")
        busca = st.text_input("Escola ou bairro contém", "", key=f"{prefixo}_busca")

    f = df.copy()
    if sel_z:
        f = f[f["zona"].isin(sel_z)]
    if busca.strip():
        q = busca.strip().upper()
        f = f[
            f["escola"].str.upper().str.contains(q, regex=False)
            | f["bairro"].str.upper().str.contains(q, regex=False)
        ]
    return f
