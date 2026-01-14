# Lista de Arquivos para Deploy no Render

## ✅ Arquivos Obrigatórios (Devem estar no GitHub)

### Código Principal
- `app.py` - Aplicação principal Dash
- `data_processing.py` - Processamento de dados
- `visualization.py` - Visualizações
- `cache_manager.py` - Gerenciador de cache
- `config_paths.py` - **NOVO** - Configuração de caminhos

### Configuração
- `requirements.txt` - Dependências Python
- `Procfile` - Configuração Gunicorn
- `runtime.txt` - Versão Python (opcional)
- `render.yaml` - Configuração Render (opcional)

### Dados (pasta `data/`)
**IMPORTANTE:** Todos os arquivos de dados devem estar em `data/`

- `data/temp.xlsx` - Dados principais de temperatura
- `data/RM_banco_SRAG.csv` - Dados SRAG (se usado)
- `data/serie_SIH_final.RData.csv` - Dados SIH (se usado)
- `data/mapa_interativo.html` - Mapa interativo
- `data/medias_HW_Severe_Extreme.xlsx` - Dados de médias (se usado)
- `data/banco_dados_climaticos_consolidado (2).xlsx` - Dados consolidados (se usado)

### Assets (pasta `assets/`)
- `assets/*.png` - Todas as imagens PNG
- `assets/*.jpg` - Todas as imagens JPG
- `assets/*.jpeg` - Todas as imagens JPEG
- `assets/custom.css` - CSS customizado

### Arquivos Processados (pasta `processed/`)
**OPCIONAL:** Podem ser gerados automaticamente

- `processed/*.parquet` - Arquivos Parquet otimizados (gerados automaticamente)

### Scripts Auxiliares (Opcional)
- `convert_excel_to_parquet.py` - Conversão de dados
- `convert_images_to_webp.py` - Conversão de imagens
- `organize_data_files.py` - **NOVO** - Organiza arquivos para deploy
- `setup_optimization.py` - Setup de otimização

## ❌ Arquivos que NÃO devem estar no GitHub

### Cache
- `cache/*` - Cache gerado automaticamente
- `__pycache__/` - Cache Python

### Dados Originais (se já estão em data/)
- `temp.xlsx` (se já está em data/)
- `*.csv` na raiz (se já estão em data/)
- `*.xlsx` na raiz (se já estão em data/)

### Arquivos Temporários
- `*.tmp`
- `*.log`
- `*.bak`

### Arquivos de Sistema
- `.DS_Store`
- `Thumbs.db`
- `*.pyc`

## 📋 Checklist Antes do Deploy

- [ ] Todos os arquivos de dados estão em `data/`
- [ ] `config_paths.py` está commitado
- [ ] `requirements.txt` está atualizado
- [ ] `Procfile` está correto: `web: gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
- [ ] `server = app.server` está em `app.py`
- [ ] Não há caminhos absolutos do Windows (`C:\...`)
- [ ] `.gitignore` está configurado corretamente
- [ ] Testado localmente: `python app.py`

## 🚀 Comandos para Preparar Deploy

```bash
# 1. Organizar arquivos de dados
python organize_data_files.py

# 2. Converter para Parquet (opcional, mas recomendado)
python convert_excel_to_parquet.py

# 3. Verificar estrutura
ls -la data/
ls -la assets/

# 4. Testar localmente
python app.py

# 5. Commit e push
git add .
git commit -m "Preparado para deploy no Render"
git push
```

## ⚠️ Importante

1. **Arquivos grandes:** Se arquivos Excel/CSV forem muito grandes (>100MB), considere usar Git LFS ou converter para Parquet primeiro
2. **Variáveis de ambiente:** Render permite configurar variáveis de ambiente se necessário
3. **Logs:** Verifique logs no Render se houver problemas
4. **Porta:** Render define automaticamente a variável `$PORT`

## 📁 Estrutura Final Esperada

```
pibic_dash/
├── app.py
├── data_processing.py
├── visualization.py
├── cache_manager.py
├── config_paths.py          # NOVO
├── requirements.txt
├── Procfile
├── runtime.txt
├── data/                    # NOVO - Todos os dados aqui
│   ├── temp.xlsx
│   ├── RM_banco_SRAG.csv
│   ├── serie_SIH_final.RData.csv
│   └── mapa_interativo.html
├── assets/                  # Imagens e CSS
│   ├── *.png
│   ├── *.jpg
│   └── custom.css
├── processed/               # Gerado automaticamente
│   └── *.parquet
└── cache/                   # Gerado automaticamente
    └── *.pkl
```

