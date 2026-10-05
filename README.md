# Painel da votação — Max Maciel 50100 (Deputado Distrital, DF)

Painel de consulta da votação do Max Maciel por **local de votação** no DF (2026),
com mapa. Feito em Streamlit para rodar no Streamlit Community Cloud e ser compartilhado
com a equipe.

## O que tem aqui

| caminho | o que é |
|---|---|
| `app.py` | o painel (Tela 1: mapa + números do Max por local) |
| `dados/locais_max_2026.csv` | 622 locais de votação do DF: escola, bairro, endereço, coordenadas, eleitores, abstenções, brancos, nulos, votos do Max e uma coluna por candidato a presidente |
| `requirements.txt` | dependências (o Streamlit Cloud instala isso sozinho) |

## Rodar na sua máquina

```bash
cd votos-max
uv venv --python 3.11 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
.venv/Scripts/python.exe -m streamlit run app.py
```

Abre em http://localhost:8501

## Publicar no Streamlit Community Cloud

1. Suba este repositório para o GitHub (`caiohmrs/votos-max`, público).
2. Entre em https://share.streamlit.io com a conta do GitHub.
3. **Create app** → repositório `caiohmrs/votos-max`, branch `main`, arquivo principal `app.py`.
4. Deploy. O link fica no formato `https://votos-max.streamlit.app` e pode ser compartilhado com a equipe.

Observação: apps do plano gratuito **hibernam** quando ninguém acessa por um tempo —
a primeira visita "acorda" o app e demora alguns segundos.

## Dados

- Fonte: arquivos de urna (BU) publicados pelo TSE + totalização oficial (EA20).
- A votação do Max bate **exato** com a totalização oficial nas 19 zonas (92.234 votos em 2026).
- Nas colunas de presidente, as zonas 6, 10, 13 e 16 somam 10.410 votos a mais que a
  totalização oficial da zona (votante em trânsito/justificativa) — 0,6% do total do DF.

## Próximos passos

- Tela 2: contraste com os presidenciáveis (votos lado a lado).
- Fase 2: agrupamentos por zona/RA/bairro, histórico 2018/2022 e ficha do local com as seções.
