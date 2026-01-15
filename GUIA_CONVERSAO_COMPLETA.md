# 📦 Guia: Converter TODOS os Arquivos para Parquet

## Por Que Converter Tudo?

O dashboard usa vários arquivos Excel e CSV. Convertendo todos para Parquet:
- ✅ **10-100x mais rápido** para carregar
- ✅ **Menos memória** usada
- ✅ **Melhor performance** no Render
- ✅ **Sem timeouts** no carregamento

## Arquivos que Precisam ser Convertidos

### Arquivos Excel:
1. ✅ `temp.xlsx` - Dados principais de temperatura (JÁ CONVERTIDO)
2. ⚠️ `medias_HW_Severe_Extreme.xlsx` - Médias de ondas de calor
3. ⚠️ `banco_dados_climaticos_consolidado (2).xlsx` - Dados consolidados
4. ⚠️ `temp1.xlsx` - Se existir

### Arquivos CSV:
1. ✅ `RM_banco_SRAG.csv` - Dados SRAG (já tem suporte Parquet no código)
2. ✅ `serie_SIH_final.RData.csv` - Dados SIH (já tem suporte Parquet no código)
3. ⚠️ `banco_dados_climaticos_consolidado (2).csv` - Dados consolidados CSV

## Como Converter TUDO

### Opção 1: Script Completo (Recomendado)

```powershell
python converter_todos_arquivos.py
```

Este script:
- ✅ Converte TODOS os arquivos Excel
- ✅ Converte TODOS os arquivos CSV
- ✅ Mostra resumo do que foi convertido
- ✅ Lista arquivos Parquet gerados

### Opção 2: Script Original

```powershell
python convert_excel_to_parquet.py
```

Converte os arquivos principais, mas pode não incluir todos.

## Verificar Conversão

Após converter, verifique se os arquivos foram criados:

```powershell
dir processed\*.parquet
```

Você deve ver:
- ✅ `temp.parquet`
- ✅ `medias_HW_Severe_Extreme.parquet` (se o arquivo existir)
- ✅ `banco_dados_climaticos_consolidado (2).parquet` (se o arquivo existir)
- ✅ `RM_banco_SRAG.parquet` (se o CSV foi convertido)
- ✅ `serie_SIH_final.RData.parquet` (se o CSV foi convertido)

## Após Converter

### 1. Limpar Cache

```powershell
python limpar_cache.py
```

### 2. Reiniciar App

```powershell
python app.py
```

### 3. Verificar Logs

Você deve ver nos logs:
- "Usando arquivo Parquet: ..." (não Excel!)
- "Dados Parquet lidos com sucesso"
- Carregamento muito mais rápido

## Status do Suporte Parquet no Código

### ✅ Já Suportam Parquet:
- `temp.xlsx` → `temp.parquet` (DataProcessor)
- `RM_banco_SRAG.csv` → `RM_banco_SRAG.parquet` (load_srag_series)
- `serie_SIH_final.RData.csv` → `serie_SIH_final.RData.parquet` (load_sih_series)

### ⚠️ Ainda Não Suportam (mas podem ser convertidos):
- `medias_HW_Severe_Extreme.xlsx` - Se usado, precisa adicionar suporte no código
- `banco_dados_climaticos_consolidado (2).xlsx` - Se usado, precisa adicionar suporte no código

## Se Algum Arquivo Não For Encontrado

O script vai avisar:
```
⚠️ Não encontrado: nome_arquivo.xlsx
```

Isso é normal se o arquivo não existir ou não for usado. O importante é que os arquivos principais (`temp.xlsx`, `RM_banco_SRAG.csv`, `serie_SIH_final.RData.csv`) sejam convertidos.

## Benefícios Após Conversão

### Antes (Excel):
- ⏱️ Carregamento: 2-5 minutos
- 💾 Memória: Alta
- ⚠️ Timeout no Render: Possível

### Depois (Parquet):
- ⏱️ Carregamento: 5-10 segundos
- 💾 Memória: Baixa
- ✅ Sem timeout no Render

## Troubleshooting

### Erro: "Missing optional dependency 'pyarrow'"
```powershell
pip install pyarrow
```

### Erro: "Arquivo não encontrado"
- Verifique se os arquivos estão em `data/`
- Execute `python organize_data_files.py` se necessário

### Parquet não é usado
- Limpe o cache: `python limpar_cache.py`
- Verifique se o arquivo Parquet existe em `processed/`
- Reinicie o app

---

**Execute `python converter_todos_arquivos.py` para converter tudo de uma vez! 🚀**

