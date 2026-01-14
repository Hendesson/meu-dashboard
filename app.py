import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from datetime import datetime, date
import os
from data_processing import DataProcessor
from visualization import Visualizer
from cache_manager import cache_manager
import calendar
from typing import List, Dict
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import numpy as np
try:
    import mapclassify as mc
except Exception:
    mc = None

def get_image_url(app, image_name: str) -> str:
    """
    Retorna a URL da imagem WebP se existir, caso contrário retorna a original.
    
    Args:
        app: Instância do app Dash
        image_name: Nome do arquivo de imagem
        
    Returns:
        URL da imagem (WebP ou original)
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Tenta WebP primeiro (verifica se existe na pasta images/webp)
    webp_name = os.path.splitext(image_name)[0] + '.webp'
    webp_path = os.path.join(current_dir, 'images', 'webp', webp_name)
    
    # Se WebP existe, copia para assets temporariamente ou usa caminho direto
    # Dash só serve arquivos de assets/, então vamos usar symlink ou copiar
    if os.path.exists(webp_path):
        # Cria link simbólico ou copia para assets se necessário
        assets_webp = os.path.join(current_dir, 'assets', webp_name)
        if not os.path.exists(assets_webp):
            try:
                # Tenta criar link simbólico (melhor para Windows e Linux)
                if not os.path.islink(assets_webp):
                    import shutil
                    shutil.copy2(webp_path, assets_webp)
            except Exception:
                pass
        
        if os.path.exists(assets_webp):
            return app.get_asset_url(webp_name)
    
    # Fallback para imagem original em assets
    return app.get_asset_url(image_name)

# Inicialização do app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
    ]
)
server = app.server
app.title = "Dashboard de Ondas de Calor"

# Inicialização dos processadores
data_processor = DataProcessor()
visualizer = Visualizer()

# Carregamento dos dados
df = data_processor.load_data()
cidades = data_processor.cidades
anos = data_processor.anos

# ======================
# Dados de Internações SRAG
# ======================

def _recode_rm_nome(df_raw: pd.DataFrame) -> pd.Series:
    if "RM_nome" in df_raw.columns:
        return df_raw["RM_nome"].astype(str)
    if "RM" in df_raw.columns:
        mapping = {
            "RM de Goiânia (GO)": "Goiânia",
            "RIDE do Distrito Federal e Entorno": "RIDE_DF",
            "RM de Salvador (BA)": "Salvador",
            "RM da Grande Vitória (ES)": "Grande Vitória",
            "RM de Belo Horizonte (MG)": "Belo Horizonte",
            "RM de Curitiba (PR)": "Curitiba",
            "RM de Florianópolis (SC)": "Florianópolis",
            "RM de Fortaleza (CE)": "Fortaleza",
            "RM de Manaus (AM)": "Manaus",
            "RM de Porto Alegre (RS)": "Porto Alegre",
            "RM de Porto Velho (RO)": "Porto Velho",
            "RM de Recife (PE)": "Recife",
            "RM de São Paulo (SP)": "São Paulo",
            "RM do Rio de Janeiro (RJ)": "Rio de Janeiro",
            "RM do Vale do Rio Cuiabá (MT)": "Cuiabá",
        }
        return df_raw["RM"].map(mapping).fillna(df_raw["RM"].astype(str))
    # fallback
    return pd.Series([None] * len(df_raw))


def _pt_month_levels() -> List[str]:
    return ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def load_srag_series(csv_path: str = None) -> pd.DataFrame:
    """
    Carrega dados SRAG do arquivo Parquet (prioritário) ou CSV.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Tenta Parquet primeiro
    parquet_path = os.path.join(current_dir, "processed", "RM_banco_SRAG.parquet")
    if csv_path is None:
        csv_path = os.path.join(current_dir, "RM_banco_SRAG.csv")
    
    # Tenta carregar do cache
    cache_key = f"srag_series_{os.path.getmtime(parquet_path) if os.path.exists(parquet_path) else (os.path.getmtime(csv_path) if os.path.exists(csv_path) else 0)}"
    cached_df = cache_manager.get(cache_key)
    if cached_df is not None:
        return cached_df
    
    # Tenta Parquet
    if os.path.exists(parquet_path):
        try:
            df = pd.read_parquet(parquet_path, engine='pyarrow')
            if 'data' in df.columns:
                df['data'] = pd.to_datetime(df['data'], errors='coerce')
            cache_manager.set(cache_key, df, use_joblib=True)
            return df
        except Exception as e:
            print(f"Erro ao carregar Parquet: {e}")
    
    # Fallback para CSV agregado
    agg_cache_path = os.path.join(current_dir, "RM_banco_SRAG_agg.csv")
    try:
        if os.path.exists(agg_cache_path):
            df = pd.read_csv(agg_cache_path, parse_dates=["data"], encoding="utf-8")
            cache_manager.set(cache_key, df, use_joblib=True)
            return df
    except Exception:
        pass

    if not os.path.exists(csv_path):
        return pd.DataFrame()

    usecols = [c for c in ["RM", "RM_nome", "DT_INTERNA", "DT_SIN_PRI", "mes", "ano"] if True]
    # Tipos leves
    dtype = {
        "RM": "category",
        "RM_nome": "category",
        "mes": "category",
        "ano": "Int64",
    }

    chunks = []
    try:
        for chunk in pd.read_csv(
            csv_path,
            usecols=[c for c in usecols if c in pd.read_csv(csv_path, nrows=0).columns],
            dtype=dtype,
            parse_dates=[c for c in ["DT_INTERNA", "DT_SIN_PRI"] if c in pd.read_csv(csv_path, nrows=0).columns],
            encoding="utf-8",
            chunksize=200_000,
            low_memory=True,
        ):
            # Recodifica RM_nome
            if "RM_nome" in chunk.columns and chunk["RM_nome"].notna().any():
                chunk["RM_nome"] = chunk["RM_nome"].astype(str)
            else:
                chunk["RM_nome"] = _recode_rm_nome(chunk)

            # Ano pela regra do R
            ano_series = pd.Series(pd.NA, index=chunk.index, dtype="Int64")
            if "DT_INTERNA" in chunk.columns:
                di = pd.to_datetime(chunk["DT_INTERNA"], errors="coerce")
                mask_di = di.notna() & (di.dt.year <= 2023)
                ano_series.loc[mask_di] = di.dt.year.loc[mask_di]
            else:
                di = None
            if "DT_SIN_PRI" in chunk.columns:
                ds = pd.to_datetime(chunk["DT_SIN_PRI"], errors="coerce")
                mask_ds = ds.notna() & ano_series.isna()
                ano_series.loc[mask_ds] = ds.dt.year.loc[mask_ds]
            else:
                ds = None
            if "ano" in chunk.columns:
                # Se já existir 'ano', mantém onde válido e completa onde faltou
                aexist = pd.to_numeric(chunk["ano"], errors="coerce")
                ano_series = ano_series.fillna(aexist.astype("Int64"))

            # Mês
            if "mes" in chunk.columns and chunk["mes"].notna().any():
                mes_series = chunk["mes"].astype(str)
            else:
                meses_pt = _pt_month_levels()
                base_date = di if di is not None else ds
                if base_date is None:
                    mes_series = pd.Series([None] * len(chunk))
                else:
                    mes_series = base_date.dt.month.apply(lambda m: meses_pt[m - 1] if pd.notna(m) else None)

            tmp = pd.DataFrame({
                "RM_nome": chunk["RM_nome"],
                "ano": pd.to_numeric(ano_series, errors="coerce"),
                "mes": mes_series,
            })
            tmp = tmp.dropna(subset=["RM_nome", "ano", "mes"]).copy()

            # Agrega por chunk já em contagem
            g = tmp.groupby(["RM_nome", "ano", "mes"], dropna=False).size().reset_index(name="casos_totais")
            chunks.append(g)
    except Exception:
        return pd.DataFrame()

    if not chunks:
        return pd.DataFrame()
    serie_grp = pd.concat(chunks, ignore_index=True)
    serie_grp = (
        serie_grp.groupby(["RM_nome", "ano", "mes"], as_index=False)["casos_totais"].sum()
    )

    # Monta mes_num e data
    ordem_meses = _pt_month_levels()
    serie_grp["mes"] = serie_grp["mes"].astype(str)
    serie_grp["mes_num"] = serie_grp["mes"].apply(lambda x: ordem_meses.index(x) + 1 if x in ordem_meses else np.nan)
    serie_grp = serie_grp.dropna(subset=["mes_num"]).copy()
    serie_grp["data"] = pd.to_datetime(
        serie_grp["ano"].astype(int).astype(str) + "-" + serie_grp["mes_num"].astype(int).astype(str) + "-01",
        errors="coerce"
    )

    # Salva cache para próximos carregamentos
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        serie_grp.to_csv(agg_cache_path, index=False, encoding="utf-8")
        # Também salva como Parquet
        parquet_path = os.path.join(current_dir, "processed", "RM_banco_SRAG_agg.parquet")
        os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
        serie_grp.to_parquet(parquet_path, engine='pyarrow', compression='snappy', index=False)
    except Exception:
        pass
    
    # Salva no cache em memória
    cache_key = f"srag_series_{os.path.getmtime(csv_path) if os.path.exists(csv_path) else 0}"
    cache_manager.set(cache_key, serie_grp, use_joblib=True)

    return serie_grp


def compute_thresholds_per_rm(serie_grp: pd.DataFrame) -> pd.DataFrame:
    if serie_grp is None or serie_grp.empty:
        return pd.DataFrame(columns=["RM_nome", "categoria", "valor"])
    categorias = ["sem_risco", "seguranca", "baixo", "moderado", "alto"]
    rows = []
    for rm, sub in serie_grp.groupby("RM_nome"):
        valores_unicos = np.sort(sub["casos_totais"].unique())
        epi = None
        try:
            if mc is not None and len(valores_unicos) >= 5:
                fj = mc.FisherJenks(valores_unicos, k=5)
                brks = np.array(fj.bins)
                # FisherJenks retorna 5 limites superiores; compõe 5 níveis ordenados
                epi = np.concatenate(([valores_unicos.min()], brks))
            elif len(valores_unicos) > 1:
                epi = np.quantile(valores_unicos, q=np.linspace(0, 1, 6))
            else:
                unico = valores_unicos[0] if len(valores_unicos) == 1 else 0
                epi = np.array([unico, unico, unico, unico, unico, unico])
        except Exception:
            if len(valores_unicos) > 1:
                epi = np.quantile(valores_unicos, q=np.linspace(0, 1, 6))
            else:
                unico = valores_unicos[0] if len(valores_unicos) == 1 else 0
                epi = np.array([unico, unico, unico, unico, unico, unico])

        # Mapear para categorias (usando 5 linhas correspondentes aos níveis 1..5)
        # epi possui 6 pontos (0..5 quantis). Usaremos 1..5 como níveis
        for idx, cat in enumerate(categorias, start=1):
            valor = float(epi[idx]) if idx < len(epi) else float(epi[-1])
            rows.append({"RM_nome": rm, "categoria": cat, "valor": valor})

    return pd.DataFrame(rows)


df_srag = load_srag_series()
df_srag_thresholds = compute_thresholds_per_rm(df_srag)
rm_list = sorted(df_srag["RM_nome"].unique().tolist()) if not df_srag.empty else []
anos_srag = sorted(df_srag["ano"].unique().tolist()) if not df_srag.empty else []

# ======================
# Dados de Internações SIH
# ======================

