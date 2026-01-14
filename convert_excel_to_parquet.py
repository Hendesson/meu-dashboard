"""
Script para converter arquivos Excel para Parquet com otimização de tipos de dados.
"""
import pandas as pd
import numpy as np
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Otimiza os tipos de dados do DataFrame para reduzir uso de memória.
    """
    df = df.copy()
    
    # Otimiza colunas numéricas
    for col in df.select_dtypes(include=['int64']).columns:
        col_min = df[col].min()
        col_max = df[col].max()
        
        if col_min >= np.iinfo(np.int8).min and col_max <= np.iinfo(np.int8).max:
            df[col] = df[col].astype('int8')
        elif col_min >= np.iinfo(np.int16).min and col_max <= np.iinfo(np.int16).max:
            df[col] = df[col].astype('int16')
        elif col_min >= np.iinfo(np.int32).min and col_max <= np.iinfo(np.int32).max:
            df[col] = df[col].astype('int32')
    
    # Otimiza colunas float
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    
    # Converte strings para category quando apropriado
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() / len(df) < 0.5:  # Se menos de 50% valores únicos
            df[col] = df[col].astype('category')
    
    return df

def convert_excel_to_parquet(excel_path: str, output_dir: str = "processed") -> str:
    """
    Converte um arquivo Excel para Parquet com otimização.
    
    Args:
        excel_path: Caminho do arquivo Excel
        output_dir: Diretório de saída
        
    Returns:
        Caminho do arquivo Parquet gerado
    """
    if not os.path.exists(excel_path):
        logger.error(f"Arquivo não encontrado: {excel_path}")
        return None
    
    logger.info(f"Convertendo {excel_path} para Parquet...")
    
    # Lê o Excel
    try:
        df = pd.read_excel(excel_path)
        logger.info(f"Dados carregados: {df.shape}")
    except Exception as e:
        logger.error(f"Erro ao ler Excel: {e}")
        return None
    
    # Processa e otimiza
    if 'index' in df.columns:
        df['index'] = pd.to_datetime(df['index'], errors='coerce')
    
    if 'isHW' in df.columns:
        df['isHW'] = df['isHW'].apply(lambda x: str(x).upper())
    
    if 'index' in df.columns:
        df['year'] = df['index'].dt.year
        df['month'] = df['index'].dt.month
    
    # Filtra dados até 2023
    if 'year' in df.columns:
        df = df[df['year'] <= 2023]
    
    # Otimiza tipos
    df = optimize_dtypes(df)
    
    # Gera nome do arquivo de saída
    excel_name = Path(excel_path).stem
    parquet_path = os.path.join(output_dir, f"{excel_name}.parquet")
    
    # Cria diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Salva como Parquet
    try:
        df.to_parquet(parquet_path, engine='pyarrow', compression='snappy', index=False)
        logger.info(f"Arquivo salvo: {parquet_path}")
        logger.info(f"Tamanho original: {os.path.getsize(excel_path) / 1024 / 1024:.2f} MB")
        logger.info(f"Tamanho Parquet: {os.path.getsize(parquet_path) / 1024 / 1024:.2f} MB")
        return parquet_path
    except Exception as e:
        logger.error(f"Erro ao salvar Parquet: {e}")
        return None

def convert_csv_to_parquet(csv_path: str, output_dir: str = "processed", 
                          usecols: list = None, dtype: dict = None) -> str:
    """
    Converte um arquivo CSV para Parquet com otimização.
    
    Args:
        csv_path: Caminho do arquivo CSV
        output_dir: Diretório de saída
        usecols: Lista de colunas a carregar
        dtype: Dicionário de tipos de dados
        
    Returns:
        Caminho do arquivo Parquet gerado
    """
    if not os.path.exists(csv_path):
        logger.error(f"Arquivo não encontrado: {csv_path}")
        return None
    
    logger.info(f"Convertendo {csv_path} para Parquet...")
    
    try:
        # Lê apenas as colunas necessárias
        df = pd.read_csv(csv_path, usecols=usecols, dtype=dtype, encoding='utf-8', low_memory=True)
        logger.info(f"Dados carregados: {df.shape}")
    except Exception as e:
        logger.error(f"Erro ao ler CSV: {e}")
        return None
    
    # Otimiza tipos
    df = optimize_dtypes(df)
    
    # Gera nome do arquivo de saída
    csv_name = Path(csv_path).stem
    parquet_path = os.path.join(output_dir, f"{csv_name}.parquet")
    
    # Cria diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Salva como Parquet
    try:
        df.to_parquet(parquet_path, engine='pyarrow', compression='snappy', index=False)
        logger.info(f"Arquivo salvo: {parquet_path}")
        logger.info(f"Tamanho original: {os.path.getsize(csv_path) / 1024 / 1024:.2f} MB")
        logger.info(f"Tamanho Parquet: {os.path.getsize(parquet_path) / 1024 / 1024:.2f} MB")
        return parquet_path
    except Exception as e:
        logger.error(f"Erro ao salvar Parquet: {e}")
        return None

if __name__ == "__main__":
    # Converte arquivos Excel principais
    excel_files = [
        "temp.xlsx",
        "medias_HW_Severe_Extreme.xlsx",
        "banco_dados_climaticos_consolidado (2).xlsx"
    ]
    
    for excel_file in excel_files:
        if os.path.exists(excel_file):
            convert_excel_to_parquet(excel_file, "processed")
    
    # Converte CSVs principais
    csv_files = [
        ("RM_banco_SRAG.csv", ["RM", "RM_nome", "DT_INTERNA", "DT_SIN_PRI", "mes", "ano"], 
         {"RM": "category", "RM_nome": "category", "mes": "category", "ano": "Int64"}),
        ("serie_SIH_final.RData.csv", None, None),
        ("banco_dados_climaticos_consolidado (2).csv", None, None)
    ]
    
    for csv_file, usecols, dtype in csv_files:
        if os.path.exists(csv_file):
            convert_csv_to_parquet(csv_file, "processed", usecols, dtype)
    
    logger.info("Conversão concluída!")

