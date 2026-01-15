# 🔧 Solução: Worker Timeout no Render

## Problema

O worker do gunicorn estava dando timeout após 2 minutos enquanto tentava carregar o arquivo Excel:

```
[CRITICAL] WORKER TIMEOUT (pid:43)
[ERROR] Worker (pid:43) was sent SIGKILL! Perhaps out of memory?
```

## Causa

1. **Arquivo Excel muito grande**: O arquivo `temp.xlsx` demora mais de 2 minutos para carregar
2. **Timeout muito curto**: O gunicorn estava configurado com timeout de 120 segundos (2 minutos)
3. **Possível falta de memória**: Arquivos Excel grandes consomem muita memória

## Soluções Aplicadas

### 1. Aumentado Timeout do Gunicorn

**Arquivo:** `Dockerfile`

**Mudança:**
- **Antes:** `--timeout 120` (2 minutos)
- **Depois:** `--timeout 300` (5 minutos)
- **Adicionado:** `--graceful-timeout 30` (30 segundos para finalizar graciosamente)

### 2. Otimizado Carregamento do Excel

**Arquivo:** `data_processing.py`

**Mudança:**
- Usa `engine='openpyxl'` explicitamente
- Adiciona tratamento de erro com fallback
- Melhora logs para debug

### 3. Recomendação: Converter para Parquet

O código já suporta Parquet, que é **muito mais rápido**:
- ✅ Carrega 10-100x mais rápido que Excel
- ✅ Usa menos memória
- ✅ Arquivo menor

## Como Converter para Parquet (Recomendado)

### Opção 1: Localmente (Antes do Deploy)

```powershell
cd C:\pibic_dash
python convert_excel_to_parquet.py
```

Isso vai criar `processed/temp.parquet` que é muito mais rápido.

### Opção 2: No Render (Após Deploy)

O código já detecta automaticamente se existe `processed/temp.parquet` e usa ele ao invés do Excel.

## Próximos Passos

### 1. Fazer Commit e Push

```powershell
cd C:\pibic_dash
git add Dockerfile data_processing.py
git commit -m "Fix: Aumentar timeout e otimizar carregamento Excel"
git push
```

### 2. Aguardar Deploy

O Render vai reconstruir automaticamente.

### 3. (Opcional) Converter para Parquet

Se quiser melhorar ainda mais a performance:

```powershell
# Localmente
python convert_excel_to_parquet.py

# Adicionar ao Git
git add processed/temp.parquet
git commit -m "Adicionar arquivo Parquet otimizado"
git push
```

## Resultado Esperado

Após as correções:

✅ **Timeout aumentado**: Agora tem 5 minutos para carregar  
✅ **Carregamento otimizado**: Excel carrega mais rápido  
✅ **Menos erros**: Worker não será morto prematuramente  

## Melhor Performance com Parquet

Se você converter para Parquet:

✅ **Carregamento instantâneo**: Parquet carrega em segundos  
✅ **Menos memória**: Arquivo otimizado  
✅ **Melhor experiência**: Usuário não espera tanto  

## Verificação

Após o deploy, verifique os logs:

1. **Deve carregar sem timeout:**
   ```
   [INFO] Arquivo encontrado, iniciando leitura...
   [INFO] Dados Excel lidos com sucesso. Shape: (...)
   ```

2. **Não deve mais ver:**
   ```
   [CRITICAL] WORKER TIMEOUT
   ```

3. **Dashboard deve funcionar:**
   - Acesse a URL do Render
   - Aguarde o carregamento (pode demorar 1-2 minutos na primeira vez)
   - Depois deve funcionar normalmente

## Se Ainda Tiver Problemas

### 1. Verificar Tamanho do Arquivo

```powershell
# Ver tamanho do arquivo
ls -lh data/temp.xlsx
```

Se for muito grande (> 100MB), considere:
- Converter para Parquet
- Dividir o arquivo
- Usar banco de dados

### 2. Aumentar Mais o Timeout

Se 5 minutos não for suficiente, pode aumentar para 600 (10 minutos):

```dockerfile
--timeout 600
```

### 3. Usar Parquet (Melhor Solução)

Parquet é a melhor solução:
- Muito mais rápido
- Menos memória
- Melhor para produção

---

**Após aplicar estas correções, o timeout não deve mais ocorrer! 🎉**