def load_sih_series(csv_path: str = None) -> pd.DataFrame:
    """
    Carrega dados SIH do arquivo Parquet (prioritário) ou CSV.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Tenta Parquet primeiro
    parquet_path = os.path.join(current_dir, "processed", "serie_SIH_final.RData.parquet")
    if csv_path is None:
        csv_path = os.path.join(current_dir, "serie_SIH_final.RData.csv")
    
    # Tenta carregar do cache
    cache_key = f"sih_series_{os.path.getmtime(parquet_path) if os.path.exists(parquet_path) else (os.path.getmtime(csv_path) if os.path.exists(csv_path) else 0)}"
    cached_df = cache_manager.get(cache_key)
    if cached_df is not None:
        return cached_df
    
    # Tenta Parquet
    if os.path.exists(parquet_path):
        try:
            df = pd.read_parquet(parquet_path, engine='pyarrow')
            if 'data' in df.columns:
                df['data'] = pd.to_datetime(df['data'], errors='coerce')
            cache_manager.set(cache_key, df, use_joblib=True)
            return df
        except Exception as e:
            print(f"Erro ao carregar Parquet: {e}")
    
    # Fallback para CSV processado
    processed_path = os.path.join(current_dir, "serie_SIH_final_processed.csv")
    try:
        if os.path.exists(processed_path):
            df = pd.read_csv(processed_path, parse_dates=["data"], encoding="utf-8", sep=",")
            cache_manager.set(cache_key, df, use_joblib=True)
            return df
    except Exception as e:
        print(f"Erro ao carregar dados processados: {e}")
    
    # Se não existir dados processados, processa agora
    print("Processando dados SIH...")
    
    if not os.path.exists(csv_path):
        print(f"Arquivo não encontrado: {csv_path}")
        return pd.DataFrame()

    try:
        # Carrega o arquivo CSV original
        df_raw = pd.read_csv(csv_path, encoding="utf-8", sep=",")
        print(f"Dados brutos carregados: {len(df_raw)} registros")
        print(f"Colunas disponíveis: {list(df_raw.columns)}")
        
        # Sempre cria grupos temáticos baseados nas comorbidades disponíveis
        # Conforme especificado pela Eucilene para monitoramento de emergências por ondas de calor
        print("Criando grupos temáticos baseados nas comorbidades...")
        
        # Primeiro, vamos agrupar por RM, ano, mes para criar séries temporais
        df_grouped = df_raw.groupby(["RM", "ano", "mes"]).agg({
            "srag_total_casos": "sum",
            "ASMA": "sum",
            "PNEUMOPATI": "sum", 
            "CARDIOPATI": "sum",
            "HEPATICA": "sum",
            "DIABETES": "sum",
            "OBESIDADE": "sum",
            "NEUROLOGIC": "sum",
            "RENAL": "sum",
            "HEMATOLOGI": "sum",
            "IMUNODEPRE": "sum",
            "SIND_DOWN": "sum",
            "PUERPERA": "sum"
        }).reset_index()
        
        # Cria grupos de diagnóstico baseados nas 3 categorias exatas especificadas pela Eucilene
        # Conforme definido para monitoramento de emergências hospitalares por ondas de calor
        diagnostic_groups = {
            "Internações de emergências por Doenças Cardíacas, Respiratórias, Renais e Distúrbios da Regulação Térmica": [
                "CARDIOPATI", "HEPATICA", "ASMA", "PNEUMOPATI", "RENAL", "DIABETES", "OBESIDADE", "NEUROLOGIC"
            ],
            "Internações de emergência por Desidratação, Transtornos Hidroeletrolíticos e Exposição a Calor Extremo": [
                "HEMATOLOGI", "IMUNODEPRE"  # Representando E860, E871, X30, T673, T675
            ],
            "Internações por Doenças Respiratórias Agudas e Crônicas em Serviços de Emergência": [
                "SIND_DOWN", "PUERPERA"  # Representando J00-J99 do CID-10
            ]
        }
        
        # Processa os dados para criar séries temporais por grupo
        processed_data = []
        
        # Cria séries para cada grupo de diagnóstico
        for group_name, columns in diagnostic_groups.items():
            # Soma as colunas relevantes para este grupo
            available_cols = [col for col in columns if col in df_grouped.columns]
            
            if available_cols:
                # Soma os casos para este grupo
                group_cases = df_grouped[available_cols].sum(axis=1)
                
                # Cria DataFrame para este grupo
                group_df = df_grouped[["RM", "ano", "mes"]].copy()
                group_df["grupo"] = group_name
                group_df["casos_totais"] = group_cases
                
                processed_data.append(group_df)
        
        # Adiciona também o grupo total
        total_df = df_grouped[["RM", "ano", "mes"]].copy()
        total_df["grupo"] = "Total_SRAG"
        total_df["casos_totais"] = df_grouped["srag_total_casos"]
        processed_data.append(total_df)
        
        # Combina todos os dados
        df_final = pd.concat(processed_data, ignore_index=True)
        
        # Processa meses - replicando exatamente o código R
        lvl_pt = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
        
        # Converte mes para formato padrão
        if "mes" in df_final.columns:
            mes_col = df_final["mes"].astype(str).str.lower()
            # Se vier como número, converte para nome
            if mes_col.str.isdigit().any():
                mes_col = pd.to_numeric(mes_col, errors="coerce").apply(
                    lambda x: lvl_pt[int(x)-1] if pd.notna(x) and 1 <= x <= 12 else None
                )
        else:
            print("Coluna 'mes' não encontrada")
            return pd.DataFrame()
        
        df_final["mes"] = mes_col
        
        # Cria mes_num e data - replicando o código R
        df_final["mes_num"] = df_final["mes"].apply(lambda x: lvl_pt.index(x) + 1 if x in lvl_pt else np.nan)
        df_final = df_final.dropna(subset=["mes_num"]).copy()
        
        # Usa ano_inter se disponível, senão usa ano
        if "ano_inter" in df_final.columns:
            df_final["data"] = pd.to_datetime(
                df_final["ano_inter"].astype(int).astype(str) + "-" + df_final["mes_num"].astype(int).astype(str) + "-01",
                errors="coerce"
            )
        else:
            df_final["data"] = pd.to_datetime(
                df_final["ano"].astype(int).astype(str) + "-" + df_final["mes_num"].astype(int).astype(str) + "-01",
                errors="coerce"
            )
        
        df_final = df_final.dropna(subset=["data"]).copy()
        
        # Remove registros com casos_totais = 0
        df_final = df_final[df_final["casos_totais"] > 0].copy()
        
        # Ordena como no código R
        df_final = df_final.sort_values(["RM", "grupo", "data"]).reset_index(drop=True)
        
        print(f"Dados SIH processados: {len(df_final)} registros")
        print(f"Grupos criados: {df_final['grupo'].unique()}")
        print(f"RMs disponíveis: {df_final['RM'].unique()}")
        
        # Salva o arquivo processado
        try:
            df_final.to_csv(processed_path, index=False, encoding="utf-8")
            print(f"Dados processados salvos em: {processed_path}")
        except Exception as e:
            print(f"Erro ao salvar dados processados: {e}")
        
        return df_final
        
    except Exception as e:
        print(f"Erro ao processar dados SIH: {e}")
        return pd.DataFrame()


def format_rm_name(rm_name: str) -> str:
    """
    Formata o nome da RM removendo underscores e capitalizando corretamente
    """
    if not rm_name:
        return rm_name
    
    # Remove underscores e substitui por espaços
    formatted = rm_name.replace("_", " ")
    
    # Corrige problemas de codificação comuns
    formatted = formatted.replace("Ã³", "ó")
    formatted = formatted.replace("Ã¡", "á")
    formatted = formatted.replace("Ã©", "é")
    formatted = formatted.replace("Ã­", "í")
    formatted = formatted.replace("Ãº", "ú")
    formatted = formatted.replace("Ã§", "ç")
    formatted = formatted.replace("Ã¢", "â")
    formatted = formatted.replace("Ãª", "ê")
    formatted = formatted.replace("Ã´", "ô")
    formatted = formatted.replace("Ã ", "ã")
    
    # Capitaliza cada palavra
    formatted = formatted.title()
    
    # Correções específicas para nomes conhecidos
    corrections = {
        "Ride Df": "RIDE DF",
        "Ride_DF": "RIDE DF",
        "Ride DF": "RIDE DF",
        "Grande Vitoria": "Grande Vitória",
        "Grande Vitória": "Grande Vitória",
        "São Paulo": "São Paulo",
        "Rio De Janeiro": "Rio de Janeiro",
        "Belo Horizonte": "Belo Horizonte",
        "Porto Alegre": "Porto Alegre",
        "Fortaleza": "Fortaleza",
        "Salvador": "Salvador",
        "Recife": "Recife",
        "Manaus": "Manaus",
        "Goiânia": "Goiânia",
        "Cuiabá": "Cuiabá",
        "Porto Velho": "Porto Velho",
        "Curitiba": "Curitiba",
        "Florianópolis": "Florianópolis",
        "Florianapolis": "Florianópolis",
        "Floriana": "Florianópolis"
    }
    
    return corrections.get(formatted, formatted)


def fisher_jenks_breaks_strict(v: np.ndarray, k: int = 5) -> np.ndarray:
    """
    Implementa Fisher-Jenks breaks conforme código R fornecido pela Eucilene
    """
    v = np.asarray(v, dtype=float)
    v = v[np.isfinite(v)]
    u = np.unique(v)
    
    if u.size < k:
        raise ValueError(f"Fisher–Jenks exige ≥{k} valores únicos, encontrados {u.size}")
    
    if mc is not None:
        fj = mc.FisherJenks(v, k=k)
        return np.array(fj.bins)
    else:
        # Fallback para quantis se mapclassify não estiver disponível
        return np.quantile(v, q=np.linspace(0, 1, k+1))[1:k+1]


def compute_sih_thresholds_per_rm_grupo(serie: pd.DataFrame) -> pd.DataFrame:
    if serie is None or serie.empty:
        return pd.DataFrame(columns=["RM", "grupo", "categoria", "valor"])
    
    categorias = ["sem_risco", "seguranca", "baixo", "moderado", "alto"]
    rows = []
    
    for (rm, grupo), sub in serie.groupby(["RM", "grupo"]):
        valores_unicos = np.sort(sub["casos_totais"].unique())
        epi = None
        
        try:
            # Implementa exatamente como no código R fornecido pela Eucilene
            if len(valores_unicos) >= 5:
                # Usa Fisher-Jenks se >= 5 valores únicos
                epi = fisher_jenks_breaks_strict(valores_unicos, k=5)
            elif len(valores_unicos) > 1:
                # Fallback: quantis como no código R
                epi = np.quantile(valores_unicos, q=np.linspace(0, 1, 6))[1:6]  # Pega os 5 valores do meio
            else:
                # Se só tem 1 valor único
                unico = valores_unicos[0] if len(valores_unicos) == 1 else 0
                epi = np.array([unico, unico, unico, unico, unico])
        except Exception as e:
            print(f"Erro ao calcular limiares para {rm} - {grupo}: {e}")
            # Fallback em caso de erro
            if len(valores_unicos) > 1:
                epi = np.quantile(valores_unicos, q=np.linspace(0, 1, 6))[1:6]
            else:
                unico = valores_unicos[0] if len(valores_unicos) == 1 else 0
                epi = np.array([unico, unico, unico, unico, unico])

        # Mapear para categorias (usando 5 linhas correspondentes aos níveis 1..5)
        # epi possui 5 pontos. Usaremos cada um como nível
        for idx, cat in enumerate(categorias):
            valor = float(epi[idx]) if idx < len(epi) else float(epi[-1])
            rows.append({"RM": rm, "grupo": grupo, "categoria": cat, "valor": valor})

    return pd.DataFrame(rows)


# Carrega dados SIH
try:
    df_sih = load_sih_series()
    print(f"Dados SIH carregados: {len(df_sih)} registros")
    if not df_sih.empty:
        print(f"RMs disponíveis: {df_sih['RM'].nunique()}")
        print(f"Anos disponíveis: {sorted(df_sih['ano'].unique())}")
    df_sih_thresholds = compute_sih_thresholds_per_rm_grupo(df_sih)
    rm_list_sih = sorted(df_sih["RM"].unique().tolist()) if not df_sih.empty else []
    grupos_list_sih = sorted(df_sih["grupo"].unique().tolist()) if not df_sih.empty else []
except Exception as e:
    print(f"Erro ao carregar dados SIH: {e}")
    df_sih = pd.DataFrame()
    df_sih_thresholds = pd.DataFrame()
    rm_list_sih = []
    grupos_list_sih = []


def create_calendar_component(dias_calor: List[date], ano: int, mes: int, cidade: str) -> html.Div:
    """
    Cria um componente de calendário com os dias de ondas de calor destacados.
    
    Args:
        dias_calor: Lista de datas com ondas de calor
        ano: Ano do calendário
        mes: Mês do calendário
        cidade: Nome da cidade
        
    Returns:
        Componente de calendário
    """
    cal = calendar.monthcalendar(ano, mes)
    month_name = calendar.month_name[mes]
    
    # Cria o cabeçalho do calendário
    header = html.Div([
        html.H4(f"{month_name} {ano}", className="text-center mb-3"),
        html.Div([
            html.Div(day, className="text-center fw-bold")
            for day in ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        ], className="d-flex justify-content-between mb-2")
    ])
    
    # Função para determinar a cor baseada na intensidade
    def get_intensity_color(intensity):
        if pd.isna(intensity):
            return "#e63946"  # Cor padrão se não houver intensidade
        
        intensity = str(intensity).strip().lower()
        if intensity == "low-intensity":
            return "#ff9f1c"  # Laranja claro
        elif intensity == "severe":
            return "#e63946"  # Vermelho médio
        elif intensity == "extreme":
            return "#dc2f3d"  # Vermelho escuro
        else:
            return "#e63946"  # Cor padrão para outros casos
    
    # Cria as semanas do calendário
    weeks = []
    for week in cal:
        week_divs = []
        for day in week:
            if day == 0:
                # Dia vazio
                week_divs.append(html.Div("", className="calendar-day"))
            else:
                current_date = date(ano, mes, day)
                is_heat_wave = current_date in dias_calor
                
                # Obtém os dados do dia se for onda de calor
                if is_heat_wave:
                    dia_data = df[
                        (df["cidade"] == cidade) & 
                        (df["index"].dt.date == current_date)
                    ].iloc[0]
                    
                    # Obtém a cor baseada na intensidade
                    intensity_color = get_intensity_color(dia_data['HWDay_Intensity'])
                    
                    # Cria o conteúdo do popup
                    popup_content = html.Div([
                        html.H5(f"Dia {day}/{mes}/{ano}", className="text-center mb-3"),
                        html.P(f"Intensidade da Onda de Calor: {dia_data['HW_Intensity']}", className="mb-2"),
                        html.P(f"Intensidade do Dia de Onda de Calor: {dia_data['HWDay_Intensity']}", className="mb-2"),
                        html.P(f"Temperatura Máxima: {dia_data['tempMax']}°C", className="mb-2"),
                        html.P(f"Temperatura Média: {dia_data['tempMed']}°C", className="mb-2"),
                        html.P(f"Temperatura Mínima: {dia_data['tempMin']}°C", className="mb-2"),
                        html.P(f"Umidade Média: {dia_data['HumidadeMed']}%", className="mb-2")
                    ], className="p-3")
                    
                    # Cria o botão com o popup
                    day_button = dbc.Button(
                        str(day),
                        id={"type": "calendar-day", "index": f"{ano}-{mes}-{day}"},
                        className="calendar-day heat-wave",
                        style={
                            "backgroundColor": intensity_color,
                            "color": "white",
                            "borderRadius": "50%",
                            "width": "40px",
                            "height": "40px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "margin": "2px",
                            "border": "none",
                            "padding": "0"
                        }
                    )
                    
                    # Adiciona o popup ao botão
                    day_div = html.Div([
                        day_button,
                        dbc.Popover(
                            popup_content,
                            target={"type": "calendar-day", "index": f"{ano}-{mes}-{day}"},
                            trigger="click",
                            placement="top",
                            className="popover-custom"
                        )
                    ])
                else:
                    day_div = html.Div(
                        str(day),
                        className="calendar-day",
                        style={
                            "backgroundColor": "transparent",
                            "color": "black",
                            "borderRadius": "50%",
                            "width": "40px",
                            "height": "40px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "margin": "2px"
                        }
                    )
                
                week_divs.append(day_div)
                
        weeks.append(
            html.Div(week_divs, className="d-flex justify-content-between mb-2")
        )
    
    return html.Div([
        header,
        html.Div(weeks, className="calendar-body")
    ], className="calendar-container p-3", style={
        "backgroundColor": "white",
        "borderRadius": "10px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
    })

# Layout do app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Img(src=app.get_asset_url('geocalor.png'), className="logo-img"),
            html.H2("Dashboard de Ondas de Calor", className="text-center my-4")
        ], width=12)
    ], align="center"),
    dcc.Tabs([
        dcc.Tab(label="Início", children=[
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3("Bem-vindo ao Dashboard de Ondas de Calor", className="text-center mb-4"),
                            html.Div([
                                html.A(
                                    html.Img(
                                        src=get_image_url(app, 'logo.png'),
                                        style={'height': '80px', 'width': 'auto', 'marginBottom': '20px'},
                                        className="img-fluid"
                                    ),
                                    href="http://www.lagas.unb.br",
                                    target="_blank",
                                    style={'marginRight': '32px'}
                                ),
                                html.A(
                                    html.Img(
                                        src=get_image_url(app, 'geocalor_nome.png'),
                                        style={'height': '60px', 'width': 'auto', 'marginBottom': '20px'},
                                        className="img-fluid"
                                    ),
                                    href="http://www.lagas.unb.br/index.php/produtos/geocalor",
                                    target="_blank"
                                )
                            ], className="d-flex justify-content-center align-items-center mb-3 gap-3"),
                            html.P([
                                "O projeto Geocalor tem como principal objetivo pesquisar os impactos das ondas de calor na saúde para ter subsídios científicos para criação de um sistema de alerta e apoiar a gestão do SUS na definição de melhores estratégias para direcionar a população nesses períodos de elevadas temperaturas em decorrência dos extremos de calor.",
                                html.Br(), html.Br(),
                                "Atualmente, as mudanças ambientais globais que presenciamos no mundo todo têm feito com que as ondas de calor sejam cada vez mais intensas e frequentes, trazendo mais riscos à saúde humana.",
                                html.Br(), html.Br(),
                                "Este dashboard foi desenvolvido para analisar e visualizar dados climáticos, com foco em ondas de calor e anomalias de temperatura. Utilizamos dados de estações meteorológicas para identificar padrões climáticos e eventos extremos, contribuindo para a conscientização e planejamento frente às mudanças climáticas."
                            ], className="text-center mb-4"),
                            html.Hr(),
                            html.H5("Apoiadores", className="text-center mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    html.A(
                                        html.Img(
                                            src=get_image_url(app, 'cnpq.png'),
                                            style={'height': '60px', 'width': 'auto'},
                                            className="img-fluid"
                                        ),
                                        href="https://www.lattes.cnpq.br/",
                                        target="_blank"
                                    )
                                ], width=2, className="text-center"),
                                dbc.Col([
                                    html.A(
                                        html.Img(
                                            src=get_image_url(app, 'unb.png'),
                                            style={'height': '60px', 'width': 'auto'},
                                            className="img-fluid"
                                        ),
                                        href="https://www.unb.br",
                                        target="_blank"
                                    )
                                ], width=2, className="text-center"),
                                dbc.Col([
                                    html.A(
                                        html.Img(
                                            src=get_image_url(app, 'ird.png'),
                                            style={'height': '60px', 'width': 'auto'},
                                            className="img-fluid"
                                        ),
                                        href="https://en.ird.fr/",
                                        target="_blank"
                                    )
                                ], width=2, className="text-center"),
                                dbc.Col([
                                    html.A(
                                        html.Img(
                                            src=get_image_url(app, 'lmi_logo.png'),
                                            style={'height': '60px', 'width': 'auto'},
                                            className="img-fluid"
                                        ),
                                        href="#",
                                        target="_blank"
                                    )
                                ], width=2, className="text-center"),
                                dbc.Col([
                                    html.A(
                                        html.Img(
                                            src=get_image_url(app, 'ufrj_logo.png'),
                                            style={'height': '60px', 'width': 'auto'},
                                            className="img-fluid"
                                        ),
                                        href="#",
                                        target="_blank"
                                    )
                                ], width=2, className="text-center"),
                                dbc.Col([
                                    html.A(
                                        html.Img(
                                            src=get_image_url(app, 'fiocruz.jpg'),
                                            style={'height': '60px', 'width': 'auto'},
                                            className="img-fluid"
                                        ),
                                        href="#",
                                        target="_blank"
                                    )
                                ], width=2, className="text-center"),
                                dbc.Col([
                                    html.A(
                                        html.Img(
                                            src=get_image_url(app, 'observatorio.png.png'),
                                            style={'height': '60px', 'width': 'auto'},
                                            className="img-fluid"
                                        ),
                                        href="https://climaesaude.icict.fiocruz.br/",
                                        target="_blank"
                                    )
                                ], width=2, className="text-center"),
                            ], className="justify-content-center align-items-center"),
                            html.Hr(),
                            html.H3("Equipe Principal", className="text-center mb-4"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        html.I(className="fas fa-chevron-left"),
                                        id="prev-button",
                                        color="primary",
                                        className="me-2"
                                    ),
                                ], width=2, className="d-flex align-items-center justify-content-center"),
                                dbc.Col([
                                    html.Div(id="team-cards-row", className="team-cards-container")
                                ], width=8),
                                dbc.Col([
                                    dbc.Button(
                                        html.I(className="fas fa-chevron-right"),
                                        id="next-button",
                                        color="primary",
                                        className="ms-2"
                                    ),
                                ], width=2, className="d-flex align-items-center justify-content-center")
                            ], className="align-items-center"),
                            dcc.Store(id="current-member-index", data=0),
                            dcc.Store(id="team-members", data=[
                                {
                                    "name": "Helen C. Gurgel",
                                    "role": "COORDENAÇÃO",
                                    "institution": "UnB / GEA",
                                    "areas": "Geotecnologia, saúde e meio ambiente e Geocartografia",
                                    "image": "helen.jpg",
                                    "lattes": "http://lattes.cnpq.br/0975018553829295",
                                    "researchgate": "https://www.researchgate.net/profile/Helen_Gurgel"
                                },
                                {
                                    "name": "Eliane Lima e Silva",
                                    "role": "PESQUISADORES PARCEIROS",
                                    "institution": "Consultora em Saúde Pública",
                                    "areas": "Saúde Coletiva, Saúde Pública, Saúde Ambiental, Ciências Ambientais",
                                    "image": "eliane.png",
                                    "lattes": "http://lattes.cnpq.br/2241554336609585",
                                    "researchgate": "https://www.researchgate.net/profile/Eliane_Lima_E_Silva"
                                },
                                {
                                    "name": "Eucilene Alves Santanna Porto",
                                    "role": "PESQUISADORES PARCEIROS",
                                    "institution": "Consultora em Saúde Pública",
                                    "areas": "Ambiente e Saúde",
                                    "image": "eucilene.jpg",
                                    "lattes": "http://lattes.cnpq.br/5603383846224202",
                                    "researchgate": "https://www.researchgate.net/profile/Eucilene_Alves_Santana"
                                },
                                {
                                    "name": "Amarílis Bahia Bezerra",
                                    "role": "PESQUISADORES COLABORADORES",
                                    "institution": "Pesquisadora Colaboradora UnB/LAGAS",
                                    "areas": "Geoprocessamento, Geografia da Saúde, Ondas de Calor",
                                    "image": "amarilis.png",
                                    "lattes": "http://lattes.cnpq.br/5691395606608035"
                                },
                                {
                                    "name": "Bruno Lofrano Porto",
                                    "role": "PESQUISADORES COLABORADORES",
                                    "institution": "Pesquisador Colaborador UnB/LAGAS",
                                    "areas": "Geoprocessamento, Climatologia, Ondas de Calor, Atividade Física",
                                    "image": "bruno.jpeg",
                                    "lattes": "http://lattes.cnpq.br/9681269314498480"
                                },
                                {
                                    "name": "Peter Zeilhofer",
                                    "role": "PÓS-DOUTORANDOS",
                                    "institution": "",
                                    "areas": "Geoprocessamento, SIG, Modelação hidrológica",
                                    "image": "peter.png",
                                    "lattes": "http://lattes.cnpq.br/1101747116364613"
                                },
                                {
                                    "name": "Adriana Dennise Rodriguez Blanco",
                                    "role": "DOUTORANDOS",
                                    "institution": "UnB / GEA",
                                    "areas": "Geografia da Saúde, Turismo e Saúde",
                                    "image": "Adriana-Rodriguez-Blanco.png",
                                    "lattes": "http://lattes.cnpq.br/7459490421107821"
                                },
                                {
                                    "name": "Caio Martins Leal",
                                    "role": "GRADUANDOS",
                                    "institution": "UnB / GEA",
                                    "areas": "Geoprocessamento, Geografia da Saúde",
                                    "image": "caio.jpeg",
                                    "lattes": "http://lattes.cnpq.br/5570352800075153"
                                },
                                {
                                    "name": "Rafaela Oliveira Cipriano",
                                    "role": "GRADUANDOS",
                                    "institution": "UnB / GEA",
                                    "areas": "Geoprocessamento, Geografia da Saúde",
                                    "image": "rafaela.jpeg",
                                    "lattes": " http://lattes.cnpq.br/2024566715066310"
                                },
                                {
                                    "name": "Hendesson Alves Pereira",
                                    "role": "GRADUANDOS",
                                    "institution": "UnB / GEA",
                                    "areas": "Geoprocessamento, Geografia da Saúde",
                                    "image": "hend.jpeg",
                                    "lattes": "http://lattes.cnpq.br/7900166623696256"
                                },
                                {
                                    "name": "Isabella Anderson de Jesus Gomes de Sá",
                                    "role": "GRADUANDOS",
                                    "institution": "UnB / GEA",
                                    "areas": "Geoprocessamento, Geografia da Saúde",
                                    "image": "isabella.png",
                                    "lattes": "http://lattes.cnpq.br/0686385905856513/"
                                },
                                {
                                    "name": "Lívia Feitosa de Oliveira",
                                    "role": "GRADUANDOS",
                                    "institution": "UnB / GEA",
                                    "areas": "Geoprocessamento, Geografia da Saúde",
                                    "image": "livia.jpeg",
                                    "lattes": "http://lattes.cnpq.br/4395234813514048"
                                }
                            ]),
                            html.Hr(),
                            html.H3("Contato", className="text-center mb-4"),
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.P("Laboratório de Geografia, Ambiente e Saúde", className="fw-bold mb-1"),
                                        html.P("Universidade de Brasília - Campus Darcy Ribeiro", className="mb-1"),
                                        html.P("Instituto de Ciências Humanas - Departamento de Geografia", className="mb-1"),
                                        html.P("ICC Norte, Subsolo, Módulo 23", className="mb-1"),
                                        html.P("Brasília-DF - 70.904-970", className="mb-1"),
                                        html.P(["E-mail: ", html.A("lagas@unb.br", href="mailto:lagas@unb.br")], className="mb-3"),
                                        html.H5("Acompanhe o LAGAS através das redes sociais", className="mt-4 mb-2"),
                                        html.Div([
                                            html.A(
                                                [html.I(className="fab fa-instagram me-2"), "Instagram"],
                                                href="https://www.instagram.com/lagas_unb",
                                                target="_blank",
                                                className="btn btn-outline-primary me-2"
                                            ),
                                            html.A(
                                                [html.I(className="fab fa-youtube me-2"), "YouTube"],
                                                href="https://www.youtube.com/channel/UC2_1JOADwnkAK7d3I3llRwg",
                                                target="_blank",
                                                className="btn btn-outline-danger me-2"
                                            ),
                                            html.A(
                                                [html.I(className="fab fa-facebook me-2"), "Facebook"],
                                                href="https://facebook.com/UnBLagas",
                                                target="_blank",
                                                className="btn btn-outline-primary"
                                            )
                                        ], className="d-flex flex-wrap")
                                    ])
                                ], width=6),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            dl.Map([
                                                dl.TileLayer(),
                                                dl.Marker(position=[-15.761341999091455, -47.87036162978922], children=dl.Tooltip("LAGAS - UnB"))
                                            ], style={"width": "100%", "height": "300px"}, center=[-15.761341999091455, -47.87036162978922], zoom=16)
                                        ])
                                    ], style={"backgroundColor": "white", "borderRadius": "10px", "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"})
                                ], width=6, className="p-3")
                            ], className="mt-4 mb-4 align-items-center"),
                        ])
                    ])
                ], width=12)
            ])
        ]),
        dcc.Tab(label="Temperaturas Diárias", children=[
            html.Br(),
            html.Label("Selecione o período:"),
            dcc.RangeSlider(
                id="slider-anos",
                min=min(anos) if anos else 1981,
                max=2023,
                step=1,
                marks={int(a): str(a) for a in anos[::2]} if anos else {1981: "1981", 2023: "2023"},
                value=[min(anos), 2023] if anos else [1981, 2023]
            ),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Estações Meteorológicas Utilizadas")),
                        dbc.CardBody([
                            dl.Map([
                                dl.TileLayer(),
                                dl.LayerGroup([
                                    dl.Marker(position=(row["Lat"], row["Long"]),
                                              children=dl.Tooltip(row["cidade"]))
                                    for _, row in df.drop_duplicates("cidade")[["cidade", "Lat", "Long"]].iterrows()
                                ]) if not df.empty else []
                            ], style={"width": "100%", "height": "400px"},
                               center=(df["Lat"].mean(), df["Long"].mean()) if not df.empty else (-15, -50), zoom=3),
                        ])
                    ]),
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Metodologia", className="card-title"),
                            html.P([
                                "Nesse Projeto estamos utilizando o Fator de Excesso de Calor (EHF – Excess Heat Factor) para definir as Ondas de Calor e classifica-las em relação intensidade. O EHF é um cálculo desenvolvido por Nairn e Fawcett em 2015 e já foi testado e aprovado para uso no mundo todo, inclusive em muitos estudos no Brasil e até por secretarias de saúde estatais. Os cálculos do EHF levam em conta as características locais e fazem uma média entre um período de vários anos anteriores e dos 30 dias anteriores, pois esse é, aproximadamente, o tempo que o corpo leva para se adaptar às temperaturas. Ou seja, se a temperatura subir muito rapidamente, as pessoas não conseguirão se adaptar às condições extremas e os impactos podem ser mais graves. Por conta dessa característica, o EHF é recomendado para estudos sobre Ondas de Calor e Saúde. As fórmulas utilizadas podem ser vistas abaixo, mas para acessar o artigo original, você pode ",
                                html.A("clicar aqui", href="https://www.mdpi.com/1660-4601/12/1/227", target="_blank"),
                                "."
                            ], className="card-text"),
                            html.Div([
                                html.P("T95 = percentil 95 das temperaturas médias diárias para o período de referência (30 anos).", className="mb-2"),
                                html.P("Ti = temperatura média diária do dia i.", className="mb-2"),
                                html.P("EHIsig = ((Ti + Ti+1 + Ti+2) / 3) – T95", className="mb-2"),
                                html.P("EHIaccl = ((Ti + Ti+1 + Ti+2) / 3) - ((Ti-1 + ... + Ti-30) / 30)", className="mb-2"),
                                html.P("EHF = EHIsig * max(1, EHIaccl)", className="mb-4")
                            ], className="mt-3"),
                            html.H5("DADOS", className="card-title mt-4 mb-2 text-center"),
                            dbc.Row([
                                dbc.Col([
                                    html.Img(src=get_image_url(app, 'inmet.png'), style={'height': '50px', 'width': 'auto'}, className="mx-auto d-block mb-2")
                                ], width=4, className="text-center"),
                                dbc.Col([
                                    html.Img(src=get_image_url(app, 'icea.png'), style={'height': '50px', 'width': 'auto'}, className="mx-auto d-block mb-2")
                                ], width=4, className="text-center"),
                                dbc.Col([
                                    html.Img(src=get_image_url(app, 'geocalor.png'), style={'height': '50px', 'width': 'auto'}, className="mx-auto d-block mb-2")
                                ], width=4, className="text-center")
                            ], className="justify-content-center align-items-center mb-2")
                        ], style={"background-color": "#f8f9fa", "border-radius": "10px"})
                    ], className="mt-3")
                ], width=5),
                dbc.Col([
                    html.Label("Cidade:"),
                    dcc.Dropdown(cidades, cidades[0] if cidades else None, id="cidade-temp"),
                    dcc.Loading(dcc.Graph(id="grafico-temp")),
                    dcc.Loading(dcc.Graph(id="grafico-umidade"))
                ], width=7)
            ])
        ]),
        dcc.Tab(label="Análise de Ondas de Calor", children=[
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H5("Dias de Ondas de Calor por Mês (1981 a 2023)", className="text-center"),
                    dbc.Row([
                        dbc.Col(dcc.Dropdown(id="cidade-hw-total", options=[{"label": cidade, "value": cidade} for cidade in cidades], value=cidades[0] if cidades else None), width=12)
                    ]),
                    dcc.Loading(dcc.Graph(id="grafico-polar-total"))
                ], width=6),
                dbc.Col([
                    html.H5("Dias de Ondas de Calor por Mês (Ano)", className="text-center"),
                    dbc.Row([
                        dbc.Col(dcc.Dropdown(id="cidade-hw", options=[{"label": cidade, "value": cidade} for cidade in cidades], value=cidades[0] if cidades else None), width=6),
                        dbc.Col(dcc.Dropdown(id="ano-hw", options=[{"label": str(ano), "value": ano} for ano in anos if ano <= 2023], value=min(anos[-1], 2023) if anos else None), width=6)
                    ]),
                    dcc.Loading(dcc.Graph(id="grafico-polar"))
                ], width=6)
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Mostrar/Ocultar Calendário de Ondas de Calor",
                        id="btn-calendario",
                        color="primary",
                        className="mb-3"
                    ),
                    html.Div(id="calendar-container", style={"display": "none"})
                ], width=12)
            ]),
            html.Br(),
            html.H5("Temperatura Diária e Ondas de Calor", className="text-center mt-4 mb-2"),
            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        dcc.Graph(id="grafico-temp-hw"),
                        type="circle"
                    ),
                    html.P(
                        "Pico: valores de temperatura máxima acima do Percentil T95",
                        className="text-center mb-2",
                        style={"fontSize": "0.95em", "color": "#b85c00"}
                    )
                ], width=12)
            ]),
            html.Br(),
            html.H6("Mapa de Temperatura Extrema", className="mb-2 ms-3"),
            html.Div([
                html.Img(
                    src=get_image_url(app, 'limiares de temperaturas extremas.png'),
                    id="img-mapa-temperatura",
                    style={
                        'width': '50px',
                        'height': '50px',
                        'objectFit': 'cover',
                        'cursor': 'pointer',
                        'transition': 'all 0.3s ease',
                        'display': 'block',
                        'marginLeft': '15px'
                    }
                ),
                dbc.Tooltip("Clique para expandir", target="img-mapa-temperatura", id="mapa-temperatura-tooltip")
            ], id="container-mapa-temperatura", className="mb-4"),
            html.Br(),
            html.H5("EHF Diário e Limiar de Onda de Calor (OC)", className="text-center mt-4 mb-2"),
            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        dcc.Graph(id="grafico-ehf-hw"),
                        type="circle"
                    )
                ], width=12)
            ]),
            html.Br(),
            html.H5("Umidade Diária e Ondas de Calor", className="text-center mt-4 mb-2"),
            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        dcc.Graph(id="grafico-umidade-hw"),
                        type="circle"
                    )
                ], width=12)
            ]),
            html.Br(),
            html.H5("Frequência de Ondas de Calor por Ano e Cidade", className="text-center mt-4 mb-2"),
            # Heatmap original
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("Dias", id="btn-heatmap-dias", color="primary", active=True),
                        dbc.Button("Eventos", id="btn-heatmap-eventos", color="primary")
                    ], id="btn-group-heatmap", className="mb-3")
                ], width=12, className="text-center"),
                dbc.Col([
                    dcc.Loading(
                        dcc.Graph(id="heatmap-oc"),
                        type="circle"
                    )
                ], width=12)
            ]),
            # Seção de Mapas Anuais Interativos
            html.H6("Mapas Anuais", className="mb-2 ms-3"), # Título para a coleção de mapas, alinhado à esquerda
            # Container para alinhar o mapa e a navegação abaixo do título
            html.Div([
                # Navegação (visível apenas quando o mapa está expandido)
                html.Div([
                    dbc.Row([
                        dbc.Col(dbc.Button(html.I(className="fas fa-chevron-left"), id="prev-year-map-button", color="primary", className="me-2"), width=2, className="d-flex justify-content-end align-items-center"),
                        dbc.Col(html.H4(id="current-map-year", className="text-center mb-0"), width=8, className="d-flex justify-content-center align-items-center"),
                        dbc.Col(dbc.Button(html.I(className="fas fa-chevron-right"), id="next-year-map-button", color="primary", className="ms-2"), width=2, className="d-flex justify-content-start align-items-center"),
                    ], className="mb-3 align-items-center"),
                ], id="year-map-navigation", style={'display': 'none', 'width': '100%', 'justifyContent': 'center'}), # Container da navegação, inicialmente escondido e ocupa 100% da largura do pai
                
                # Área do Mapa com funcionalidade de expandir
                html.Div([
                    html.Img(
                        src=get_image_url(app, 'DIAS 2010.png'), # Define uma imagem inicial
                        id="heatmap-year-map",
                        style={
                            'width': '50px', # Tamanho inicial pequeno
                            'height': '50px', # Tamanho inicial pequeno
                            'objectFit': 'cover',
                            'cursor': 'pointer',
                            'transition': 'all 0.3s ease',
                            'display': 'block',
                            'margin': '0' # Remove margens automáticas para alinhar à esquerda
                        }
                    ),
                    dbc.Tooltip("", target="heatmap-year-map", id="heatmap-year-tooltip")
                ], id="container-heatmap-year-map", className="mb-4 ms-3"), # Container da imagem, alinhado à esquerda com margem
                
                dcc.Store(id='current-year-map-index', data=0),
                dcc.Store(id='year-map-list', data=[str(y) for y in range(2010, 2024)])

            ]),
            # Fim da Seção de Mapas Interativos
        ]),
        dcc.Tab(label="Eventos Extremos", children=[
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Mapa interativo dos eventos extremos nas Regiões Metropolitanas", className="text-center")),
                        dbc.CardBody([
                            html.Div([
                                html.Iframe(
                                    id="mapa-interativo",
                                    srcDoc=open(r'C:\pibic_dash\mapa_interativo.html', 'r', encoding='utf-8').read(),
                                    style={
                                        'width': '100%',
                                        'height': '600px',
                                        'border': 'none'
                                    }
                                )
                            ])
                        ])
                    ])
                ], width=12)
            ])
        ]),
        # Aba de Internações removida completamente
        dcc.Tab(label="Ficha Técnica", children=[
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3("Ficha Técnica", className="text-center mb-4"),
                            html.Div([
                                html.H5("Financiamento do Projeto:", className="mb-3"),
                                html.P([
                                    "CNPq – Conselho Nacional de Desenvolvimento Científico e Tecnológico chamada N° 18/2023 (processo 444938/2023-0);",
                                    html.Br(),
                                    "IRD – Institut de Recherche pour le Développement (Instituto Francês de Pesquisa para o Desenvolvimento)."
                                ], className="mb-4"),
                                html.H5("Desenvolvido por:", className="mb-3"),
                                html.P("Laboratório de Geografia, Ambiente e Saúde (LAGAS) da Universidade de Brasília (UnB)", className="mb-4"),
                                html.H5("Equipe do Projeto:", className="mb-3"),
                                html.P("Helen Gurgel, Eliane Lima e Silva, Eucilene Alves Santana, Amarílis Bezerra, Bruno Porto, Peter Zeilhofer, Caio Leal, Hendesson Alves, Isabella de Sá, Livia Feitosa, Adriana Dennise Rodriguez-Blanco.", className="mb-4"),
                                html.H5("Observação:", className="mb-3"),
                                html.P([
                                    "Esse projeto está gerando publicações de artigos científicos que você pode acessar no site ",
                                    html.A("lagas.unb.br", href="http://www.lagas.unb.br", target="_blank")
                                ], className="mb-4"),
                                html.H5("Desenvolvimento:", className="mb-3"),
                                html.P("Painel desenvolvido por Hendesson Alves, sob orientação de Bruno Porto.", className="mb-4"),
                                html.H5("Como Citar:", className="mb-3"),
                                html.Div([
                                    html.P("NBR 6023: lorem impsum", className="mb-2"),
                                    html.P("APA: lorem impsum", className="mb-2"),
                                    html.P("Vancouver: lorem impsum", className="mb-4")
                                ]),
                                html.Div([
                                    html.A(
                                        html.Img(
                                            src=get_image_url(app, 'logo.png'),
                                            style={'height': '80px', 'width': 'auto', 'marginBottom': '20px'},
                                            className="img-fluid"
                                        ),
                                        href="http://www.lagas.unb.br",
                                        target="_blank",
                                        style={'marginRight': '32px'}
                                    ),
                                    html.A(
                                        html.Img(
                                            src=get_image_url(app, 'geocalor_nome.png'),
                                            style={'height': '60px', 'width': 'auto', 'marginBottom': '20px'},
                                            className="img-fluid"
                                        ),
                                        href="http://www.lagas.unb.br",
                                        target="_blank"
                                    )
                                ], className="text-center mb-4"),
                                html.Hr()
                            ])
                        ])
                    ])
                ], width=12)
            ])
        ])
    ])
], fluid=True)

@app.callback(
    [Output("grafico-temp", "figure"),
     Output("grafico-umidade", "figure")],
    [Input("cidade-temp", "value"),
     Input("slider-anos", "value")]
)
def update_temp(cidade, anos_selecionados):
    if not cidade or df.empty:
        return visualizer.create_temperature_plot(pd.DataFrame(), "", 0, 0), visualizer.create_umidity_plot(pd.DataFrame(), "", 0, 0)
    
    ano_inicio, ano_fim = anos_selecionados
    
    return (
        visualizer.create_temperature_plot(df, cidade, ano_inicio, ano_fim),
        visualizer.create_umidity_plot(df, cidade, ano_inicio, ano_fim)
    )

@app.callback(
    Output("grafico-polar-total", "figure"),
    [Input("cidade-hw-total", "value")]
)
def update_hw_total(cidade_total):
    # Verifica se há dados ou cidade selecionada, caso contrário retorna um estado vazio.
    if not cidade_total or df.empty:
        return visualizer.create_polar_plot(pd.DataFrame(), "", 0)

    # Usa dados de dias de ondas de calor
    df_polar_total = data_processor.calculate_hw_monthly_all_years(cidade_total)

    # Retorna a figura do gráfico polar
    return visualizer.create_polar_plot(df_polar_total, cidade_total, None)

@app.callback(
    [Output("grafico-polar", "figure"),
     Output("calendar-container", "children")],
    [Input("cidade-hw", "value"),
     Input("ano-hw", "value")]
)
def update_hw_annual(cidade, ano):
    if not cidade or not ano or df.empty:
        return visualizer.create_polar_plot(pd.DataFrame(), "", 0), []
    
    # Usa dados de dias de ondas de calor
    df_polar = data_processor.calculate_hw_monthly(cidade, ano)
    
    # Lógica para o calendário
    dias_calor = data_processor.get_heat_wave_days(cidade)
    calendar_children = create_calendar_grid(dias_calor, ano, cidade)

    # Retorna os outputs
    return (
        visualizer.create_polar_plot(df_polar, cidade, ano),
        calendar_children
    )

def create_calendar_grid(dias_calor, ano, cidade):
    calendars = []
    for mes in range(1, 13):
        calendars.append(
            dbc.Col(
                create_calendar_component(dias_calor, ano, mes, cidade),
                width=4,
                className="mb-4"
            )
        )
    return dbc.Row(calendars)

@app.callback(
    Output("calendar-container", "style"),
    [Input("btn-calendario", "n_clicks")],
    [State("calendar-container", "style")]
)
def toggle_calendar(n_clicks, current_style):
    if n_clicks is None:
        n_clicks = 0
    
    if n_clicks % 2 == 0:
        return {"display": "none"}
    else:
        return {"display": "block"}

@app.callback(
    Output("grafico-temp-hw", "figure"),
    [Input("cidade-hw", "value"),
     Input("ano-hw", "value")]
)
def update_temp_hw_plot(cidade, ano):
    if not cidade or not ano or df.empty:
        return visualizer.create_temperature_hw_plot(pd.DataFrame(), "", 0)
    
    return visualizer.create_temperature_hw_plot(df, cidade, ano)

@app.callback(
    Output("grafico-ehf-hw", "figure"),
    [Input("cidade-hw", "value"), Input("ano-hw", "value")]
)
def update_ehf_hw_plot(cidade, ano):
    if not cidade or not ano or df.empty:
        return go.Figure()
    dff = df[(df["cidade"] == cidade) & (df["year"] == ano)].copy()
    if dff.empty:
        return go.Figure()
    dff["index"] = pd.to_datetime(dff["index"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dff["index"], y=dff["EHF"], mode="lines", name="EHF", line=dict(color="black")))
    fig.add_trace(go.Scatter(x=dff["index"], y=[0]*len(dff), mode="lines", name="Limiar OC", line=dict(color="red", dash="dash")))
    # Ajuste do eixo y para ser simétrico em torno de zero
    max_abs_ehf = max(abs(dff["EHF"].max()), abs(dff["EHF"].min()), 12)
    y_tickvals = [-12, 0, 12]
    if max_abs_ehf > 12:
        step = 6
        max_tick = int((max_abs_ehf // step + 1) * step)
        y_tickvals = list(range(-max_tick, max_tick+1, step))
    fig.update_layout(
        title=f"EHF Diário e Limiar de Onda de Calor (OC) ({cidade}, {ano})",
        xaxis_title="Data",
        yaxis_title="EHF (°C)",
        legend=dict(orientation="h"),
        yaxis=dict(tickvals=y_tickvals, zeroline=True, zerolinecolor='red')
    )
    return fig

@app.callback(
    Output("grafico-umidade-hw", "figure"),
    [Input("cidade-hw", "value"),
     Input("ano-hw", "value")]
)
def update_umidity_hw_plot(cidade, ano):
    if not cidade or not ano or df.empty:
        return visualizer.create_umidity_hw_plot(pd.DataFrame(), "", 0)
    
    return visualizer.create_umidity_hw_plot(df, cidade, ano)

@app.callback(
    Output("team-cards-row", "children"),
    [Input("current-member-index", "data"),
     Input("team-members", "data")]
)
def update_team_cards(index, members):
    if not members:
        return []
    n = len(members)
    # Pega os índices das 5 cartas a serem exibidas
    indices = [
        (index - 2) % n,
        (index - 1) % n,
        index % n,
        (index + 1) % n,
        (index + 2) % n
    ]
    classes = ["card-far-left", "card-left", "card-center", "card-right", "card-far-right"]
    cards = []
    for idx, cls in zip(indices, classes):
        member = members[idx]
        cards.append(
            html.Div([
                html.H4(member["role"], className="text-center mb-2"),
                html.Img(
                    src=app.get_asset_url(member["image"]),
                    style={
                        'width': '120px' if cls!="card-center" else '200px',
                        'height': '120px' if cls!="card-center" else '200px',
                        'objectFit': 'cover',
                        'borderRadius': '50%',
                        'margin': '0 auto',
                        'display': 'block'
                    },
                    className="mb-2"
                ),
                html.H5(member["name"], className="text-center mb-1"),
                html.P(member["institution"], className="text-center mb-1", style={"fontSize": "0.95em"}),
                html.P(f"Áreas: {member['areas']}", className="text-center mb-2", style={"fontSize": "0.85em"}),
                html.Div([
                    html.A(
                        html.Img(
                            src=get_image_url(app, 'logo_lattes.png'),
                            style={'height': '32px', 'width': '32px'},
                            title='Lattes'
                        ),
                        href=member["lattes"],
                        target="_blank",
                        className="me-2"
                    ),
                    html.A(
                        html.Img(
                            src=get_image_url(app, 'research_logo.png'),
                            style={'height': '32px', 'width': '32px'},
                            title='ResearchGate'
                        ),
                        href=member["researchgate"],
                        target="_blank"
                    ) if member.get("researchgate") else None
                ], className="d-flex justify-content-center")
            ], className=f"team-card {cls}")
        )
    return cards

@app.callback(
    Output("current-member-index", "data"),
    [Input("prev-button", "n_clicks"),
     Input("next-button", "n_clicks")],
    [State("current-member-index", "data"),
     State("team-members", "data")]
)
def update_member_index(prev_clicks, next_clicks, current_index, members):
    if not members:
        return 0
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_index
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "prev-button":
        return (current_index - 1) % len(members)
    elif button_id == "next-button":
        return (current_index + 1) % len(members)
    
    return current_index

@app.callback(
    [Output('heatmap-year-map', 'style'),
     Output('year-map-navigation', 'style')],
    [Input('heatmap-year-map', 'n_clicks')],
    [State('heatmap-year-map', 'style'),
     State('year-map-navigation', 'style')]
)
def toggle_heatmap_map_size(n_clicks, current_map_style, current_nav_style):
    if n_clicks is None:
        n_clicks = 0
        
    # Define os estilos para os dois estados do mapa
    initial_map_style = {
        'width': '50px',
        'height': '50px',
        'objectFit': 'cover',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'display': 'block',
        'margin': '0' # Alinhado à esquerda
    }

    expanded_map_style = {
        'width': '50%', # Ocupa metade da tela
        'height': 'auto',
        'objectFit': 'contain',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'display': 'block',
        'margin': '0 auto' # Centraliza quando expandido
    }
    
    # Define os estilos para os dois estados da navegação
    hidden_nav_style = {'display': 'none'}
    visible_nav_style = {'display': 'flex', 'justifyContent': 'center', 'width': '100%'}

    if n_clicks % 2 == 0:
        # Estado inicial (mapa pequeno, navegação escondida)
        return initial_map_style, hidden_nav_style
    else:
        # Estado expandido (mapa maior, navegação visível)
        return expanded_map_style, visible_nav_style

@app.callback(
    Output('current-year-map-index', 'data'),
    [Input('prev-year-map-button', 'n_clicks'),
     Input('next-year-map-button', 'n_clicks')],
    [State('current-year-map-index', 'data'),
     State('year-map-list', 'data')]
)
def update_year_map_index(prev_clicks, next_clicks, current_index, year_list):
    if not year_list: # Garante que a lista de anos não está vazia
        return 0

    ctx = dash.callback_context
    if not ctx.triggered:
        return current_index
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    n_years = len(year_list)
    
    if button_id == 'prev-year-map-button':
        return (current_index - 1 + n_years) % n_years # Loop infinito para trás
    elif button_id == 'next-year-map-button':
        return (current_index + 1) % n_years # Loop infinito para frente
        
    return current_index # Retorna o índice atual se nenhum botão foi clicado

@app.callback(
    [Output('heatmap-year-map', 'src'),
     Output('current-map-year', 'children'),
     Output('heatmap-year-tooltip', 'children')],
    [Input('current-year-map-index', 'data'),
     Input('year-map-list', 'data')]
)
def update_heatmap_year_map(current_index, year_list):
    if not year_list:
        return '', '', ''
    
    year = year_list[current_index]
    img_src = get_image_url(app, f'DIAS {year}.png')
    return img_src, f'Ano: {year}', f'Mapa do Ano {year}'

@app.callback(
    [Output('img-mapa-temperatura', 'style'),
     Output('mapa-temperatura-tooltip', 'children')],
    [Input('img-mapa-temperatura', 'n_clicks')],
    [State('img-mapa-temperatura', 'style')]
)
def toggle_mapa_temperatura_size(n_clicks, current_style):
    if n_clicks is None:
        n_clicks = 0
        
    # Define os estilos para os dois estados do mapa
    initial_map_style = {
        'width': '50px',
        'height': '50px',
        'objectFit': 'cover',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'display': 'block',
        'marginLeft': '15px'
    }

    expanded_map_style = {
        'width': '50%',
        'height': 'auto',
        'objectFit': 'contain',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'display': 'block',
        'margin': '0 auto'
    }

    if n_clicks % 2 == 0:
        # Estado inicial (mapa pequeno)
        return initial_map_style, "Clique para expandir"
    else:
        # Estado expandido (mapa maior)
        return expanded_map_style, "Clique para reduzir"

@app.callback(
    [Output("heatmap-oc", "figure"),
     Output("btn-heatmap-dias", "active"),
     Output("btn-heatmap-eventos", "active")],
    [Input("btn-heatmap-dias", "n_clicks"),
     Input("btn-heatmap-eventos", "n_clicks")]
)
def update_heatmap(dias_clicks, eventos_clicks):
    if df.empty:
        return {}, True, False
    
    ctx = dash.callback_context
    button_id = None
    if ctx.triggered:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "btn-heatmap-eventos":
        # Usar dados de eventos
        df_heatmap_data = data_processor.prepare_heatmap_events_data()
        is_dias_active = False
        is_eventos_active = True
        title = "Frequência de Eventos de Ondas de Calor por Ano e Cidade"
        color_bar_title = "Número de Eventos"
        color_scale = "Oranges"
    else:
        # Usar dados de dias por padrão ou se btn-heatmap-dias foi clicado
        df_heatmap_data = data_processor.prepare_heatmap_data()
        is_dias_active = True
        is_eventos_active = False
        title = "Frequência de Dias de Ondas de Calor por Ano e Cidade"
        color_bar_title = "Número de Dias"
        color_scale = "Reds"
    # Cria o heatmap
    fig = px.imshow(
        df_heatmap_data.pivot(index='cidade', columns='year', values='count').fillna(0),
        labels=dict(x="Ano", y="Cidade", color=color_bar_title),
        color_continuous_scale=color_scale,
        aspect="auto"
    )
    
    # Atualiza o layout
    fig.update_layout(
        title=title,
        xaxis_title="Ano",
        yaxis_title="Cidade",
        coloraxis_colorbar_title=color_bar_title,
        height=500
    )
    
    return fig, is_dias_active, is_eventos_active

@app.callback(
    [Output("grafico-tmax-p95", "figure"), Output("grafico-ehf-oc", "figure")],
    [Input("cidade-p95", "value"), Input("slider-anos-p95", "value")]
)
def update_tmax_p95_ehf_oc(cidade, anos_selecionados):
    if not cidade or df.empty or not anos_selecionados:
        return go.Figure(), go.Figure()
    ano_inicio, ano_fim = anos_selecionados
    df_cidade = df[(df["cidade"] == cidade) & (df["index"].dt.year >= ano_inicio) & (df["index"].dt.year <= ano_fim)].copy()
    if df_cidade.empty:
        return go.Figure(), go.Figure()
    df_cidade["index"] = pd.to_datetime(df_cidade["index"])
    # Gráfico 1: Tmax diário + linha P95
    p95 = df_cidade["tempMax"].quantile(0.95)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_cidade["index"], y=df_cidade["tempMax"], mode="lines", name="Tmax", line=dict(color="black")))
    fig1.add_trace(go.Scatter(x=df_cidade["index"], y=[p95]*len(df_cidade), mode="lines", name="P95", line=dict(color="orange", dash="dash"), fill=None))
    # Preenchimento apenas entre P95 e Tmax acima do P95
    y_acima_p95 = [y if y > p95 else None for y in df_cidade["tempMax"]]
    y_base_p95 = [p95 if y > p95 else None for y in df_cidade["tempMax"]]
    fig1.add_trace(go.Scatter(
        x=df_cidade["index"],
        y=y_acima_p95,
        mode="lines",
        name="Acima do P95",
        fill=None,
        line=dict(color="rgba(255,140,0,0.0)")
    ))
    fig1.add_trace(go.Scatter(
        x=df_cidade["index"],
        y=y_base_p95,
        mode="lines",
        name=None,
        fill="tonexty",
        fillcolor="rgba(255,140,0,0.4)",
        line=dict(color="rgba(255,140,0,0.0)"),
        showlegend=False
    ))
    fig1.update_layout(title=f"Temperatura Máxima Diária e Limiar P95 ({cidade}, {ano_inicio}-{ano_fim})", xaxis_title="Data", yaxis_title="Tmax (°C)", legend=dict(orientation="h"))
    # Gráfico 2: EHF diário + linha OC (zero)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_cidade["index"], y=df_cidade["EHF"], mode="lines", name="EHF", line=dict(color="black")))
    fig2.add_trace(go.Scatter(x=df_cidade["index"], y=[0]*len(df_cidade), mode="lines", name="Limiar OC", line=dict(color="red", dash="dash")))
    # Preenchimento onde EHF > 0
    y_ehf_pos = [y if y > 0 else None for y in df_cidade["EHF"]]
    fig2.add_trace(go.Scatter(
        x=df_cidade["index"],
        y=y_ehf_pos,
        mode="lines",
        name="Onda de Calor (EHF>0)",
        fill="tozeroy",
        fillcolor="rgba(255,0,0,0.4)",
        line=dict(color="rgba(255,0,0,0.0)")
    ))
    fig2.update_layout(title=f"EHF Diário e Limiar de Onda de Calor (OC) ({cidade}, {ano_inicio}-{ano_fim})", xaxis_title="Data", yaxis_title="EHF (°C)", legend=dict(orientation="h"))
    return fig1, fig2

# ======================
# Callbacks Hospitalizations (SRAG + SIH) - REMOVIDOS
# ======================
# Todos os callbacks de internações foram removidos junto com a aba
# Seção comentada para manter histórico caso precise restaurar
"""
# Todos os callbacks relacionados a hospitalizations foram removidos
# pois a aba "Análise de Internações" foi removida do dashboard

