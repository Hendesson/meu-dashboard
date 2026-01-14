# Guia de Otimização do Dashboard

Este documento descreve as otimizações implementadas no dashboard para melhorar desempenho, reduzir uso de memória e acelerar o tempo de inicialização.

## Estrutura de Pastas

O projeto agora utiliza uma estrutura organizada:

```
pibic_dash/
├── raw/              # Dados brutos originais (backup)
├── processed/         # Dados processados em formato Parquet
├── cache/            # Cache de dados processados
├── images/
│   └── webp/         # Imagens convertidas para WebP
└── assets/           # Assets originais (mantidos para compatibilidade)
```

## Otimizações Implementadas

### 1. Conversão de Excel para Parquet

- **Benefícios:**
  - Redução de 60-80% no tamanho dos arquivos
  - Leitura 5-10x mais rápida
  - Tipos de dados otimizados (int16, float32, category)

- **Como usar:**
  ```bash
  python convert_excel_to_parquet.py
  ```

### 2. Conversão de Imagens para WebP

- **Benefícios:**
  - Redução de 50-70% no tamanho das imagens
  - Carregamento mais rápido no navegador
  - Redimensionamento automático baseado no tipo de imagem

- **Como usar:**
  ```bash
  python convert_images_to_webp.py
  ```

### 3. Sistema de Cache

- **Benefícios:**
  - Evita recomputações desnecessárias
  - Reduz tempo de resposta em callbacks
  - Cache persistente em disco

- **Implementação:**
  - Cache automático para funções decoradas com `@cached_dataframe`
  - Cache em memória usando `lru_cache`
  - Cache em disco usando `joblib` para DataFrames grandes

### 4. Otimização de Tipos de Dados

- **Mudanças:**
  - `int64` → `int8/int16/int32` quando apropriado
  - `float64` → `float32` quando possível
  - `object` → `category` para strings repetidas

- **Resultado:**
  - Redução de 40-60% no uso de memória

### 5. Lazy Loading

- **Implementação:**
  - Dados carregados apenas quando necessário
  - Imagens WebP carregadas com fallback para originais
  - Cache de resultados intermediários

## Script de Inicialização

Execute uma vez para converter todos os dados e imagens:

```bash
python setup_optimization.py
```

Este script:
1. Converte todos os arquivos Excel para Parquet
2. Converte todos os CSVs principais para Parquet
3. Converte todas as imagens para WebP
4. Organiza os arquivos nas pastas apropriadas

## Uso Normal

Após a conversão inicial, o dashboard funciona normalmente:

```bash
python app.py
```

O sistema automaticamente:
- Usa arquivos Parquet quando disponíveis
- Usa imagens WebP quando disponíveis
- Aplica cache para operações repetidas
- Faz fallback para formatos originais se necessário

## Dependências Adicionais

As seguintes dependências foram adicionadas ao `requirements.txt`:

- `pyarrow>=14.0.0` - Para leitura/escrita de Parquet
- `joblib>=1.3.0` - Para cache eficiente de DataFrames
- `Pillow>=10.0.0` - Para conversão de imagens

Instale com:
```bash
pip install -r requirements.txt
```

## Melhorias de Desempenho Esperadas

- **Tempo de inicialização:** 50-70% mais rápido
- **Uso de memória:** 40-60% menor
- **Tempo de resposta:** 30-50% mais rápido em callbacks
- **Tamanho total do projeto:** 50-70% menor

## Manutenção

### Limpar Cache

Para limpar o cache e forçar recomputação:

```python
from cache_manager import cache_manager
cache_manager.clear()
```

### Atualizar Dados

Quando novos dados forem adicionados:

1. Coloque os arquivos originais em `raw/`
2. Execute `python convert_excel_to_parquet.py`
3. Os arquivos processados serão salvos em `processed/`

### Adicionar Novas Imagens

1. Coloque a imagem em `assets/`
2. Execute `python convert_images_to_webp.py`
3. A imagem WebP será criada em `images/webp/`

## Notas Importantes

- Os arquivos originais são mantidos para compatibilidade
- O sistema faz fallback automático se arquivos otimizados não existirem
- Cache é invalidado automaticamente quando arquivos são modificados
- Imagens WebP são copiadas para `assets/` automaticamente quando necessário

