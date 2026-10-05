"""Carregamento e filtros dos dados do painel — compartilhado pelas páginas.

Sem barra lateral: os filtros são desenhados na própria página.
Colunas de contexto (eleitores, compareceram, abstenções, brancos, nulos) só aparecem
na página de Comparação.
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


# ------------------------------------------------------------------ identidade visual
# paleta do app do PDAF (#ff6a00 laranja + #1f2937 grafite), que funciona nos dois temas
LARANJA = "#ff6a00"    # Max
AZUL = "#3b82f6"       # presidenciáveis
CINZA = "#94a3b8"      # abstenções, brancos, nulos

CSS = """<style>
/* faixa de título */
.faixa{background:#1f2937;border-bottom:4px solid #ff6a00;border-radius:10px;
       padding:14px 18px;margin-bottom:16px}
.faixa .t{color:#ff6a00;font-weight:800;font-size:26px;line-height:1.15}
.faixa .s{color:#ffffff;opacity:.9;font-size:14px;margin-top:2px}
/* cartões da página do Max */
.loc{margin-bottom:6px;padding:10px 12px;border:1px solid rgba(128,128,128,.32);border-radius:10px;
     display:flex;align-items:center;gap:12px}
.loc .n{flex:1;min-width:0}
.loc .n b{font-weight:600;line-height:1.25;overflow-wrap:anywhere;display:block}
.loc .n span{font-size:12px;opacity:.65}
.loc .v{font-weight:700;font-size:19px;white-space:nowrap;color:#ff6a00}
/* cartões da comparação */
.cmp{margin-bottom:8px;padding:10px 12px;border:1px solid rgba(128,128,128,.32);border-radius:10px}
.cmp .e{font-weight:600;line-height:1.25;overflow-wrap:anywhere}
.cmp .s{font-size:12px;opacity:.65;margin-bottom:2px}
.cmp .l{display:flex;align-items:center;gap:8px;margin-top:3px}
.cmp .r{flex:0 0 40%;font-size:12px;line-height:1.15;overflow-wrap:anywhere}
.cmp .b{flex:1;min-width:0}
.cmp .b i{display:block;height:9px;border-radius:5px}
.cmp .v{flex:0 0 62px;text-align:right;font-size:13px;white-space:nowrap}
.cmp .v.f{font-weight:700}
</style>"""


def cabecalho(titulo: str, subtitulo: str) -> None:
    st.markdown(
        f'{CSS}<div class="faixa"><div class="t">{titulo}</div><div class="s">{subtitulo}</div></div>',
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------ filtros na página
def seletor_zonas(df: pd.DataFrame, prefixo: str):
    """Multiselect de zona/RA desenhado na página (não na barra lateral)."""
    zonas = sorted(df["zona"].unique(), key=lambda z: int(z))
    rotulos = {z: f"zona {int(z):02d} · {df.loc[df['zona'] == z, 'ra'].iloc[0]}" for z in zonas}
    return st.multiselect(
        "Zona / RA", zonas, format_func=lambda z: rotulos[z],
        key=f"{prefixo}_zonas", placeholder="todas as zonas",
    )


def busca_escola(prefixo: str, label: str = "Buscar escola"):
    """Caixa de busca por nome de escola, desenhada na página."""
    return st.text_input(label, "", key=f"{prefixo}_busca", placeholder="digite parte do nome da escola")


def filtra(df: pd.DataFrame, zonas=None, busca: str = "") -> pd.DataFrame:
    """Filtros manuais (nunca automáticos)."""
    f = df
    if zonas:
        f = f[f["zona"].isin(zonas)]
    if busca and busca.strip():
        f = f[f["escola"].str.upper().str.contains(busca.strip().upper(), regex=False)]
    return f


def botao_pagina(rotulo: str, destino: str, key: str):
    """Botão que leva para a outra página (a navegação fica escondida)."""
    if st.button(rotulo, key=key, width="stretch"):
        st.switch_page(destino)
