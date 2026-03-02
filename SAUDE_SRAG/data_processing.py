import logging
import os
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd
import pyreadr

from config_paths import DATA_DIR, PROCESSED_DIR

logger = logging.getLogger(__name__)


def _jenks_breaks(values: np.ndarray, n_classes: int) -> List[float]:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return [0.0] * (n_classes + 1)
    if x.size == 1:
        return [float(x[0])] * (n_classes + 1)

    x.sort()
    n = x.size
    k = max(2, int(n_classes))

    lower_class_limits = np.zeros((n + 1, k + 1), dtype=int)
    variance_combinations = np.full((n + 1, k + 1), np.inf, dtype=float)

    for i in range(1, k + 1):
        lower_class_limits[1, i] = 1
        variance_combinations[1, i] = 0.0

    for j in range(1, n + 1):
        lower_class_limits[j, 1] = 1
        variance_combinations[j, 1] = 0.0

    for l in range(2, n + 1):
        s1 = s2 = w = 0.0
        for m in range(1, l + 1):
            i3 = l - m + 1
            val = x[i3 - 1]
            w += 1.0
            s1 += val
            s2 += val * val
            variance = s2 - (s1 * s1) / w
            if i3 > 1:
                for j in range(2, k + 1):
                    if variance_combinations[l, j] >= variance + variance_combinations[i3 - 1, j - 1]:
                        lower_class_limits[l, j] = i3
                        variance_combinations[l, j] = variance + variance_combinations[i3 - 1, j - 1]

        lower_class_limits[l, 1] = 1
        variance_combinations[l, 1] = variance

    breaks = [0.0] * (k + 1)
    breaks[k] = float(x[-1])
    breaks[0] = float(x[0])

    count_num = k
    idx = n
    while count_num > 1:
        idxt = lower_class_limits[idx, count_num] - 1
        breaks[count_num - 1] = float(x[idxt])
        idx = lower_class_limits[idx, count_num] - 1
        count_num -= 1

    for i in range(1, len(breaks)):
        if breaks[i] < breaks[i - 1]:
            breaks[i] = breaks[i - 1]
    return breaks


def _compute_thresholds(values: np.ndarray) -> Dict[str, float]:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return {"sem_risco": 0.0, "seguranca": 0.0, "baixo": 0.0, "moderado": 0.0, "alto": 0.0}

    if x.size < 5:
        qs = np.quantile(x, [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        brks = [float(v) for v in qs]
    else:
        brks = _jenks_breaks(x, n_classes=5)

    return {
        "sem_risco": float(brks[0]),
        "seguranca": float(brks[1]),
        "baixo": float(brks[2]),
        "moderado": float(brks[3]),
        "alto": float(brks[4]),
    }


@dataclass(frozen=True)
class SRAGData:
    series: pd.DataFrame
    rms: List[str]
    anos: List[int]
    thresholds_by_rm: Dict[str, Dict[str, float]]


class DataProcessor:
    def __init__(
        self,
        data_filename: str = "RM_banco_SRAG.RDATA",
        processed_filename: str = "srag_monthly.parquet",
    ):
        self.data_path = os.path.join(DATA_DIR, data_filename)
        self.processed_path = os.path.join(PROCESSED_DIR, processed_filename)

    def load(self) -> SRAGData:
        if os.path.exists(self.processed_path):
            serie = pd.read_parquet(self.processed_path, engine="pyarrow")
        else:
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(
                    "Dados SRAG não encontrados. Opções:\n"
                    f"- (recomendado) gere `{os.path.basename(self.processed_path)}` em `{PROCESSED_DIR}`\n"
                    f"- ou coloque `{os.path.basename(self.data_path)}` em `{DATA_DIR}`\n"
                )

            r = pyreadr.read_r(self.data_path)
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
            serie["data"] = pd.to_datetime(
                dict(year=serie["ano"], month=serie["mes"], day=1),
                errors="coerce",
            )
            serie = serie.dropna(subset=["data"]).sort_values(["RM", "data"])

            try:
                os.makedirs(PROCESSED_DIR, exist_ok=True)
                serie.to_parquet(self.processed_path, index=False, engine="pyarrow")
            except Exception as e:
                logger.warning("Não foi possível salvar parquet SRAG agregado: %s", e)

        # Limita aos anos de interesse (2019–2024) para evitar anos espúrios
        if "ano" in serie.columns:
            serie = serie[(serie["ano"] >= 2019) & (serie["ano"] <= 2024)]

        required = {"RM", "ano", "mes", "casos_totais"}
        missing = required - set(serie.columns)
        if missing:
            raise ValueError(f"Parquet/agregado de SRAG inválido. Colunas faltando: {sorted(missing)}")

        if "data" not in serie.columns:
            serie["data"] = pd.to_datetime(
                dict(year=serie["ano"], month=serie["mes"], day=1),
                errors="coerce",
            )
        serie = serie.dropna(subset=["data"]).sort_values(["RM", "data"])

        rms = sorted(serie["RM"].unique().tolist())
        anos = sorted(serie["ano"].unique().tolist())

        thresholds_by_rm: Dict[str, Dict[str, float]] = {}
        for rm, grp in serie.groupby("RM"):
            thresholds_by_rm[rm] = _compute_thresholds(grp["casos_totais"].to_numpy())

        return SRAGData(series=serie, rms=rms, anos=anos, thresholds_by_rm=thresholds_by_rm)

