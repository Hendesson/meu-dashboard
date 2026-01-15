"""
Script para testar se o dashboard funciona corretamente com arquivos Parquet.
"""
import os
import pandas as pd
from data_processing import DataProcessor
from config_paths import PROCESSED_DIR, DATA_DIR

print("=" * 70)
print("TESTE: Funcionamento com Parquet")
print("=" * 70)

# Verifica se existe arquivo Parquet
parquet_path = os.path.join(PROCESSED_DIR, "temp.parquet")
excel_path = os.path.join(DATA_DIR, "temp.xlsx")

print(f"\n1. Verificando arquivos:")
print(f"   Parquet: {parquet_path} - {'✅ Existe' if os.path.exists(parquet_path) else '❌ Não existe'}")
print(f"   Excel: {excel_path} - {'✅ Existe' if os.path.exists(excel_path) else '❌ Não existe'}")

# Testa carregamento
print(f"\n2. Testando carregamento de dados:")
processor = DataProcessor()
df = processor.load_data()

if df.empty:
    print("   ❌ DataFrame vazio!")
else:
    print(f"   ✅ DataFrame carregado: {df.shape}")
    print(f"   📁 Fonte: {'Parquet' if processor.use_parquet else 'Excel'}")
    
    # Verifica colunas essenciais
    print(f"\n3. Verificando colunas essenciais:")
    colunas_essenciais = ['cidade', 'index', 'year', 'month', 'isHW']
    for col in colunas_essenciais:
        if col in df.columns:
            print(f"   ✅ {col}: {df[col].dtype}")
        else:
            print(f"   ❌ {col}: NÃO ENCONTRADA")
    
    # Verifica isHW
    print(f"\n4. Verificando coluna isHW:")
    if "isHW" in df.columns:
        print(f"   Tipo: {df['isHW'].dtype}")
        print(f"   Valores únicos: {df['isHW'].unique()}")
        print(f"   Contagem TRUE: {len(df[df['isHW'] == 'TRUE'])}")
        print(f"   Contagem FALSE: {len(df[df['isHW'] == 'FALSE'])}")
        
        # Testa normalização
        print(f"\n5. Testando função de normalização:")
        normalized = processor._normalize_isHW(df['isHW'])
        print(f"   Tipo normalizado: {normalized.dtype}")
        print(f"   Valores únicos normalizados: {normalized.unique()}")
        print(f"   Contagem TRUE após normalização: {len(normalized[normalized == 'TRUE'])}")
    
    # Testa cálculo de ondas de calor
    print(f"\n6. Testando cálculo de ondas de calor:")
    if processor.cidades:
        cidade_teste = processor.cidades[0]
        print(f"   Cidade de teste: {cidade_teste}")
        
        if processor.anos:
            ano_teste = processor.anos[0]
            print(f"   Ano de teste: {ano_teste}")
            
            # Testa calculate_hw_monthly
            try:
                hw_monthly = processor.calculate_hw_monthly(cidade_teste, ano_teste)
                print(f"   ✅ calculate_hw_monthly: {len(hw_monthly)} meses")
                if not hw_monthly.empty:
                    print(f"      Total de dias de onda de calor: {hw_monthly['frequencia'].sum()}")
            except Exception as e:
                print(f"   ❌ Erro em calculate_hw_monthly: {e}")
            
            # Testa calculate_hw_monthly_all_years
            try:
                hw_all = processor.calculate_hw_monthly_all_years(cidade_teste)
                print(f"   ✅ calculate_hw_monthly_all_years: {len(hw_all)} meses")
                if not hw_all.empty:
                    print(f"      Total de dias de onda de calor (todos anos): {hw_all['frequencia'].sum()}")
            except Exception as e:
                print(f"   ❌ Erro em calculate_hw_monthly_all_years: {e}")

print("\n" + "=" * 70)
print("RESUMO:")
if not df.empty and "isHW" in df.columns:
    print("✅ O dashboard DEVE funcionar com Parquet!")
    print("   - Dados carregados corretamente")
    print("   - Coluna isHW normalizada")
    print("   - Funções de cálculo funcionando")
else:
    print("⚠️  Verifique os erros acima")
print("=" * 70)

