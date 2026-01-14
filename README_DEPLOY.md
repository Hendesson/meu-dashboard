# 🚀 Guia de Deploy no Render

Este projeto foi preparado para rodar no Render usando Gunicorn.

## ✅ Alterações Realizadas

### 1. Caminhos Relativos
- ✅ Criado `config_paths.py` com constantes `BASE_DIR` e `DATA_DIR`
- ✅ Todos os caminhos absolutos do Windows removidos
- ✅ Código usa `os.path.join()` para compatibilidade Windows/Linux

### 2. Estrutura de Pastas
- ✅ Criada pasta `data/` para arquivos de dados
- ✅ Pasta `processed/` para arquivos processados (Parquet)
- ✅ Pasta `cache/` para cache (gerado automaticamente)

### 3. Tratamento de Erros
- ✅ Try/except adicionado para arquivos ausentes
- ✅ Logging configurado para debug
- ✅ App não quebra se arquivos estiverem ausentes

### 4. Compatibilidade Gunicorn
- ✅ `server = app.server` exportado corretamente
- ✅ `Procfile` configurado: `gunicorn app:server --bind 0.0.0.0:$PORT`
- ✅ Porta via variável de ambiente `$PORT`

## 📋 Antes do Deploy

### 1. Organizar Arquivos de Dados

Execute o script para mover arquivos para `data/`:

```bash
python organize_data_files.py
```

Ou mova manualmente:
- `temp.xlsx` → `data/temp.xlsx`
- `RM_banco_SRAG.csv` → `data/RM_banco_SRAG.csv`
- `serie_SIH_final.RData.csv` → `data/serie_SIH_final.RData.csv`
- `mapa_interativo.html` → `data/mapa_interativo.html`

### 2. Verificar Arquivos Essenciais

Execute o teste de deploy:

```bash
python test_deploy.py
```

### 3. Converter para Parquet (Opcional mas Recomendado)

Para melhor performance:

```bash
python convert_excel_to_parquet.py
```

## 🔧 Configuração no Render

### 1. Criar Novo Web Service

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub

### 2. Configurações

- **Name**: `pibic-dash` (ou seu nome)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 120`

### 3. Variáveis de Ambiente (se necessário)

Render define automaticamente `$PORT`. Se precisar de outras variáveis:

- Adicione em "Environment" → "Environment Variables"

## 📁 Estrutura de Arquivos

```
pibic_dash/
├── app.py                    # Aplicação principal
├── data_processing.py        # Processamento de dados
├── visualization.py          # Visualizações
├── cache_manager.py          # Gerenciador de cache
├── config_paths.py           # ⭐ NOVO - Configuração de caminhos
├── requirements.txt          # Dependências
├── Procfile                  # Configuração Gunicorn
├── runtime.txt               # Versão Python (opcional)
├── data/                     # ⭐ NOVO - Arquivos de dados
│   ├── temp.xlsx
│   ├── RM_banco_SRAG.csv
│   ├── serie_SIH_final.RData.csv
│   └── mapa_interativo.html
├── assets/                   # Imagens e CSS
│   ├── *.png
│   ├── *.jpg
│   └── custom.css
├── processed/                # Gerado automaticamente
│   └── *.parquet
└── cache/                    # Gerado automaticamente
    └── *.pkl
```

## 🐛 Troubleshooting

### Erro: "Arquivo não encontrado"

1. Verifique se arquivos estão em `data/`
2. Execute `python organize_data_files.py`
3. Verifique logs no Render Dashboard

### Erro: "Module not found"

1. Verifique `requirements.txt`
2. Execute `pip install -r requirements.txt` localmente
3. Verifique se todas as dependências estão listadas

### Erro: "Port already in use"

- Render define `$PORT` automaticamente
- Não defina porta manualmente
- Verifique `Procfile` está correto

### App não inicia

1. Verifique logs no Render Dashboard
2. Execute `python test_deploy.py` localmente
3. Verifique se `server = app.server` está em `app.py`

## ✅ Checklist Final

- [ ] Arquivos de dados estão em `data/`
- [ ] `config_paths.py` está commitado
- [ ] `Procfile` está correto
- [ ] `server = app.server` está em `app.py`
- [ ] Sem caminhos absolutos do Windows
- [ ] `requirements.txt` está atualizado
- [ ] Testado localmente: `python app.py`
- [ ] Teste de deploy passou: `python test_deploy.py`

## 📝 Comandos Úteis

```bash
# Testar localmente
python app.py

# Testar com Gunicorn (simular Render)
gunicorn app:server --bind 0.0.0.0:8050

# Organizar arquivos
python organize_data_files.py

# Converter para Parquet
python convert_excel_to_parquet.py

# Testar configuração
python test_deploy.py
```

## 🔗 Links Úteis

- [Render Documentation](https://render.com/docs)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Dash Deployment](https://dash.plotly.com/deployment)

---

**Pronto para deploy!** 🎉

