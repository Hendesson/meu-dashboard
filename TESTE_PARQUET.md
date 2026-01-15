# 🧪 Como Testar se o Parquet Está Funcionando

## Teste Rápido

Execute este código Python para verificar se os dados estão corretos:

```python
import pandas as pd
from config_paths import PROCESSED_DIR, DATA_DIR
from data_processing import DataProcessor

# Teste 1: Verificar se Parquet existe e pode ser lido
parquet_path = f"{PROCESSED_DIR}/temp.parquet"
print("=" * 50)
print("TESTE 1: Verificar arquivo Parquet")
print("=" * 50)

if os.path.exists(parquet_path):
    df_parquet = pd.read_parquet(parquet_path, engine='pyarrow')
    print(f"✅ Parquet encontrado: {parquet_path}")
    print(f"   Shape: {df_parquet.shape}")
    print(f"   Colunas: {df_parquet.columns.tolist()}")
    print(f"   Tipos: {df_parquet.dtypes}")
    print(f"   Primeiras linhas:")
    print(df_parquet.head())
else:
    print(f"❌ Parquet não encontrado: {parquet_path}")

# Teste 2: Verificar DataProcessor
print("\n" + "=" * 50)
print("TESTE 2: Verificar DataProcessor")
print("=" * 50)

processor = DataProcessor()
df = processor.load_data()

print(f"✅ DataFrame carregado")
print(f"   Shape: {df.shape}")
print(f"   Cidades: {len(processor.cidades)}")
print(f"   Primeiras cidades: {processor.cidades[:5]}")
print(f"   Anos: {len(processor.anos)}")
print(f"   Primeiros anos: {processor.anos[:5]}")

# Teste 3: Verificar filtros
print("\n" + "=" * 50)
print("TESTE 3: Verificar Filtros")
print("=" * 50)

if processor.cidades:
    cidade_teste = processor.cidades[0]
    print(f"Testando filtro por cidade: {cidade_teste}")
    
    df_filtrado = df[df["cidade"] == cidade_teste]
    print(f"   Linhas encontradas: {len(df_filtrado)}")
    
    if len(df_filtrado) > 0:
        print(f"   ✅ Filtro funcionando!")
        print(f"   Primeiras linhas:")
        print(df_filtrado[["cidade", "index", "year", "tempMax", "tempMed", "tempMin"]].head())
    else:
        print(f"   ❌ Filtro não encontrou dados!")

if processor.anos:
    ano_teste = processor.anos[0]
    print(f"\nTestando filtro por ano: {ano_teste}")
    
    df_filtrado = df[df["year"] == ano_teste]
    print(f"   Linhas encontradas: {len(df_filtrado)}")
    
    if len(df_filtrado) > 0:
        print(f"   ✅ Filtro funcionando!")
    else:
        print(f"   ❌ Filtro não encontrou dados!")

# Teste 4: Verificar tipos de dados
print("\n" + "=" * 50)
print("TESTE 4: Verificar Tipos de Dados")
print("=" * 50)

print(f"   cidade dtype: {df['cidade'].dtype}")
print(f"   year dtype: {df['year'].dtype}")
print(f"   index dtype: {df['index'].dtype}")
print(f"   isHW dtype: {df['isHW'].dtype if 'isHW' in df.columns else 'N/A'}")

# Verificar se são category (não deve ser)
if df['cidade'].dtype == 'category':
    print("   ⚠️  ATENÇÃO: cidade é category! Deve ser string.")
else:
    print("   ✅ cidade não é category")

if df['year'].dtype == 'category':
    print("   ⚠️  ATENÇÃO: year é category! Deve ser int.")
else:
    print("   ✅ year não é category")

print("\n" + "=" * 50)
print("TESTE CONCLUÍDO")
print("=" * 50)
```

## O Que Verificar

### ✅ Se Está Funcionando:
- Parquet pode ser lido
- DataProcessor carrega dados
- Cidades e anos são extraídos
- Filtros funcionam (encontram dados)
- Tipos de dados estão corretos (não são category)

### ❌ Se Não Está Funcionando:
- Parquet não existe ou não pode ser lido
- DataFrame vazio após carregar
- Cidades ou anos vazios
- Filtros não encontram dados
- Tipos são category (deve ser string/int)

## Solução de Problemas

### Problema: Parquet não encontrado
**Solução:** Execute `python convert_excel_to_parquet.py`

### Problema: DataFrame vazio
**Solução:** Verifique se o arquivo Excel original tem dados

### Problema: Filtros não funcionam
**Solução:** Verifique se os tipos estão corretos (não category)

### Problema: Tipos são category
**Solução:** A correção no `data_processing.py` deve resolver isso

---

**Execute este teste para diagnosticar o problema!**

