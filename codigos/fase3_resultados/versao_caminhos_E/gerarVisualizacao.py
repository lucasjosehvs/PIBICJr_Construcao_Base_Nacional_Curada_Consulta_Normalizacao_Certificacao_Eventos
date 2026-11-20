#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projeto Lattes - Eventos: gera gráficos, mapas (Brasil e Mundo) e tabelas
a partir dos CSVs do projeto.

Uso:
    pip install pandas matplotlib geopandas plotly openpyxl
    python gerarVisualizacao.py                      # usa a pasta padrão abaixo
    python gerarVisualizacao.py --entrada D:/outra --saida D:/outra

Estrutura da saída:
    saida/graficos/   PNGs para relatório / slides / artigo
    saida/mapas/      PNGs (estáticos) + HTMLs (interativos, para site)
    saida/tabelas/    Excel formatado + CSVs prontos para Datawrapper/Flourish
"""
import argparse
import json
import textwrap
import urllib.request
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Configuração visual (paleta Okabe-Ito: segura para daltônicos)
# ----------------------------------------------------------------------------
AZUL, LARANJA, VERDE, VERMELHO, CINZA = "#0072B2", "#E69F00", "#009E73", "#D55E00", "#8C8C8C"
PALETA_EVENTOS = [AZUL, LARANJA, VERDE, VERMELHO, "#CC79A7", "#56B4E9", "#F0E442", "#7F7F7F"]

plt.rcParams.update({
    "figure.dpi": 100, "savefig.dpi": 200, "savefig.bbox": "tight",
    "font.size": 11, "axes.titlesize": 15, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25,
    "axes.axisbelow": True,
})

# Pasta padrão: os CSVs estão nela e os resultados também são gravados nela
PASTA_PADRAO = r"E:\Magela\saidas"

URL_UF = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
URL_PAISES = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"

FONTE = "Fonte: currículos Lattes (CNPq) — processamento próprio."

# Nomes de países em português (os CSVs vêm sem acento)
NOMES_PAISES = {
    "estados unidos": "Estados Unidos", "italia": "Itália", "franca": "França",
    "canada": "Canadá", "mexico": "México", "colombia": "Colômbia",
    "alemanha": "Alemanha", "reino unido": "Reino Unido", "africa sul": "África do Sul",
    "paises baixos": "Países Baixos", "holanda": "Países Baixos", "belgica": "Bélgica",
    "suica": "Suíça", "austria": "Áustria", "japao": "Japão", "russia": "Rússia",
}


def fmt(n, casas=0):
    """Formata número no padrão brasileiro: 1.234.567,8"""
    s: str = f"{n:,.{casas}f}"                       # ex.: 1,234,567.8
    return s.translate(str.maketrans(",.", ".,"))    # troca vírgula <-> ponto de uma vez: 1.234.567,8

def nome_pais(x):
    return NOMES_PAISES.get(x, x.title())

def localizar(pasta, nome):
    """Procura o CSV na pasta indicada e, se não achar, na subpasta 'saidas' dela."""
    base = Path(pasta)
    candidatos = [base / nome, base / "saidas" / nome]
    for c in candidatos:
        if c.exists():
            return c
    raise FileNotFoundError(f"Não encontrei '{nome}'. Procurei em:\n" + "\n".join(f"  - {c}" for c in candidatos))


def ler(pasta, nome):
    # keep_default_na=False é ESSENCIAL: senão o conjunto "NA" vira NaN no pandas
    return pd.read_csv(localizar(pasta, nome), sep=";", keep_default_na=False, encoding="utf-8")

def baixar(url, destino):
    destino = Path(destino)
    if not destino.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
        print(f"Baixando {url} ...")
        urllib.request.urlretrieve(url, destino)
    return destino


def rodape(fig, texto=FONTE, y=-0.01):
    fig.text(0.01, y, texto, fontsize=8.5, color="#666", ha="left", va="top")


# ----------------------------------------------------------------------------
# 1) Gráficos
# ----------------------------------------------------------------------------
def grafico_ano(df, saida):
    d = df.copy()
    d = d[d.ANO >= 1985]
    fig, ax = plt.subplots(figsize=(11, 5.6))
    estilos = {"NA": (AZUL, "-", "Nome + ano"), "NPA": (CINZA, "--", "Nome + país + ano"),
               "NCA": (LARANJA, "-", "Nome + cidade + ano")}
    for conj, (cor, ls, rot) in estilos.items():
        s = d[d.CONJUNTO == conj].sort_values("ANO")
        ax.plot(s.ANO, s.DISTINTOS, color=cor, ls=ls, lw=2.4, label=rot)
    # anos com dados incompletos
    ax.axvspan(2023.5, d.ANO.max() + .5, color="#999", alpha=.15, lw=0)
    ax.text(2024.5, ax.get_ylim()[1] * .55, "dados\nincompletos", rotation=90,
            ha="center", va="center", fontsize=9, color="#555")
    # pico
    na = d[d.CONJUNTO == "NA"]
    pico = na.loc[na.DISTINTOS.idxmax()]
    ax.annotate(f"Pico: {int(pico.ANO)}\n{fmt(pico.DISTINTOS)} eventos",
                (pico.ANO, pico.DISTINTOS), xytext=(pico.ANO - 14, pico.DISTINTOS * .93),
                arrowprops=dict(arrowstyle="->", color="#444"), fontsize=10)
    ax.axvline(2020, color="#444", ls=":", lw=1)
    ax.text(2019.7, ax.get_ylim()[1] * .06, "pandemia", rotation=90, ha="right", fontsize=9, color="#444")
    ax.set_title("Eventos distintos registrados no Lattes, por ano")
    ax.set_xlabel("")
    ax.set_ylabel("Eventos distintos")
    ax.yaxis.set_major_formatter(lambda v, _: fmt(v))
    ax.legend(frameon=False, loc="upper left")
    rodape(fig, FONTE + " As séries NA e NPA são praticamente idênticas.")
    fig.savefig(saida / "01_eventos_por_ano.png")
    plt.close(fig)

def grafico_top10(df, coluna_rotulo, titulo, arquivo, saida, subtitulo=""):
    d = df.sort_values("OCORRENCIAS", ascending=True).copy()
    cores_evento = {n: PALETA_EVENTOS[i % len(PALETA_EVENTOS)]
                    for i, n in enumerate(df.sort_values("OCORRENCIAS", ascending=False)["NOME-DO-EVENTO"].unique())}
    rotulos = [textwrap.fill(r, 42) for r in d[coluna_rotulo]]
    fig, ax = plt.subplots(figsize=(11, 6.2))
    barras = ax.barh(rotulos, d.OCORRENCIAS, color=[cores_evento[n] for n in d["NOME-DO-EVENTO"]])
    for b, v in zip(barras, d.OCORRENCIAS):
        ax.text(v + d.OCORRENCIAS.max() * .01, b.get_y() + b.get_height() / 2,
                fmt(v), va="center", fontsize=9.5)
    ax.set_xlim(0, d.OCORRENCIAS.max() * 1.12)
    ax.xaxis.set_major_formatter(lambda v, _: fmt(v))
    ax.set_xlabel("Ocorrências")
    ax.grid(axis="y", visible=False)
    ax.set_title(titulo, pad=26 if subtitulo else 10)
    if subtitulo:
        ax.text(0, 1.015, subtitulo, transform=ax.transAxes, fontsize=10, color="#555")
    rodape(fig)
    fig.savefig(saida / arquivo)
    plt.close(fig)

def graficos_top10(entrada, saida):
    n = ler(entrada, "top10_N.csv")
    n["rotulo"] = n["NOME-DO-EVENTO"].str.capitalize()
    grafico_top10(n, "rotulo", "10 eventos mais registrados (nome do evento)", "02a_top10_N.png", saida)

    na = ler(entrada, "top10_NA.csv")
    na["rotulo"] = na["NOME-DO-EVENTO"].str.capitalize() + " (" + na["ANO-DO-EVENTO"].astype(str) + ")"
    grafico_top10(na, "rotulo", "10 edições de eventos mais registrados (nome + ano)", "02b_top10_NA.png", saida,
                  "Cada cor é um evento; edições do mesmo evento repetem a cor")

    npa = ler(entrada, "top10_NPA.csv")
    npa["rotulo"] = (npa["NOME-DO-EVENTO"].str.capitalize() + " — " +
                     npa["PAIS-DO-EVENTO"].str.title() + " (" + npa["ANO-DO-EVENTO"].astype(str) + ")")
    grafico_top10(npa, "rotulo", "10 edições mais registrados, com país (nome + país + ano)",
                  "02d_top10_NPA.png", saida, "Cada cor é um evento; edições do mesmo evento repetem a cor")

    nca = ler(entrada, "top10_NCA.csv")
    nca["rotulo"] = (nca["NOME-DO-EVENTO"].str.capitalize() + " — " +
                     nca["CIDADE-DO-EVENTO"].str.title() + " (" + nca["ANO-DO-EVENTO"].astype(str) + ")")
    grafico_top10(nca, "rotulo", "10 edições mais registrados, com cidade (nome + cidade + ano)",
                  "02c_top10_NCA.png", saida, "Cada cor é um evento; edições do mesmo evento repetem a cor")


def grafico_faixas(df, saida):
    conjuntos = [("N", AZUL, "Nome"), ("NA", LARANJA, "Nome + ano"),
                 ("NPA", VERMELHO, "Nome + país + ano"), ("NCA", VERDE, "Nome + cidade + ano")]
    faixas = list(df[df.CONJUNTO == "N"].FAIXA)
    x = np.arange(len(faixas))
    larg = .2
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    for i, (c, cor, rot) in enumerate(conjuntos):
        s = df[df.CONJUNTO == c].set_index("FAIXA").reindex(faixas)["QTD-EVENTOS"]
        ax.bar(x + (i - 1.5) * larg, s.fillna(0), larg, color=cor, label=rot)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(faixas, rotation=35, ha="right")
    ax.set_xlabel("Faixa de ocorrências por evento")
    ax.set_ylabel("Quantidade de eventos (escala log)")
    ax.yaxis.set_major_formatter(lambda v, _: fmt(v))
    ax.set_title("Poucos eventos concentram muitos registros", pad=26)
    ax.text(0, 1.015, "Quantos eventos existem em cada faixa de número de registros", transform=ax.transAxes,
            fontsize=10, color="#555")
    ax.legend(frameon=False)
    ax.grid(axis="x", visible=False)
    rodape(fig, FONTE + " Eixo vertical em escala logarítmica (cada linha = 10x).", y=-0.09)
    fig.savefig(saida / "03_distribuicao_por_faixas.png")
    plt.close(fig)


def grafico_uf(uf, saida):
    d = uf.copy()
    d["certas"] = d.OCORRENCIAS - d["OCORRENCIAS-AMBIGUAS"]
    d = d.sort_values("certas")
    fig, ax = plt.subplots(figsize=(10, 8.5))
    ax.barh(d.ESTADO, d.certas, color=AZUL, label="Cidade identificada sem ambiguidade")
    ax.barh(d.ESTADO, d["OCORRENCIAS-AMBIGUAS"], left=d.certas, color="#BFD9EC",
            hatch="///", edgecolor="white", label="Cidade ambígua (existe em outros estados)")
    ax.xaxis.set_major_formatter(lambda v, _: fmt(v))
    ax.set_xlabel("Ocorrências de eventos")
    ax.grid(axis="y", visible=False)
    ax.set_title("Eventos por estado (UF)")
    ax.legend(frameon=False, loc="lower right")
    rodape(fig, FONTE + " Ocorrências ambíguas aparecem contadas em cada UF candidata.")
    fig.savefig(saida / "04_eventos_por_uf.png")
    plt.close(fig)


# ----------------------------------------------------------------------------
# 2) Mapas estáticos
# ----------------------------------------------------------------------------
def carregar_geo(pasta_geo):
    import geopandas as gpd
    g_uf = gpd.read_file(baixar(URL_UF, Path(pasta_geo) / "brasil_uf.geojson"))
    g_pa = gpd.read_file(baixar(URL_PAISES, Path(pasta_geo) / "paises.geojson"))
    return g_uf, g_pa


def colorbar_log(fig, ax, cmap, lo, hi, rotulo):
    """Barra de cores em escala log. lo/hi são log10 dos valores mínimo e máximo."""
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=lo, vmax=hi))
    sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, orientation="horizontal", fraction=.04, pad=.02, shrink=.8)
    cb.set_label(rotulo)
    expoentes = list(range(int(np.ceil(lo)), int(np.floor(hi)) + 1))
    cb.set_ticks(expoentes)
    cb.set_ticklabels([fmt(10 ** e) for e in expoentes])      # 1.000 / 10.000 / 100.000 ...
    return cb


def mapa_brasil_png(g_uf, uf, saida):
    d = g_uf.merge(uf, left_on="sigla", right_on="ESTADO", how="left")
    d["certas"] = d.OCORRENCIAS - d["OCORRENCIAS-AMBIGUAS"]
    d["pct_amb"] = d["OCORRENCIAS-AMBIGUAS"] / d.OCORRENCIAS * 100
    d["certas_log"] = np.log10(d.certas.clip(lower=1))          # escala log feita "na mão"
    lo, hi = float(d.certas_log.min()), float(d.certas_log.max())

    fig, axs = plt.subplots(1, 2, figsize=(15, 7.4))
    # painel A - contagem (escala log)
    cmapA = plt.get_cmap("YlGnBu")
    normA = mcolors.Normalize(vmin=lo, vmax=hi)
    d.plot(ax=axs[0], column="certas_log", cmap=cmapA, vmin=lo, vmax=hi, edgecolor="white", linewidth=.6)
    axs[0].set_title("Ocorrências com cidade identificada")
    colorbar_log(fig, axs[0], cmapA, lo, hi, "Ocorrências (escala log)")
    # painel B - % ambiguidade
    cmapB = plt.get_cmap("OrRd")
    normB = mcolors.Normalize(0, 100)
    d.plot(ax=axs[1], column="pct_amb", cmap=cmapB, norm=normB, edgecolor="white", linewidth=.6)
    axs[1].set_title("Qualidade do mapeamento")
    sm = plt.cm.ScalarMappable(cmap=cmapB, norm=normB)
    cb = fig.colorbar(sm, ax=axs[1], orientation="horizontal", fraction=.04, pad=.02, shrink=.8)
    cb.set_label("% das ocorrências da UF com cidade ambígua")
    for ax, coluna, cmap_, norm_ in zip(axs, ["certas_log", "pct_amb"], [cmapA, cmapB], [normA, normB]):
        for _, r in d.iterrows():
            p = r.geometry.representative_point()
            rgb = cmap_(norm_(r[coluna]))[:3]
            lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]     # texto branco em fundo escuro
            ax.text(p.x, p.y, r.sigla, ha="center", va="center", fontsize=8,
                    color="white" if lum < 0.5 else "#222", fontweight="bold")
        ax.set_axis_off()
    fig.subplots_adjust(top=.86, wspace=.02)
    fig.suptitle("Eventos do Lattes por estado", x=.05, y=1.0, ha="left", fontsize=17, fontweight="bold")
    rodape(fig, FONTE + " Malha: Click That Hood (derivada do IBGE). Painel A exclui cidades ambíguas para não contar duas vezes.")
    fig.savefig(saida / "05_mapa_brasil.png")
    plt.close(fig)


def mapa_mundo_png(g_pa, paises, saida):
    d = g_pa.merge(paises, left_on="ISO3166-1-Alpha-3", right_on="CODIGO-ISO3", how="left")
    d = d[d["name"] != "Antarctica"]
    sem_br = d[d["ISO3166-1-Alpha-3"] != "BRA"]
    fig, ax = plt.subplots(figsize=(14, 7.6))
    d.plot(ax=ax, color="#EEEEEE", edgecolor="white", linewidth=.3)                  # sem dados
    d[d["ISO3166-1-Alpha-3"] == "BRA"].plot(ax=ax, color="#CFCFCF", edgecolor="white", hatch="///", linewidth=.3)
    cmap = plt.get_cmap("YlOrRd")
    dados = sem_br.dropna(subset=["OCORRENCIAS"]).copy()
    dados["ocorr_log"] = np.log10(dados.OCORRENCIAS.astype(float))
    lo, hi = float(dados.ocorr_log.min()), float(dados.ocorr_log.max())
    dados.plot(ax=ax, column="ocorr_log", cmap=cmap, vmin=lo, vmax=hi, edgecolor="white", linewidth=.3)
    # rótulos dos 6 maiores, com deslocamento manual para não sobrepor (em pontos)
    desloc = {"USA": (-55, -55), "PRT": (-75, 35), "ESP": (-40, 62), "ARG": (-70, -45),
              "URY": (75, -30), "CHL": (-70, 10)}
    for _, r in dados.nlargest(6, "OCORRENCIAS").iterrows():
        c = r.geometry.representative_point()
        dx, dy = desloc.get(r["CODIGO-ISO3"], (0, 15))
        ax.annotate(nome_pais(r["PAIS-DO-EVENTO"]), (c.x, c.y), fontsize=9, ha="center",
                    xytext=(dx, dy), textcoords="offset points",
                    arrowprops=dict(arrowstyle="-", color="#555", lw=.7))
    ax.set_xlim(-170, 180)
    ax.set_ylim(-58, 84)
    colorbar_log(fig, ax, cmap, lo, hi, "Ocorrências (escala log)")
    ax.set_axis_off()
    ax.set_title("Eventos no exterior registrados por pesquisadores brasileiros")
    br = paises.loc[paises["CODIGO-ISO3"] == "BRA", "OCORRENCIAS"].iloc[0]
    ax.text(0.60, 0.02, f"Brasil (hachurado) tem {fmt(br)} ocorrências —\nomitido da escala para não achatar o mapa.",
            transform=ax.transAxes, fontsize=9, color="#444")
    rodape(fig, FONTE + " Malha: Natural Earth via datasets/geo-countries. Países sem dados em cinza-claro.")
    fig.savefig(saida / "06_mapa_mundo.png")
    plt.close(fig)


# ----------------------------------------------------------------------------
# 3) Mapas interativos (HTML) com Plotly
# ----------------------------------------------------------------------------
def mapas_interativos(g_uf, uf, paises, saida):
    import plotly.express as px

    # Brasil
    g = g_uf.copy()
    g["geometry"] = g.geometry.simplify(0.05)          # reduz tamanho do HTML
    geojson = json.loads(g[["sigla", "name", "geometry"]].to_json())
    d = uf.copy()
    d["certas"] = d.OCORRENCIAS - d["OCORRENCIAS-AMBIGUAS"]
    d["pct_amb"] = (d["OCORRENCIAS-AMBIGUAS"] / d.OCORRENCIAS * 100).round(1)
    d["log10"] = np.log10(d.certas.clip(lower=1))
    d["certas_fmt"] = d.certas.map(fmt)
    d["amb_fmt"] = d["pct_amb"].map(lambda v: fmt(v, 1) + "%")
    fig = px.choropleth(
        d, geojson=geojson, locations="ESTADO", featureidkey="properties.sigla", color="log10",
        color_continuous_scale="YlGnBu", hover_name="ESTADO",
        hover_data={"log10": False, "ESTADO": False, "certas_fmt": True, "amb_fmt": True},
        labels={"certas_fmt": "Ocorrências (cidade identificada)", "amb_fmt": "% ambíguas"},
        title="Eventos do Lattes por estado")
    fig.update_geos(fitbounds="locations", visible=False)
    ticks = [3, 4, 5, 6]
    fig.update_coloraxes(colorbar=dict(title="Ocorrências", tickvals=ticks,
                                       ticktext=[fmt(10 ** t) for t in ticks]))
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    fig.write_html(saida / "mapa_brasil_interativo.html", include_plotlyjs="cdn")

    # Mundo (sem o Brasil, que domina a escala)
    p = paises[paises["CODIGO-ISO3"] != "BRA"].copy()
    p["pais"] = p["PAIS-DO-EVENTO"].map(nome_pais)
    p["log10"] = np.log10(p.OCORRENCIAS)
    p["oc_fmt"] = p.OCORRENCIAS.map(fmt)
    p["ev_fmt"] = p["EVENTOS-DISTINTOS"].map(fmt)
    fig = px.choropleth(
        p, locations="CODIGO-ISO3", color="log10", color_continuous_scale="YlOrRd", hover_name="pais",
        hover_data={"log10": False, "CODIGO-ISO3": False, "oc_fmt": True, "ev_fmt": True},
        labels={"oc_fmt": "Ocorrências", "ev_fmt": "Eventos distintos"},
        title="Eventos no exterior registrados por pesquisadores brasileiros (Brasil omitido)")
    fig.update_geos(projection_type="natural earth", showcountries=True, countrycolor="#FFF",
                    showland=True, landcolor="#EEE", showframe=False)
    ticks = [1, 2, 3, 4, 5]
    fig.update_coloraxes(colorbar=dict(title="Ocorrências", tickvals=ticks,
                                       ticktext=[fmt(10 ** t) for t in ticks]))
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    fig.write_html(saida / "mapa_mundo_interativo.html", include_plotlyjs="cdn")


# ----------------------------------------------------------------------------
# 4) Tabelas (Excel formatado + CSVs para ferramentas online)
# ----------------------------------------------------------------------------
def tabelas(entrada, uf, paises, saida):
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.formatting.rule import DataBarRule
    from openpyxl.utils import get_column_letter

    resumo = ler(entrada, "resumo.csv")
    mapeamento = ler(entrada, "relatorioMapeamento.csv")

    uf_t = uf.copy()
    uf_t["OCORRENCIAS-CERTAS"] = uf_t.OCORRENCIAS - uf_t["OCORRENCIAS-AMBIGUAS"]
    uf_t["% AMBIGUAS"] = (uf_t["OCORRENCIAS-AMBIGUAS"] / uf_t.OCORRENCIAS * 100).round(1)
    uf_t = uf_t.sort_values("OCORRENCIAS-CERTAS", ascending=False)

    pa_t = paises.copy()
    pa_t["PAIS"] = pa_t["PAIS-DO-EVENTO"].map(nome_pais)
    pa_t = pa_t[["PAIS", "CODIGO-ISO3", "OCORRENCIAS", "EVENTOS-DISTINTOS", "ANO-MIN", "ANO-MAX"]]

    top = {}
    for k in ["N", "NA", "NCA", "NPA"]:
        t = ler(entrada, f"top10_{k}.csv")
        t["NOME-DO-EVENTO"] = t["NOME-DO-EVENTO"].str.capitalize()
        top[f"Top10_{k}"] = t

    cab_fill = PatternFill("solid", fgColor="0072B2")
    with pd.ExcelWriter(saida / "tabelas_formatadas.xlsx", engine="openpyxl") as xw:
        abas = {"Resumo": resumo, "Mapeamento": mapeamento, "UF": uf_t, "Paises": pa_t, **top}
        for nome, df in abas.items():
            df.to_excel(xw, sheet_name=nome, index=False)
            ws = xw.sheets[nome]
            ws.freeze_panes = "A2"
            for c in ws[1]:
                c.font = Font(bold=True, color="FFFFFF")
                c.fill = cab_fill
                c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            for i, col in enumerate(df.columns, start=1):
                larg = max(len(str(col)), df[col].astype(str).str.len().max()) + 3
                ws.column_dimensions[get_column_letter(i)].width = min(larg, 60)
                if pd.api.types.is_integer_dtype(df[col]) and "ANO" not in str(col):
                    for cel in ws[get_column_letter(i)][1:]:
                        cel.number_format = "#,##0"
                if str(col) in ("OCORRENCIAS", "OCORRENCIAS-CERTAS"):
                    ws.conditional_formatting.add(
                        f"{get_column_letter(i)}2:{get_column_letter(i)}{len(df) + 1}",
                        DataBarRule(start_type="min", end_type="max", color="9CC3E6"))
    # CSVs (separador vírgula, ponto decimal) prontos para Datawrapper / Flourish
    uf_dw = uf_t.rename(columns={"ESTADO": "UF"})[["UF", "OCORRENCIAS-CERTAS", "% AMBIGUAS", "EVENTOS-DISTINTOS"]]
    uf_dw.to_csv(saida / "para_datawrapper_uf.csv", index=False, encoding="utf-8")
    pa_t.to_csv(saida / "para_datawrapper_paises.csv", index=False, encoding="utf-8")


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default=PASTA_PADRAO, help="pasta com os CSVs")
    ap.add_argument("--saida", default=PASTA_PADRAO, help="pasta onde serão criadas graficos/, mapas/ e tabelas/")
    ap.add_argument("--geo", default=None, help="pasta de cache dos GeoJSON (padrão: <saida>/geo)")
    a = ap.parse_args()

    out = Path(a.saida)
    g_dir, m_dir, t_dir = out / "graficos", out / "mapas", out / "tabelas"
    for p in (g_dir, m_dir, t_dir):
        p.mkdir(parents=True, exist_ok=True)

    ano = ler(a.entrada, "eventosPorAno.csv")
    faixas = ler(a.entrada, "eventosPorFaixas.csv")
    uf = ler(a.entrada, "eventosPorUF.csv")
    paises = ler(a.entrada, "eventosPorPais.csv")

    grafico_ano(ano, g_dir)
    graficos_top10(a.entrada, g_dir)
    grafico_faixas(faixas, g_dir)
    grafico_uf(uf, g_dir)

    g_uf, g_pa = carregar_geo(a.geo or out / "geo")
    mapa_brasil_png(g_uf, uf, m_dir)
    mapa_mundo_png(g_pa, paises, m_dir)
    mapas_interativos(g_uf, uf, paises, m_dir)
    tabelas(a.entrada, uf, paises, t_dir)
    print("Pronto! Veja a pasta:", out.resolve())


if __name__ == "__main__":
    main()