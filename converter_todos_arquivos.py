"""
Script para converter TODOS os arquivos Excel e CSV para Parquet.
Garante que todos os arquivos usados no dashboard sejam convertidos.
"""
import os
import pandas as pd
from pathlib import Path
import logging
from config_paths import DATA_DIR, PROCESSED_DIR
from convert_excel_to_parquet import convert_excel_to_parquet, convert_csv_to_parquet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def converter_todos_arquivos():
    """Converte todos os arquivos Excel e CSV para Parquet."""
    print("=" * 70)
    print("CONVERSÃO COMPLETA: Todos os arquivos para Parquet")
    print("=" * 70)
    
    # Lista completa de arquivos Excel
    excel_files = [
        "temp.xlsx",  # Principal - dados de temperatura
        "medias_HW_Severe_Extreme.xlsx",  # Médias de ondas de calor
        "banco_dados_climaticos_consolidado (2).xlsx",  # Dados consolidados
        "temp1.xlsx",  # Se existir
    ]
    
    print("\n1. CONVERTENDO ARQUIVOS EXCEL")
    print("-" * 70)
    excel_convertidos = 0
    excel_nao_encontrados = []
    
    for excel_file in excel_files:
        # Tenta em DATA_DIR primeiro
        excel_path = os.path.join(DATA_DIR, excel_file)
        if not os.path.exists(excel_path):
            excel_path = excel_file  # Fallback para raiz
        
        if os.path.exists(excel_path):
            print(f"\n📄 Convertendo: {excel_file}")
            resultado = convert_excel_to_parquet(excel_path)
            if resultado:
                excel_convertidos += 1
                print(f"   ✅ Convertido com sucesso!")
            else:
                print(f"   ❌ Erro na conversão")
        else:
            excel_nao_encontrados.append(excel_file)
            print(f"   ⚠️  Não encontrado: {excel_file}")
    
    # Lista completa de arquivos CSV
    csv_files = [
        ("RM_banco_SRAG.csv", ["RM", "RM_nome", "DT_INTERNA", "DT_SIN_PRI", "mes", "ano"], 
         {"RM": "category", "RM_nome": "category", "mes": "category", "ano": "Int64"}),
        ("serie_SIH_final.RData.csv", None, None),
        ("banco_dados_climaticos_consolidado (2).csv", None, None)
    ]
    
    print("\n2. CONVERTENDO ARQUIVOS CSV")
    print("-" * 70)
    csv_convertidos = 0
    csv_nao_encontrados = []
    
    for csv_file, usecols, dtype in csv_files:
        # Tenta em DATA_DIR primeiro
        csv_path = os.path.join(DATA_DIR, csv_file)
        if not os.path.exists(csv_path):
            csv_path = csv_file  # Fallback para raiz
        
        if os.path.exists(csv_path):
            print(f"\n📄 Convertendo: {csv_file}")
            resultado = convert_csv_to_parquet(csv_path, None, usecols, dtype)
            if resultado:
                csv_convertidos += 1
                print(f"   ✅ Convertido com sucesso!")
            else:
                print(f"   ❌ Erro na conversão")
        else:
            csv_nao_encontrados.append(csv_file)
            print(f"   ⚠️  Não encontrado: {csv_file}")
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO DA CONVERSÃO")
    print("=" * 70)
    print(f"✅ Excel convertidos: {excel_convertidos}/{len(excel_files)}")
    if excel_nao_encontrados:
        print(f"   ⚠️  Não encontrados: {', '.join(excel_nao_encontrados)}")
    
    print(f"✅ CSV convertidos: {csv_convertidos}/{len(csv_files)}")
    if csv_nao_encontrados:
        print(f"   ⚠️  Não encontrados: {', '.join(csv_nao_encontrados)}")
    
    # Lista arquivos Parquet gerados
    print("\n3. ARQUIVOS PARQUET GERADOS")
    print("-" * 70)
    if os.path.exists(PROCESSED_DIR):
        parquet_files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith('.parquet')]
        if parquet_files:
            for parquet_file in sorted(parquet_files):
                parquet_path = os.path.join(PROCESSED_DIR, parquet_file)
                tamanho_mb = os.path.getsize(parquet_path) / 1024 / 1024
                print(f"   ✅ {parquet_file} ({tamanho_mb:.2f} MB)")
        else:
            print("   ⚠️  Nenhum arquivo Parquet encontrado")
    else:
        print("   ⚠️  Diretório processed/ não existe")
    
    print("\n" + "=" * 70)
    print("CONVERSÃO CONCLUÍDA!")
    print("=" * 70)
    print("\nPróximos passos:")
    print("1. Limpe o cache: python limpar_cache.py")
    print("2. Reinicie o app: python app.py")
    print("3. Os dados agora serão carregados do Parquet (muito mais rápido!)")

if __name__ == "__main__":
    converter_todos_arquivos()

