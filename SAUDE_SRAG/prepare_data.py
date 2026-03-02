import argparse
import os

import pandas as pd
import pyreadr

from config_paths import DATA_DIR, PROCESSED_DIR


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera parquet mensal de SRAG a partir de RM_banco_SRAG.RDATA.")
    parser.add_argument(
        "--input",
        default=os.path.join(DATA_DIR, "RM_banco_SRAG.RDATA"),
        help="Caminho do .RDATA (default: data/RM_banco_SRAG.RDATA)",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(PROCESSED_DIR, "srag_monthly.parquet"),
        help="Caminho do parquet (default: processed/srag_monthly.parquet)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Arquivo não encontrado: {args.input}")

    r = pyreadr.read_r(args.input)
    if not r:
        raise ValueError("Não foi possível ler o .RDATA de SRAG (arquivo vazio ou corrompido).")

    df = next((obj for obj in r.values() if isinstance(obj, pd.DataFrame)), None)
    if df is None or df.empty:
        raise ValueError("Nenhum data.frame encontrado dentro do .RDATA de SRAG.")

    if "RM" not in df.columns:
        raise ValueError("Coluna RM não encontrada no banco SRAG.")

    if "DT_INTERNA" in df.columns:
        date_col = "DT_INTERNA"
    elif "DT_INTER" in df.columns:
        date_col = "DT_INTER"
    else:
        raise ValueError("Colunas de data (DT_INTERNA ou DT_INTER) não encontradas em SRAG.")

    dff = df[["RM", date_col]].copy()
    dff[date_col] = pd.to_datetime(dff[date_col], errors="coerce")
    dff = dff.dropna(subset=[date_col, "RM"])
    dff["ano"] = dff[date_col].dt.year
    dff["mes"] = dff[date_col].dt.month

    dff = dff.dropna(subset=["ano", "mes"])
    dff["ano"] = dff["ano"].astype(int)
    dff["mes"] = dff["mes"].astype(int)
    dff = dff[(dff["mes"] >= 1) & (dff["mes"] <= 12)]

    serie = (
        dff.groupby(["RM", "ano", "mes"], as_index=False)
        .size()
        .rename(columns={"size": "casos_totais"})
    )
    serie["data"] = pd.to_datetime(dict(year=serie["ano"], month=serie["mes"], day=1), errors="coerce")
    serie = serie.dropna(subset=["data"]).sort_values(["RM", "data"])

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    serie.to_parquet(args.output, index=False, engine="pyarrow")

    print(f"OK: gerado {args.output} com {len(serie)} linhas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

