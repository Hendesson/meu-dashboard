"""
Script para testar valores de isHW no DataFrame.
"""
import pandas as pd
from data_processing import DataProcessor
from config_paths import PROCESSED_DIR, DATA_DIR

print("=" * 70)
print("TESTE: Valores de isHW")
print("=" * 70)

# Carrega dados
processor = DataProcessor()
df = processor.load_data()

if df.empty:
    print("❌ DataFrame vazio!")
else:
    print(f"✅ DataFrame carregado: {df.shape}")
    
    if "isHW" in df.columns:
        print(f"\nColuna isHW encontrada!")
        print(f"  Tipo: {df['isHW'].dtype}")
        print(f"  Valores únicos: {df['isHW'].unique()}")
        print(f"  Contagem de valores:")
        print(df['isHW'].value_counts())
        
        # Testa diferentes comparações
        print(f"\nTestando comparações:")
        print(f"  isHW == 'TRUE': {len(df[df['isHW'] == 'TRUE'])} linhas")
        print(f"  isHW == 'true': {len(df[df['isHW'] == 'true'])} linhas")
        print(f"  isHW == True: {len(df[df['isHW'] == True])} linhas")
        print(f"  isHW == 1: {len(df[df['isHW'] == 1])} linhas")
        print(f"  isHW.astype(str).str.upper() == 'TRUE': {len(df[df['isHW'].astype(str).str.upper() == 'TRUE'])} linhas")
        
        # Verifica se há valores não-nulos
        print(f"\nValores não-nulos:")
        print(f"  Total não-nulo: {df['isHW'].notna().sum()}")
        print(f"  Total nulo: {df['isHW'].isna().sum()}")
        
        # Mostra algumas linhas de exemplo
        print(f"\nPrimeiras linhas com isHW:")
        if 'cidade' in df.columns and 'year' in df.columns:
            exemplo = df[['cidade', 'year', 'index', 'isHW']].head(10)
            print(exemplo)
            
        # Testa para uma cidade específica
        if processor.cidades:
            cidade_teste = processor.cidades[0]
            print(f"\nTestando para cidade: {cidade_teste}")
            df_cidade = df[df['cidade'] == cidade_teste]
            print(f"  Total de linhas: {len(df_cidade)}")
            print(f"  isHW == 'TRUE': {len(df_cidade[df_cidade['isHW'] == 'TRUE'])} linhas")
            print(f"  Valores únicos de isHW: {df_cidade['isHW'].unique()}")
    else:
        print("❌ Coluna isHW não encontrada!")
        print(f"Colunas disponíveis: {df.columns.tolist()}")

print("\n" + "=" * 70)

