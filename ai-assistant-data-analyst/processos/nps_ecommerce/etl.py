"""ETL consolidado da base NPS do e-commerce.

Uso:
    python processos/nps_ecommerce/etl.py --input-dir dados_brutos --output-csv dados_tratados/nps_ecommerce_tratado.csv

O script le todos os arquivos nps_ecommerce_YYYY-MM.csv da pasta de origem,
aplica a limpeza padronizada e salva uma base historica consolidada.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

from limpeza import carregar_e_limpar


ARQUIVO_PADRAO = re.compile(r"^nps_ecommerce_(\d{4}-\d{2})\.csv$")


def descobrir_arquivos(origem: Path) -> list[Path]:
    arquivos = []
    for caminho in sorted(origem.glob("nps_ecommerce_*.csv")):
        if ARQUIVO_PADRAO.match(caminho.name):
            arquivos.append(caminho)
    return arquivos


def validar_mes_do_arquivo(df: pd.DataFrame, arquivo: Path) -> None:
    match = ARQUIVO_PADRAO.match(arquivo.name)
    if not match:
        raise ValueError(f"Nome de arquivo invalido: {arquivo.name}")

    mes_arquivo = match.group(1)
    meses = set(df["mes_referencia"].astype(str).unique())
    if meses != {mes_arquivo}:
        raise ValueError(
            f"{arquivo.name} contem datas fora do mes esperado. "
            f"Esperado {mes_arquivo}, encontrado {sorted(meses)}"
        )


def consolidar_arquivos(arquivos: list[Path]) -> tuple[pd.DataFrame, list[dict]]:
    tabelas = []
    resumo_execucao = []

    for arquivo in arquivos:
        df, resumo = carregar_e_limpar(arquivo)
        validar_mes_do_arquivo(df, arquivo)
        df["arquivo_origem"] = arquivo.name
        tabelas.append(df)
        resumo_execucao.append(resumo)

    if not tabelas:
        raise ValueError("Nenhum arquivo NPS foi encontrado para processamento.")

    consolidado = pd.concat(tabelas, ignore_index=True)
    consolidado = consolidado.sort_values(["mes_referencia", "data_avaliacao", "id_avaliacao"]).reset_index(drop=True)
    return consolidado, resumo_execucao


def validar_consolidado(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("A base consolidada ficou vazia.")
    if df.duplicated(subset=["id_avaliacao"]).any():
        raise ValueError("A base consolidada ainda possui id_avaliacao duplicado.")
    if df["mes_referencia"].isna().any():
        raise ValueError("A base consolidada possui mes_referencia nulo.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Consolida o historico mensal da base NPS.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("dados_brutos"),
        help="Pasta com os CSVs brutos",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("dados_tratados") / "nps_ecommerce_tratado.csv",
        help="Arquivo consolidado de saida",
    )
    args = parser.parse_args()

    arquivos = descobrir_arquivos(args.input_dir)
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo encontrado em {args.input_dir}")

    consolidado, resumo_execucao = consolidar_arquivos(arquivos)
    validar_consolidado(consolidado)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    consolidado.to_csv(args.output_csv, sep=";", index=False, encoding="utf-8-sig")

    resumo = {
        "arquivos_processados": [arquivo.name for arquivo in arquivos],
        "linhas_totais": int(len(consolidado)),
        "meses": sorted(consolidado["mes_referencia"].astype(str).unique().tolist()),
        "periodo_inicio": str(consolidado["data_avaliacao"].min()),
        "periodo_fim": str(consolidado["data_avaliacao"].max()),
    }

    print("ETL concluido.")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    print(json.dumps(resumo_execucao, ensure_ascii=False, indent=2))
    print(f"Base consolidada salva em: {args.output_csv}")


if __name__ == "__main__":
    main()
