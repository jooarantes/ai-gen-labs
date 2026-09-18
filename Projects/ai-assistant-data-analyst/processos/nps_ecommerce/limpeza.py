"""Limpeza da base NPS do e-commerce.

Uso:
    python processos/nps_ecommerce/limpeza.py dados_brutos/nps_ecommerce_2026-04.csv saida.csv

Este modulo concentra as regras de padronizacao e validacao para a base mensal.
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd


COLUNAS_ESPERADAS = [
    "id_avaliacao",
    "data_avaliacao",
    "id_cliente",
    "nota_nps",
    "canal",
    "dispositivo",
    "categoria_compra",
    "valor_pedido",
    "uf",
    "primeiro_pedido",
]

DISPOSITIVO_MAP = {
    "android": "Android",
    "desktop": "Desktop",
    "ios": "iOS",
}
BOOL_MAP = {
    "sim": "Sim",
    "nao": "Nao",
    "yes": "Sim",
    "no": "Nao",
}


def _normalizar_texto(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df


def _ler_csv_com_fallback(caminho: Path) -> pd.DataFrame:
    tentativas = [
        {"encoding": "utf-8-sig"},
        {"encoding": "utf-8"},
        {"encoding": "latin-1"},
    ]
    ultimo_erro: Exception | None = None

    for kwargs in tentativas:
        try:
            df = pd.read_csv(caminho, **kwargs)
            if len(df.columns) == 1:
                continue
            return df
        except Exception as exc:  # pragma: no cover - erro de leitura
            ultimo_erro = exc

    try:
        return pd.read_csv(caminho, sep=";", encoding="utf-8-sig")
    except Exception as exc:  # pragma: no cover - erro de leitura
        if ultimo_erro is not None:
            raise ValueError(f"Falha ao ler {caminho.name}: {ultimo_erro}") from exc
        raise


def _validar_estrutura(df: pd.DataFrame, origem: Path) -> None:
    faltando = [col for col in COLUNAS_ESPERADAS if col not in df.columns]
    extras = [col for col in df.columns if col not in COLUNAS_ESPERADAS]

    if faltando:
        raise ValueError(f"{origem.name} esta sem as colunas obrigatorias: {faltando}")
    if extras:
        raise ValueError(f"{origem.name} possui colunas inesperadas: {extras}")


def _converter_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    datas = pd.to_datetime(df["data_avaliacao"], format="%Y-%m-%d", errors="raise")
    df["data_avaliacao"] = datas.dt.strftime("%Y-%m-%d")
    df["mes_referencia"] = datas.dt.to_period("M").astype(str)
    return df


def _converter_nota(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    nota = pd.to_numeric(df["nota_nps"], errors="raise")
    if ((nota < 0) | (nota > 10)).any():
        invalida = df.loc[(nota < 0) | (nota > 10), ["id_avaliacao", "nota_nps"]]
        raise ValueError(
            "nota_nps fora da faixa 0-10 encontrada em: "
            + ", ".join(invalida["id_avaliacao"].astype(str).tolist())
        )
    if (nota % 1 != 0).any():
        raise ValueError("nota_nps deve ser inteira.")
    df["nota_nps"] = nota.astype("Int64")
    return df


def _converter_valor(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    valores = (
        df["valor_pedido"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )
    df["valor_pedido"] = pd.to_numeric(valores, errors="raise").round(2)
    return df


def _normalizar_categoria(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["canal"] = df["canal"].astype(str).str.strip().str.lower()

    df["categoria_compra"] = df["categoria_compra"].astype(str).str.strip()
    df["categoria_compra"] = df["categoria_compra"].str.replace(r"\s+", " ", regex=True)
    df["categoria_compra"] = df["categoria_compra"].str.title()

    df["uf"] = df["uf"].astype(str).str.strip().str.upper()
    return df


def _normalizar_dispositivo(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["dispositivo"] = df["dispositivo"].fillna("Nao informado")
    df["dispositivo"] = df["dispositivo"].astype(str).str.strip()
    df["dispositivo"] = df["dispositivo"].replace({"": "Nao informado"})

    normalizado = []
    for valor in df["dispositivo"]:
        chave = _normalizar_texto(valor)
        if chave in DISPOSITIVO_MAP:
            normalizado.append(DISPOSITIVO_MAP[chave])
        elif chave in {"nao informado", "nao informada"}:
            normalizado.append("Nao informado")
        else:
            normalizado.append(str(valor).strip())
    df["dispositivo"] = normalizado
    return df


def _normalizar_primeiro_pedido(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    normalizado = []
    for valor in df["primeiro_pedido"]:
        chave = _normalizar_texto(valor)
        normalizado.append(BOOL_MAP.get(chave, str(valor).strip().title()))
    df["primeiro_pedido"] = normalizado
    return df


def limpar_dataframe(df: pd.DataFrame, origem: Path | None = None) -> tuple[pd.DataFrame, dict]:
    """Aplica as regras de tratamento da base NPS."""
    origem = origem or Path("arquivo_desconhecido.csv")
    df = _normalizar_colunas(df)
    _validar_estrutura(df, origem)

    resumo = {
        "arquivo_origem": origem.name,
        "linhas_entrada": int(len(df)),
        "duplicatas_exatas_removidas": 0,
        "dispositivos_sem_info_preenchidos": 0,
    }

    antes = len(df)
    df = df.drop_duplicates().copy()
    resumo["duplicatas_exatas_removidas"] = int(antes - len(df))

    df = _converter_data(df)
    df = _converter_nota(df)
    df = _converter_valor(df)
    df = _normalizar_categoria(df)

    dispositivos_sem_info = int(df["dispositivo"].isna().sum())
    df = _normalizar_dispositivo(df)
    resumo["dispositivos_sem_info_preenchidos"] = dispositivos_sem_info

    df = _normalizar_primeiro_pedido(df)
    df = df[
        [
            "id_avaliacao",
            "data_avaliacao",
            "mes_referencia",
            "id_cliente",
            "nota_nps",
            "canal",
            "dispositivo",
            "categoria_compra",
            "valor_pedido",
            "uf",
            "primeiro_pedido",
        ]
    ].copy()

    df = df.sort_values(["data_avaliacao", "id_avaliacao"]).reset_index(drop=True)

    _validar_dataframe(df, origem)

    resumo["linhas_saida"] = int(len(df))
    resumo["periodo_inicio"] = str(df["data_avaliacao"].min())
    resumo["periodo_fim"] = str(df["data_avaliacao"].max())
    resumo["nps_medio"] = round(float(df["nota_nps"].mean()), 2)
    return df, resumo


def _validar_dataframe(df: pd.DataFrame, origem: Path | None = None) -> None:
    origem_txt = f" em {origem.name}" if origem else ""
    obrigatorias = [
        "id_avaliacao",
        "data_avaliacao",
        "mes_referencia",
        "id_cliente",
        "nota_nps",
        "canal",
        "dispositivo",
        "categoria_compra",
        "valor_pedido",
        "uf",
        "primeiro_pedido",
    ]

    faltando = [col for col in obrigatorias if col not in df.columns]
    if faltando:
        raise ValueError(f"Base limpa com colunas faltando{origem_txt}: {faltando}")

    if df["id_avaliacao"].isna().any():
        raise ValueError(f"id_avaliacao nao pode ficar nulo{origem_txt}.")
    if df["data_avaliacao"].isna().any():
        raise ValueError(f"data_avaliacao nao pode ficar nulo{origem_txt}.")
    if df["nota_nps"].isna().any():
        raise ValueError(f"nota_nps nao pode ficar nulo{origem_txt}.")
    if df.duplicated().any():
        raise ValueError(f"A base limpa ainda possui duplicatas exatas{origem_txt}.")

    if not df["nota_nps"].between(0, 10).all():
        raise ValueError(f"nota_nps fora de faixa encontrado{origem_txt}.")
    if not pd.api.types.is_numeric_dtype(df["valor_pedido"]):
        raise ValueError(f"valor_pedido deveria ser numerico{origem_txt}.")

    allowed_bool = {"Sim", "Nao", "Nao"}
    if not set(df["primeiro_pedido"].dropna().unique()).issubset(allowed_bool):
        raise ValueError(f"primeiro_pedido possui valores inesperados{origem_txt}.")


def carregar_e_limpar(caminho: Path) -> tuple[pd.DataFrame, dict]:
    raw = _ler_csv_com_fallback(caminho)
    return limpar_dataframe(raw, origem=caminho)


def main() -> None:
    parser = argparse.ArgumentParser(description="Limpa uma base NPS do e-commerce.")
    parser.add_argument("entrada", type=Path, help="Arquivo CSV bruto de entrada")
    parser.add_argument("saida", type=Path, help="Arquivo CSV tratado de saida")
    args = parser.parse_args()

    df, resumo = carregar_e_limpar(args.entrada)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.saida, sep=";", index=False, encoding="utf-8-sig")

    print("Limpeza concluida.")
    print(resumo)
    print(f"Arquivo tratado salvo em: {args.saida}")


if __name__ == "__main__":
    main()