# Callbacks comentados - aba removida
"""
def _hospitalizations_srag_build_time_series_figure(serie: pd.DataFrame, thresholds: pd.DataFrame, rm: str, ano: int | None) -> go.Figure:
    if serie is None or serie.empty or rm is None:
        return go.Figure()
    dff = serie[serie["RM_nome"] == rm].copy()
    if ano is not None:
        dff = dff[dff["ano"] == ano]
    if dff.empty:
        return go.Figure()
    dff = dff.sort_values("data")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dff["data"],
        y=dff["casos_totais"],
        mode="lines+markers",
        name="Casos",
        line=dict(color="#111111", width=2),
        marker=dict(size=5, color="#111111")
    ))

    cores_limiar = {
        "sem_risco": "#000099",
        "seguranca": "#009900",
        "baixo": "#FFD166",
        "moderado": "#ff8000",
        "alto": "#cc0000",
    }
    
    # Adiciona linhas tracejadas com legenda
    thr = thresholds[thresholds["RM_nome"] == rm] if thresholds is not None else pd.DataFrame()
    for _, row in thr.iterrows():
        categoria_nome = row["categoria"].replace("_", " ").title()
        fig.add_trace(go.Scatter(
            x=[dff["data"].min(), dff["data"].max()],
            y=[row["valor"], row["valor"]],
            mode="lines",
            line=dict(dash="dash", color=cores_limiar.get(row["categoria"], "#888"), width=2),
            name=f"Limiar {categoria_nome}",
            showlegend=True
        ))

    title = f"Série Temporal de Internações SRAG - {format_rm_name(rm)}" + (f" ({ano})" if ano is not None else "")
    fig.update_layout(
        title=title,
        xaxis_title="Mês/Ano",
        yaxis_title="Número de Casos",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        margin=dict(l=40, r=20, t=100, b=40),
        hovermode="x unified"
    )
    return fig


@app.callback(
    Output("hospitalizations-srag-main", "figure"),
    [Input("hospitalizations-rm-srag", "value")]
)
def hospitalizations_srag_main(rm):
    if not rm_list or df_srag.empty:
        return go.Figure()
    return _hospitalizations_srag_build_time_series_figure(df_srag, df_srag_thresholds, rm, None)


@app.callback(
    Output("hospitalizations-srag-modal-content", "figure"),
    [Input("hospitalizations-srag-modal", "is_open")]
)
def hospitalizations_srag_modal(is_open):
    if not is_open or df_srag.empty:
        return go.Figure()
    
    dff = df_srag.copy().sort_values(["RM_nome", "data"]) 
    if dff.empty:
        return go.Figure()
    
    # Formata nomes das RMs removendo underscores
    dff["RM_nome_formatado"] = dff["RM_nome"].apply(format_rm_name)
    
    # Cria figura com subplots para cada RM
    from plotly.subplots import make_subplots
    
    rm_list_formatado = sorted(dff["RM_nome_formatado"].unique())
    n_cols = 3
    n_rows = (len(rm_list_formatado) + n_cols - 1) // n_cols
    
    fig = make_subplots(
        rows=n_rows, 
        cols=n_cols,
        subplot_titles=rm_list_formatado,
        vertical_spacing=0.08,
        horizontal_spacing=0.05
    )
    
    cores_limiar = {
        "sem_risco": "#000099",
        "seguranca": "#009900", 
        "baixo": "#FFD166",
        "moderado": "#ff8000",
        "alto": "#cc0000",
    }
    
    # Adiciona dados para cada RM
    for i, rm_formatado in enumerate(rm_list_formatado):
        row = (i // n_cols) + 1
        col = (i % n_cols) + 1
        
        rm_data = dff[dff["RM_nome_formatado"] == rm_formatado]
        rm_original = rm_data["RM_nome"].iloc[0]
        
        # Adiciona linha principal
        fig.add_trace(
            go.Scatter(
                x=rm_data["data"],
                y=rm_data["casos_totais"],
                mode="lines+markers",
                name=f"Casos - {rm_formatado}",
                line=dict(color="#111111", width=2),
                marker=dict(size=4, color="#111111"),
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Adiciona linhas tracejadas dos limiares
        thr = df_srag_thresholds[df_srag_thresholds["RM_nome"] == rm_original] if not df_srag_thresholds.empty else pd.DataFrame()
        for _, threshold_row in thr.iterrows():
            categoria_nome = threshold_row["categoria"].replace("_", " ").title()
            fig.add_trace(
                go.Scatter(
                    x=[rm_data["data"].min(), rm_data["data"].max()],
                    y=[threshold_row["valor"], threshold_row["valor"]],
                    mode="lines",
                    line=dict(dash="dash", color=cores_limiar.get(threshold_row["categoria"], "#888"), width=1.5),
                    name=f"Limiar {categoria_nome}",
                    showlegend=False
                ),
                row=row, col=col
            )
    
    fig.update_layout(
        title="Série de Internações por SRAG nas RMs",
        height=900,
        template="plotly_white",
        margin=dict(l=40, r=20, t=100, b=40)
    )
    
    # Atualiza eixos
    fig.update_xaxes(title_text="Data", showgrid=True)
    fig.update_yaxes(title_text="Número de Casos", showgrid=True)
    
    return fig


@app.callback(
    Output("hospitalizations-srag-modal", "is_open"),
    [Input("btn-hospitalizations-srag-modal", "n_clicks"), Input("btn-close-hospitalizations-srag-modal", "n_clicks")],
    [State("hospitalizations-srag-modal", "is_open")]
)
def toggle_hospitalizations_srag_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open


@app.callback(
    Output("hospitalizations-srag-detailed-modal", "is_open"),
    [Input("btn-hospitalizations-srag-detailed", "n_clicks"), Input("btn-close-hospitalizations-srag-detailed", "n_clicks")],
    [State("hospitalizations-srag-detailed-modal", "is_open")]
)
def toggle_hospitalizations_srag_detailed_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

# ======================
# Callbacks SIH - Nova Estrutura
# ======================

def _hospitalizations_sih_build_individual_figure(serie: pd.DataFrame, thresholds: pd.DataFrame, rm: str, grupo: str) -> go.Figure:
    """Cria figura individual para uma RM e um grupo específico"""
    if serie is None or serie.empty or rm is None or grupo is None:
        print(f"Dados vazios ou parâmetros None - serie: {len(serie) if serie is not None else 'None'}, rm: {rm}, grupo: {grupo}")
        return go.Figure()
    
    dff = serie[(serie["RM"] == rm) & (serie["grupo"] == grupo)].copy()
    print(f"Filtro aplicado - RM: {rm}, Grupo: {grupo}, Registros encontrados: {len(dff)}")
    
    if dff.empty:
        print(f"Nenhum registro encontrado para RM: {rm}, Grupo: {grupo}")
        print(f"RMs disponíveis: {serie['RM'].unique() if not serie.empty else 'N/A'}")
        print(f"Grupos disponíveis: {serie['grupo'].unique() if not serie.empty else 'N/A'}")
        return go.Figure()
    
    dff = dff.sort_values("data")
    fig = go.Figure()
    
    # Linha principal
    fig.add_trace(go.Scatter(
        x=dff["data"],
        y=dff["casos_totais"],
        mode="lines+markers",
        name="Casos",
        line=dict(color="darkblue", width=2),
        marker=dict(size=5, color="black")
    ))

    # Cores dos limiares baseadas no código R
    cores_limiar = {
        "sem_risco": "#000099",
        "seguranca": "#009900",
        "baixo": "#FFD166",
        "moderado": "#ff8000",
        "alto": "#cc0000",
    }
    
    # Adiciona linhas tracejadas com legenda
    thr = thresholds[(thresholds["RM"] == rm) & (thresholds["grupo"] == grupo)] if thresholds is not None else pd.DataFrame()
    print(f"Limiares encontrados: {len(thr)} para RM: {rm}, Grupo: {grupo}")
    
    for _, row in thr.iterrows():
        categoria_nome = row["categoria"].replace("_", " ").title()
        fig.add_trace(go.Scatter(
            x=[dff["data"].min(), dff["data"].max()],
            y=[row["valor"], row["valor"]],
            mode="lines",
            line=dict(dash="dash", color=cores_limiar.get(row["categoria"], "#888"), width=2),
            name=f"Limiar {categoria_nome}",
            showlegend=True
        ))

    title = f"Série Temporal de Internações SIH - {format_rm_name(rm)} - {grupo}"
    fig.update_layout(
        title=title,
        xaxis_title="Mês/Ano",
        yaxis_title="Número de Casos",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        margin=dict(l=40, r=20, t=100, b=40),
        hovermode="x unified"
    )
    return fig


def _sih_build_facets_by_indicator_figure(serie: pd.DataFrame, thresholds: pd.DataFrame, rm: str) -> go.Figure:
    """Cria figura com facets por indicador para uma RM específica"""
    if serie is None or serie.empty or rm is None:
        return go.Figure()
    
    dff = serie[serie["RM"] == rm].copy().sort_values(["grupo", "data"])
    if dff.empty:
        return go.Figure()
    
    # Cria figura com subplots para cada grupo
    from plotly.subplots import make_subplots
    
    grupos_list = sorted(dff["grupo"].unique())
    n_cols = 1  # Uma coluna para melhor visualização
    n_rows = len(grupos_list)
    
    fig = make_subplots(
        rows=n_rows, 
        cols=n_cols,
        subplot_titles=grupos_list,
        vertical_spacing=0.08,
        horizontal_spacing=0.05
    )
    
    cores_limiar = {
        "sem_risco": "#000099",
        "seguranca": "#009900", 
        "baixo": "#FFD166",
        "moderado": "#ff8000",
        "alto": "#cc0000",
    }
    
    # Adiciona dados para cada grupo
    for i, grupo in enumerate(grupos_list):
        row = i + 1
        col = 1
        
        grupo_data = dff[dff["grupo"] == grupo]
        
        # Adiciona linha principal
        fig.add_trace(
            go.Scatter(
                x=grupo_data["data"],
                y=grupo_data["casos_totais"],
                mode="lines+markers",
                name=f"Casos - {grupo}",
                line=dict(color="darkblue", width=2),
                marker=dict(size=4, color="black"),
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Adiciona linhas tracejadas dos limiares
        thr = thresholds[(thresholds["RM"] == rm) & (thresholds["grupo"] == grupo)] if not thresholds.empty else pd.DataFrame()
        for _, threshold_row in thr.iterrows():
            categoria_nome = threshold_row["categoria"].replace("_", " ").title()
            fig.add_trace(
                go.Scatter(
                    x=[grupo_data["data"].min(), grupo_data["data"].max()],
                    y=[threshold_row["valor"], threshold_row["valor"]],
                    mode="lines",
                    line=dict(dash="dash", color=cores_limiar.get(threshold_row["categoria"], "#888"), width=1.5),
                    name=f"Limiar {categoria_nome}",
                    showlegend=False
                ),
                row=row, col=col
            )
    
    fig.update_layout(
        title=f"Série Temporal de Internações SIH - {format_rm_name(rm)} - Todos os Indicadores",
        height=300 * n_rows,  # Altura dinâmica baseada no número de grupos
        template="plotly_white",
        margin=dict(l=40, r=20, t=100, b=40)
    )
    
    # Atualiza eixos
    fig.update_xaxes(title_text="Data", showgrid=True)
    fig.update_yaxes(title_text="Número de Casos", showgrid=True)
    
    return fig


def _sih_build_facets_by_rm_figure(serie: pd.DataFrame, thresholds: pd.DataFrame, grupo: str) -> go.Figure:
    """Cria figura com facets por RM para um grupo específico"""
    if serie is None or serie.empty or grupo is None:
        return go.Figure()
    
    dff = serie[serie["grupo"] == grupo].copy().sort_values(["RM", "data"])
    if dff.empty:
        return go.Figure()
    
    # Cria figura com subplots para cada RM
    from plotly.subplots import make_subplots
    
    rm_list_formatado = sorted(dff["RM"].unique())
    n_cols = 3  # Três colunas para melhor organização
    n_rows = (len(rm_list_formatado) + n_cols - 1) // n_cols
    
    fig = make_subplots(
        rows=n_rows, 
        cols=n_cols,
        subplot_titles=rm_list_formatado,
        vertical_spacing=0.08,
        horizontal_spacing=0.05
    )
    
    cores_limiar = {
        "sem_risco": "#000099",
        "seguranca": "#009900", 
        "baixo": "#FFD166",
        "moderado": "#ff8000",
        "alto": "#cc0000",
    }
    
    # Adiciona dados para cada RM
    for i, rm in enumerate(rm_list_formatado):
        row = (i // n_cols) + 1
        col = (i % n_cols) + 1
        
        rm_data = dff[dff["RM"] == rm]
        
        # Adiciona linha principal
        fig.add_trace(
            go.Scatter(
                x=rm_data["data"],
                y=rm_data["casos_totais"],
                mode="lines+markers",
                name=f"Casos - {rm}",
                line=dict(color="darkblue", width=2),
                marker=dict(size=4, color="black"),
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Adiciona linhas tracejadas dos limiares
        thr = thresholds[(thresholds["RM"] == rm) & (thresholds["grupo"] == grupo)] if not thresholds.empty else pd.DataFrame()
        for _, threshold_row in thr.iterrows():
            categoria_nome = threshold_row["categoria"].replace("_", " ").title()
            fig.add_trace(
                go.Scatter(
                    x=[rm_data["data"].min(), rm_data["data"].max()],
                    y=[threshold_row["valor"], threshold_row["valor"]],
                    mode="lines",
                    line=dict(dash="dash", color=cores_limiar.get(threshold_row["categoria"], "#888"), width=1.5),
                    name=f"Limiar {categoria_nome}",
                    showlegend=False
                ),
                row=row, col=col
            )
    
    fig.update_layout(
        title=f"Série Temporal de Internações SIH - {grupo} - Todas as RMs",
        height=900,
        template="plotly_white",
        margin=dict(l=40, r=20, t=100, b=40)
    )
    
    # Atualiza eixos
    fig.update_xaxes(title_text="Data", showgrid=True)
    fig.update_yaxes(title_text="Número de Casos", showgrid=True)
    
    return fig


# Callback para série individual SIH
@app.callback(
    Output("hospitalizations-sih-main", "figure"),
    [Input("hospitalizations-rm-sih", "value"), Input("hospitalizations-grupo-sih", "value")]
)
def hospitalizations_sih_main(rm, grupo):
    if not rm_list_sih or not grupos_list_sih or df_sih.empty:
        return go.Figure()
    
    print(f"Atualizando gráfico individual - RM: {rm}, Grupo: {grupo}")
    print(f"Dados disponíveis - RMs: {len(rm_list_sih)}, Grupos: {len(grupos_list_sih)}")
    
    return _hospitalizations_sih_build_individual_figure(df_sih, df_sih_thresholds, rm, grupo)


# Callback para facets por indicador SIH
@app.callback(
    Output("hospitalizations-sih-groups-content", "figure"),
    [Input("hospitalizations-sih-groups-modal", "is_open")],
    [State("hospitalizations-rm-sih", "value")]
)
def hospitalizations_sih_groups_modal(is_open, rm):
    if not is_open or not rm_list_sih or df_sih.empty:
        return go.Figure()
    return _sih_build_facets_by_indicator_figure(df_sih, df_sih_thresholds, rm)


# Callback para facets por RM SIH
@app.callback(
    Output("hospitalizations-sih-rms-content", "figure"),
    [Input("hospitalizations-sih-rms-modal", "is_open")],
    [State("hospitalizations-grupo-sih", "value")]
)
def hospitalizations_sih_rms_modal(is_open, grupo):
    if not is_open or not grupos_list_sih or df_sih.empty:
        return go.Figure()
    return _sih_build_facets_by_rm_figure(df_sih, df_sih_thresholds, grupo)


# Callbacks para controle dos modais SIH
@app.callback(
    Output("hospitalizations-sih-groups-modal", "is_open"),
    [Input("btn-hospitalizations-sih-groups", "n_clicks"), Input("btn-close-hospitalizations-sih-groups", "n_clicks")],
    [State("hospitalizations-sih-groups-modal", "is_open")]
)
def toggle_hospitalizations_sih_groups_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open


@app.callback(
    Output("hospitalizations-sih-rms-modal", "is_open"),
    [Input("btn-hospitalizations-sih-rms", "n_clicks"), Input("btn-close-hospitalizations-sih-rms", "n_clicks")],
    [State("hospitalizations-sih-rms-modal", "is_open")]
)
def toggle_hospitalizations_sih_rms_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open


@app.callback(
    Output("hospitalizations-sih-detailed-modal", "is_open"),
    [Input("btn-hospitalizations-sih-detailed", "n_clicks"), Input("btn-close-hospitalizations-sih-detailed", "n_clicks")],
    [State("hospitalizations-sih-detailed-modal", "is_open")]
)
def toggle_hospitalizations_sih_detailed_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open


@app.callback(
    Output("hospitalizations-srag-detailed-content", "children"),
    [Input("hospitalizations-srag-detailed-modal", "is_open")],
    [State("hospitalizations-rm-srag", "value")]
)
def hospitalizations_srag_detailed_content(is_open, rm):
    if not is_open or not rm:
        return html.Div()
    
    return html.Div([
        html.H5(f"Análise Detalhada SRAG - {rm}", className="text-center mb-4"),
        dbc.Row([
            dbc.Col([
                html.H6("Estatísticas Resumidas", className="mb-3"),
                html.Div(id="hospitalizations-srag-stats")
            ], width=6),
            dbc.Col([
                html.H6("Tendências Temporais", className="mb-3"),
                dcc.Loading(dcc.Graph(id="hospitalizations-srag-trends"))
            ], width=6)
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H6("Análise de Sazonalidade", className="mb-3"),
                dcc.Loading(dcc.Graph(id="hospitalizations-srag-seasonality"))
            ], width=12)
        ])
    ])


@app.callback(
    Output("hospitalizations-sih-detailed-content", "children"),
    [Input("hospitalizations-sih-detailed-modal", "is_open")],
    [State("hospitalizations-rm-sih", "value"), State("hospitalizations-grupo-sih", "value")]
)
def hospitalizations_sih_detailed_content(is_open, rm, grupo):
    if not is_open or not rm or not grupo:
        return html.Div()
    
    return html.Div([
        html.H5(f"Análise Detalhada SIH - {rm} - {grupo}", className="text-center mb-4"),
        dbc.Row([
            dbc.Col([
                html.H6("Estatísticas Resumidas", className="mb-3"),
                html.Div(id="hospitalizations-sih-stats")
            ], width=6),
            dbc.Col([
                html.H6("Comparação com Outros Grupos", className="mb-3"),
                dcc.Loading(dcc.Graph(id="hospitalizations-sih-comparison"))
            ], width=6)
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H6("Análise de Correlação com SRAG", className="mb-3"),
                dcc.Loading(dcc.Graph(id="hospitalizations-sih-correlation"))
            ], width=12)
        ])
    ])


@app.callback(
    Output("hospitalizations-advanced-modal-content", "children"),
    [Input("hospitalizations-advanced-modal", "is_open")],
    [Input("btn-hospitalizations-geographic", "n_clicks"),
     Input("btn-hospitalizations-export", "n_clicks")]
)
def hospitalizations_advanced_content(is_open, n_geographic, n_export):
    if not is_open:
        return html.Div()
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return html.Div([
            html.H5("Análises Avançadas", className="text-center mb-4"),
            html.P("Selecione uma análise avançada para visualizar.", className="text-center text-muted")
        ])
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "btn-hospitalizations-geographic":
        return html.Div([
            html.H5("Análise Geográfica", className="text-center mb-4"),
            dbc.Row([
                dbc.Col([
                    html.Div(id="hospitalizations-geographic-map")
                ], width=12)
            ])
        ])
    
    elif button_id == "btn-hospitalizations-export":
        return html.Div([
            html.H5("Exportar Dados", className="text-center mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H6("Opções de Exportação:", className="mb-3"),
                    dbc.ButtonGroup([
                        dbc.Button("Exportar SRAG (CSV)", id="btn-export-srag", color="primary", className="mb-2"),
                        dbc.Button("Exportar SIH (CSV)", id="btn-export-sih", color="secondary", className="mb-2"),
                        dbc.Button("Exportar Limiares (CSV)", id="btn-export-thresholds", color="info", className="mb-2"),
                        dbc.Button("Exportar Relatório (PDF)", id="btn-export-report", color="success", className="mb-2")
                    ], vertical=True, className="w-100")
                ], width=4),
                dbc.Col([
                    html.Div(id="export-status", className="text-center")
                ], width=8)
            ])
        ])
    
@app.callback(
    Output("hospitalizations-advanced-modal", "is_open"),
    [Input("btn-hospitalizations-geographic", "n_clicks"),
     Input("btn-hospitalizations-export", "n_clicks"),
     Input("btn-close-hospitalizations-advanced", "n_clicks")],
    [State("hospitalizations-advanced-modal", "is_open")]
)
def toggle_hospitalizations_advanced_modal(n_geographic, n_export, n_close, is_open):
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id.startswith("btn-hospitalizations-") and not button_id.endswith("-close"):
            return True
        elif button_id == "btn-close-hospitalizations-advanced":
            return False
    return is_open


# Callbacks para análises detalhadas SRAG
@app.callback(
    Output("hospitalizations-srag-stats", "children"),
    [Input("hospitalizations-srag-detailed-modal", "is_open")],
    [State("hospitalizations-rm-srag", "value")]
)
def hospitalizations_srag_stats(is_open, rm):
    if not is_open or not rm or df_srag.empty:
        return html.Div()
    
    dff = df_srag[df_srag["RM_nome"] == rm]
    if dff.empty:
        return html.Div("Nenhum dado disponível para esta RM.")
    
    stats = {
        "Total de Casos": int(dff["casos_totais"].sum()),
        "Média Mensal": round(dff["casos_totais"].mean(), 1),
        "Máximo Mensal": int(dff["casos_totais"].max()),
        "Período": f"{dff['ano'].min()} - {dff['ano'].max()}"
    }
    
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H6(f"{key}:", className="fw-bold"),
                html.P(f"{value}", className="mb-2")
            ])
        ], className="mb-2") for key, value in stats.items()
    ])


@app.callback(
    Output("hospitalizations-srag-trends", "figure"),
    [Input("hospitalizations-srag-detailed-modal", "is_open")],
    [State("hospitalizations-rm-srag", "value")]
)
def hospitalizations_srag_trends(is_open, rm):
    if not is_open or not rm or df_srag.empty:
        return go.Figure()
    
    dff = df_srag[df_srag["RM_nome"] == rm].copy()
    if dff.empty:
        return go.Figure()
    
    # Agrupa por ano para mostrar tendência anual
    yearly_data = dff.groupby("ano")["casos_totais"].sum().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yearly_data["ano"],
        y=yearly_data["casos_totais"],
        mode="lines+markers",
        name="Casos Anuais",
        line=dict(color="darkblue", width=3),
        marker=dict(size=8, color="black")
    ))
    
    fig.update_layout(
        title="Tendência Anual de Casos SRAG",
        xaxis_title="Ano",
        yaxis_title="Número de Casos",
        template="plotly_white"
    )
    
    return fig


@app.callback(
    Output("hospitalizations-srag-seasonality", "figure"),
    [Input("hospitalizations-srag-detailed-modal", "is_open")],
    [State("hospitalizations-rm-srag", "value")]
)
def hospitalizations_srag_seasonality(is_open, rm):
    if not is_open or not rm or df_srag.empty:
        return go.Figure()
    
    dff = df_srag[df_srag["RM_nome"] == rm].copy()
    if dff.empty:
        return go.Figure()
    
    # Análise de sazonalidade por mês usando mes_num
    monthly_data = dff.groupby("mes_num")["casos_totais"].mean().reset_index()
    
    # Mapeia números para nomes dos meses
    month_names = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
                   7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
    monthly_data["mes_nome"] = monthly_data["mes_num"].map(month_names)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_data["mes_nome"],
        y=monthly_data["casos_totais"],
        name="Média Mensal",
        marker_color="lightblue"
    ))
    
    fig.update_layout(
        title="Sazonalidade - Média de Casos por Mês",
        xaxis_title="Mês",
        yaxis_title="Número Médio de Casos",
        template="plotly_white"
    )
    
    return fig


# Callbacks para análises detalhadas SIH
@app.callback(
    Output("hospitalizations-sih-stats", "children"),
    [Input("hospitalizations-sih-detailed-modal", "is_open")],
    [State("hospitalizations-rm-sih", "value"), State("hospitalizations-grupo-sih", "value")]
)
def hospitalizations_sih_stats(is_open, rm, grupo):
    if not is_open or not rm or not grupo or df_sih.empty:
        return html.Div()
    
    dff = df_sih[(df_sih["RM"] == rm) & (df_sih["grupo"] == grupo)]
    if dff.empty:
        return html.Div("Nenhum dado disponível para esta combinação.")
    
    stats = {
        "Total de Casos": int(dff["casos_totais"].sum()),
        "Média Mensal": round(dff["casos_totais"].mean(), 1),
        "Máximo Mensal": int(dff["casos_totais"].max()),
        "Período": f"{dff['ano'].min()} - {dff['ano'].max()}"
    }
    
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H6(f"{key}:", className="fw-bold"),
                html.P(f"{value}", className="mb-2")
            ])
        ], className="mb-2") for key, value in stats.items()
    ])


@app.callback(
    Output("hospitalizations-sih-comparison", "figure"),
    [Input("hospitalizations-sih-detailed-modal", "is_open")],
    [State("hospitalizations-rm-sih", "value"), State("hospitalizations-grupo-sih", "value")]
)
def hospitalizations_sih_comparison(is_open, rm, grupo):
    if not is_open or not rm or not grupo or df_sih.empty:
        return go.Figure()
    
    dff = df_sih[df_sih["RM"] == rm].copy()
    if dff.empty:
        return go.Figure()
    
    # Compara com outros grupos da mesma RM
    grupos_comparacao = dff.groupby("grupo")["casos_totais"].sum().reset_index()
    grupos_comparacao = grupos_comparacao.sort_values("casos_totais", ascending=True)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grupos_comparacao["casos_totais"],
        y=grupos_comparacao["grupo"],
        orientation="h",
        name="Total de Casos",
        marker_color=["red" if g == grupo else "lightblue" for g in grupos_comparacao["grupo"]]
    ))
    
    fig.update_layout(
        title=f"Comparação de Grupos - {format_rm_name(rm)}",
        xaxis_title="Total de Casos",
        yaxis_title="Grupo de Diagnóstico",
        template="plotly_white",
        height=400
    )
    
    return fig


@app.callback(
    Output("hospitalizations-sih-correlation", "figure"),
    [Input("hospitalizations-sih-detailed-modal", "is_open")],
    [State("hospitalizations-rm-sih", "value"), State("hospitalizations-grupo-sih", "value")]
)
def hospitalizations_sih_correlation(is_open, rm, grupo):
    if not is_open or not rm or not grupo or df_sih.empty or df_srag.empty:
        return go.Figure()
    
    # Busca dados SIH
    dff_sih = df_sih[(df_sih["RM"] == rm) & (df_sih["grupo"] == grupo)].copy()
    if dff_sih.empty:
        return go.Figure()
    
    # Busca dados SRAG correspondentes - precisa mapear RM para RM_nome
    # Primeiro, vamos encontrar o RM_nome correspondente ao RM
    rm_mapping = {}
    if not df_srag.empty:
        for rm_nome in df_srag["RM_nome"].unique():
            # Tenta diferentes mapeamentos
            if rm in rm_nome or rm_nome in rm:
                rm_mapping[rm] = rm_nome
                break
    
    if rm not in rm_mapping:
        return go.Figure()
    
    dff_srag = df_srag[df_srag["RM_nome"] == rm_mapping[rm]].copy()
    if dff_srag.empty:
        return go.Figure()
    
    # Agrupa por ano para comparação
    sih_yearly = dff_sih.groupby("ano")["casos_totais"].sum().reset_index()
    srag_yearly = dff_srag.groupby("ano")["casos_totais"].sum().reset_index()
    
    # Merge dos dados
    merged = pd.merge(sih_yearly, srag_yearly, on="ano", suffixes=("_sih", "_srag"))
    
    if merged.empty:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=merged["casos_totais_srag"],
        y=merged["casos_totais_sih"],
        mode="markers+text",
        text=merged["ano"],
        textposition="top center",
        name="Correlação Anual",
        marker=dict(size=10, color="blue")
    ))
    
    fig.update_layout(
        title=f"Correlação SIH ({grupo}) vs SRAG - {format_rm_name(rm)}",
        xaxis_title="Casos SRAG",
        yaxis_title=f"Casos SIH ({grupo})",
        template="plotly_white"
    )
    
    return fig


# Callbacks para análises avançadas
@app.callback(
    Output("advanced-comparison-chart", "figure"),
    [Input("btn-generate-comparison", "n_clicks")],
    [State("advanced-comparison-rm", "value"), State("advanced-comparison-grupo", "value")]
)
def generate_advanced_comparison(n_clicks, rm, grupo):
    if not n_clicks or not rm or not grupo:
        return go.Figure()
    
    # Busca dados SRAG
    dff_srag = df_srag[df_srag["RM_nome"] == rm].copy()
    if dff_srag.empty:
        return go.Figure()
    
    # Busca dados SIH - precisa encontrar o RM correspondente
    sih_rm = None
    for sih_rm_candidate in df_sih["RM"].unique():
        if rm in sih_rm_candidate or sih_rm_candidate in rm:
            sih_rm = sih_rm_candidate
            break
    
    if not sih_rm:
        return go.Figure()
    
    dff_sih = df_sih[(df_sih["RM"] == sih_rm) & (df_sih["grupo"] == grupo)].copy()
    if dff_sih.empty:
        return go.Figure()
    
    # Agrupa por ano
    srag_yearly = dff_srag.groupby("ano")["casos_totais"].sum().reset_index()
    sih_yearly = dff_sih.groupby("ano")["casos_totais"].sum().reset_index()
    
    # Merge dos dados
    merged = pd.merge(srag_yearly, sih_yearly, on="ano", suffixes=("_srag", "_sih"))
    
    if merged.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    # Adiciona linha SRAG
    fig.add_trace(go.Scatter(
        x=merged["ano"],
        y=merged["casos_totais_srag"],
        mode="lines+markers",
        name="SRAG",
        line=dict(color="red", width=3),
        marker=dict(size=8)
    ))
    
    # Adiciona linha SIH
    fig.add_trace(go.Scatter(
        x=merged["ano"],
        y=merged["casos_totais_sih"],
        mode="lines+markers",
        name=f"SIH ({grupo})",
        line=dict(color="blue", width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f"Comparação SRAG vs SIH ({grupo}) - {format_rm_name(rm)}",
        xaxis_title="Ano",
        yaxis_title="Número de Casos",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


@app.callback(
    Output("hospitalizations-temporal-trends", "figure"),
    [Input("hospitalizations-advanced-modal", "is_open")]
)
def hospitalizations_temporal_trends(is_open):
    if not is_open:
        return go.Figure()
    
    fig = go.Figure()
    
    # Adiciona tendência SRAG se disponível
    if not df_srag.empty:
        srag_yearly = df_srag.groupby("ano")["casos_totais"].sum().reset_index()
        fig.add_trace(go.Scatter(
            x=srag_yearly["ano"],
            y=srag_yearly["casos_totais"],
            mode="lines+markers",
            name="SRAG Total",
            line=dict(color="red", width=3),
            marker=dict(size=6)
        ))
    
    # Adiciona tendência SIH se disponível
    if not df_sih.empty:
        sih_yearly = df_sih.groupby("ano")["casos_totais"].sum().reset_index()
        fig.add_trace(go.Scatter(
            x=sih_yearly["ano"],
            y=sih_yearly["casos_totais"],
            mode="lines+markers",
            name="SIH Total",
            line=dict(color="blue", width=3),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title="Tendências Temporais - SRAG vs SIH",
        xaxis_title="Ano",
        yaxis_title="Número de Casos",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


@app.callback(
    Output("hospitalizations-geographic-map", "children"),
    [Input("hospitalizations-advanced-modal", "is_open")]
)
def hospitalizations_geographic_map(is_open):
    if not is_open:
        return html.Div()
    
    # Coordenadas aproximadas das principais RMs brasileiras
    rm_coordinates = {
        "São Paulo": [-23.5505, -46.6333],
        "Rio de Janeiro": [-22.9068, -43.1729],
        "Belo Horizonte": [-19.9167, -43.9345],
        "Salvador": [-12.9714, -38.5014],
        "Fortaleza": [-3.7319, -38.5267],
        "Brasília": [-15.7801, -47.9292],
        "Manaus": [-3.1190, -60.0217],
        "Curitiba": [-25.4244, -49.2654],
        "Recife": [-8.0476, -34.8770],
        "Porto Alegre": [-30.0346, -51.2177],
        "Goiânia": [-16.6864, -49.2643],
        "Belém": [-1.4558, -48.5044],
        "Guarulhos": [-23.4538, -46.5333],
        "Campinas": [-22.9056, -47.0608],
        "São Luís": [-2.5297, -44.3028],
        "Florianópolis": [-27.5954, -48.5480],
        "Cuiabá": [-15.6014, -56.0979],
        "Porto Velho": [-8.7612, -63.9024],
        "RIDE DF": [-15.7801, -47.9292],
        "Grande Vitória": [-20.3155, -40.3128]
    }
    
    # Cria dados geográficos para SRAG
    geographic_data = []
    if not df_srag.empty:
        srag_by_rm = df_srag.groupby("RM_nome")["casos_totais"].sum().reset_index()
        for _, row in srag_by_rm.iterrows():
            rm_name = format_rm_name(row["RM_nome"])
            coords = rm_coordinates.get(rm_name, rm_coordinates.get(row["RM_nome"], [-15.0, -50.0]))
            geographic_data.append({
                "name": rm_name,
                "coordinates": coords,
                "cases": row["casos_totais"],
                "type": "SRAG"
            })
    
    # Cria o mapa interativo
    markers = []
    for data in geographic_data:
        markers.append(
            dl.Marker(
                position=data["coordinates"],
                children=[
                    dl.Tooltip(f"{data['name']}: {data['cases']:,} casos SRAG"),
                    dl.Popup([
                        html.H4(data["name"]),
                        html.P(f"Casos SRAG: {data['cases']:,}"),
                        html.P(f"Coordenadas: {data['coordinates'][0]:.4f}, {data['coordinates'][1]:.4f}")
                    ])
                ]
            )
        )
    
    return html.Div([
        html.H5("Mapa Interativo das Regiões Metropolitanas", className="text-center mb-3"),
        html.P("Clique nos marcadores para ver informações detalhadas sobre os casos SRAG por região.", className="text-center mb-3"),
        dl.Map([
            dl.TileLayer(),
            dl.LayerGroup(markers)
        ], 
        style={"width": "100%", "height": "500px"}, 
        center=[-15.0, -50.0], 
        zoom=4)
    ])



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    print(f"Iniciando servidor na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False) 