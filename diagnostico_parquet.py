"""
Script de diagnóstico para verificar problemas com Parquet.
"""
import pandas as pd
import os
from config_paths import PROCESSED_DIR, DATA_DIR
from data_processing import DataProcessor

print("=" * 70)
print("DIAGNÓSTICO: Problema com Parquet e Gráficos Vazios")
print("=" * 70)

# 1. Verificar arquivo Parquet
print("\n1. VERIFICANDO ARQUIVO PARQUET")
print("-" * 70)
parquet_path = os.path.join(PROCESSED_DIR, "temp.parquet")
if os.path.exists(parquet_path):
    print(f"✅ Parquet encontrado: {parquet_path}")
    df_parquet = pd.read_parquet(parquet_path, engine='pyarrow')
    print(f"   Shape: {df_parquet.shape}")
    print(f"   Colunas: {df_parquet.columns.tolist()}")
    print(f"\n   TIPOS DE DADOS:")
    for col in ['cidade', 'year', 'index', 'isHW']:
        if col in df_parquet.columns:
            print(f"     {col}: {df_parquet[col].dtype}")
    print(f"\n   VALORES ÚNICOS:")
    if 'cidade' in df_parquet.columns:
        print(f"     Cidades (primeiras 5): {df_parquet['cidade'].unique()[:5].tolist()}")
    if 'year' in df_parquet.columns:
        anos = sorted([int(x) for x in df_parquet['year'].unique() if pd.notna(x)])[:5]
        print(f"     Anos (primeiros 5): {anos}")
else:
    print(f"❌ Parquet NÃO encontrado: {parquet_path}")

# 2. Testar DataProcessor
print("\n2. TESTANDO DATAPROCESSOR")
print("-" * 70)
processor = DataProcessor()
df = processor.load_data()

print(f"✅ DataFrame carregado")
print(f"   Shape: {df.shape}")
print(f"   Cidades: {len(processor.cidades)}")
print(f"   Primeiras cidades: {processor.cidades[:5]}")
print(f"   Anos: {len(processor.anos)}")
print(f"   Primeiros anos: {processor.anos[:5]}")

# 3. Verificar tipos após processamento
print("\n3. VERIFICANDO TIPOS APÓS PROCESSAMENTO")
print("-" * 70)
print(f"   cidade dtype: {df['cidade'].dtype}")
print(f"   year dtype: {df['year'].dtype}")
print(f"   index dtype: {df['index'].dtype}")
if 'isHW' in df.columns:
    print(f"   isHW dtype: {df['isHW'].dtype}")

# Verificar se são category (não deve ser)
problemas = []
if df['cidade'].dtype == 'category':
    problemas.append("❌ cidade ainda é category!")
else:
    print("   ✅ cidade não é category")

if df['year'].dtype == 'category':
    problemas.append("❌ year ainda é category!")
else:
    print("   ✅ year não é category")

# 4. Testar filtros
print("\n4. TESTANDO FILTROS")
print("-" * 70)
if processor.cidades:
    cidade_teste = processor.cidades[0]
    print(f"   Testando filtro por cidade: '{cidade_teste}'")
    print(f"   Tipo da cidade: {type(cidade_teste)}")
    
    # Verificar valores exatos
    cidades_unicas = df['cidade'].unique()
    print(f"   Valores únicos de cidade (primeiros 3): {cidades_unicas[:3].tolist()}")
    
    # Testar filtro
    df_filtrado = df[df["cidade"] == cidade_teste]
    print(f"   Linhas encontradas: {len(df_filtrado)}")
    
    if len(df_filtrado) > 0:
        print(f"   ✅ Filtro por cidade funcionando!")
        print(f"   Primeiras linhas:")
        print(df_filtrado[["cidade", "index", "year", "tempMax"]].head(3))
    else:
        print(f"   ❌ Filtro por cidade NÃO encontrou dados!")
        print(f"   Tentando busca case-insensitive...")
        df_filtrado_ci = df[df["cidade"].str.upper() == cidade_teste.upper()]
        print(f"   Linhas encontradas (case-insensitive): {len(df_filtrado_ci)}")

if processor.anos:
    ano_teste = processor.anos[0]
    print(f"\n   Testando filtro por ano: {ano_teste}")
    
    df_filtrado = df[df["year"] == ano_teste]
    print(f"   Linhas encontradas: {len(df_filtrado)}")
    
    if len(df_filtrado) > 0:
        print(f"   ✅ Filtro por ano funcionando!")
    else:
        print(f"   ❌ Filtro por ano NÃO encontrou dados!")

# 5. Testar filtro combinado (como nas visualizações)
print("\n5. TESTANDO FILTRO COMBINADO (como nas visualizações)")
print("-" * 70)
if processor.cidades and processor.anos:
    cidade_teste = processor.cidades[0]
    ano_inicio = processor.anos[0]
    ano_fim = processor.anos[-1] if len(processor.anos) > 1 else processor.anos[0]
    
    print(f"   Cidade: '{cidade_teste}'")
    print(f"   Anos: {ano_inicio} - {ano_fim}")
    
    dff = df[
        (df["cidade"] == cidade_teste) & 
        (df["year"] >= ano_inicio) & 
        (df["year"] <= ano_fim)
    ]
    
    print(f"   Linhas encontradas: {len(dff)}")
    
    if len(dff) > 0:
        print(f"   ✅ Filtro combinado funcionando!")
        print(f"   Colunas disponíveis: {dff.columns.tolist()}")
        if 'tempMax' in dff.columns:
            print(f"   ✅ Coluna tempMax existe")
        else:
            print(f"   ❌ Coluna tempMax NÃO existe!")
    else:
        print(f"   ❌ Filtro combinado NÃO encontrou dados!")
        print(f"   Verificando filtros individuais:")
        print(f"     Apenas cidade: {len(df[df['cidade'] == cidade_teste])}")
        print(f"     Apenas ano: {len(df[(df['year'] >= ano_inicio) & (df['year'] <= ano_fim)])}")

# 6. Resumo
print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)
if problemas:
    print("⚠️ PROBLEMAS ENCONTRADOS:")
    for problema in problemas:
        print(f"   {problema}")
else:
    print("✅ Nenhum problema óbvio encontrado")
    print("   Se os gráficos ainda estão vazios, verifique:")
    print("   - Se as colunas tempMax, tempMed, tempMin existem")
    print("   - Se há valores NaN nessas colunas")
    print("   - Se os filtros estão retornando dados")

print("\n" + "=" * 70)

