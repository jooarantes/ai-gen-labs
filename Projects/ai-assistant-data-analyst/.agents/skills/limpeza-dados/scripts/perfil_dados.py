"""Perfil rápido de qualidade de dados para arquivos tabulares (CSV/Excel).

Uso:
    python perfil_dados.py dados.csv
    python perfil_dados.py dados.csv --sep ";" --encoding latin-1
    python perfil_dados.py planilha.xlsx --aba "Vendas"
"""
import argparse
import sys

import pandas as pd


def carregar(caminho, sep=None, encoding=None, aba=0):
    if caminho.lower().endswith((".xlsx", ".xls", ".xlsm")):
        return pd.read_excel(caminho, sheet_name=aba)
    # tenta detectar separador e encoding se não informados
    encodings = [encoding] if encoding else ["utf-8", "latin-1", "cp1252"]
    seps = [sep] if sep else [",", ";", "\t", "|"]
    erro = None
    for enc in encodings:
        for s in seps:
            try:
                df = pd.read_csv(caminho, sep=s, encoding=enc)
                if df.shape[1] > 1 or (sep and s == sep):
                    print(f"[info] lido com sep='{s}' encoding='{enc}'")
                    return df
            except Exception as e:  # noqa: BLE001
                erro = e
    raise SystemExit(f"Não consegui ler o arquivo: {erro}")


def perfilar(df):
    n = len(df)
    print("=" * 70)
    print(f"DIMENSÕES: {n} linhas x {df.shape[1]} colunas")
    dup = df.duplicated().sum()
    print(f"DUPLICATAS EXATAS: {dup} ({dup / max(n, 1):.1%})")
    print("=" * 70)

    for col in df.columns:
        s = df[col]
        nulos = s.isna().sum()
        unicos = s.nunique(dropna=True)
        print(f"\n--- {col!r} | tipo: {s.dtype} ---")
        print(f"  nulos: {nulos} ({nulos / max(n, 1):.1%}) | únicos: {unicos}")
        exemplos = s.dropna().unique()[:5]
        print(f"  exemplos: {list(exemplos)}")

        if pd.api.types.is_numeric_dtype(s) and unicos > 2:
            q1, q3 = s.quantile([0.25, 0.75])
            iqr = q3 - q1
            if iqr > 0:
                out = ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum()
                print(f"  min={s.min()} max={s.max()} média={s.mean():.2f}")
                if out:
                    print(f"  [atenção] {out} outliers (IQR)")
        elif s.dtype == object:
            amostra = s.dropna().astype(str)
            if len(amostra):
                if (amostra != amostra.str.strip()).any():
                    print("  [atenção] valores com espaços extras")
                num_like = amostra.str.match(r"^[\d.,\sR$%-]+$").mean()
                if num_like > 0.8:
                    print("  [atenção] parece numérico armazenado como texto")
                dt = pd.to_datetime(amostra, errors="coerce", dayfirst=True, format="mixed")
                if dt.notna().mean() > 0.8:
                    print("  [atenção] parece data armazenada como texto")
                # variações de caixa do mesmo valor (ex.: 'SP' vs 'sp')
                if unicos > amostra.str.lower().str.strip().nunique():
                    print("  [atenção] mesmo valor com grafias diferentes (caixa/espaços)")

    print("\n" + "=" * 70)
    print("Fim do perfil. Revise os itens marcados com [atenção].")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("arquivo")
    p.add_argument("--sep", default=None)
    p.add_argument("--encoding", default=None)
    p.add_argument("--aba", default=0)
    args = p.parse_args()
    perfilar(carregar(args.arquivo, args.sep, args.encoding, args.aba))
