# Guia: Deploy Gratuito do Dashboard + Integração Joomla

Este guia mostra como colocar seu dashboard online de forma **100% gratuita** e integrá-lo no Joomla.

## 🎯 Opções Gratuitas de Hospedagem

### Opção 1: Render.com (⭐ RECOMENDADO - Mais Fácil)

**Vantagens:**
- ✅ 100% gratuito
- ✅ Deploy automático via GitHub
- ✅ HTTPS automático
- ✅ Sem cartão de crédito
- ✅ 750 horas/mês grátis

**Passo a Passo:**

1. **Crie conta no GitHub** (se não tiver):
   - Acesse: https://github.com
   - Crie uma conta gratuita

2. **Envie seu código para o GitHub:**
   ```bash
   # No terminal, na pasta do projeto
   git init
   git add .
   git commit -m "Dashboard de Ondas de Calor"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/pibic-dash.git
   git push -u origin main
   ```

3. **Crie conta no Render:**
   - Acesse: https://render.com
   - Faça login com GitHub

4. **Crie novo Web Service:**
   - Clique em "New +" → "Web Service"
   - Conecte seu repositório GitHub
   - Configure:
     - **Name:** `dashboard-ondas-calor`
     - **Environment:** `Python 3`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:server --host 0.0.0.0 --port $PORT`
     - **Plan:** Free

5. **Clique em "Create Web Service"**

6. **Aguarde o deploy** (5-10 minutos)

7. **Sua URL será:** `https://dashboard-ondas-calor.onrender.com`

**⚠️ Nota:** Render "dorme" após 15min de inatividade. Primeira requisição pode demorar ~30s.

---

### Opção 2: Railway.app (⭐ Alternativa Excelente)

**Vantagens:**
- ✅ $5 grátis/mês (suficiente para dashboard)
- ✅ Deploy automático
- ✅ HTTPS automático
- ✅ Sem dormir (mais rápido)

**Passo a Passo:**

1. **Acesse:** https://railway.app
2. **Login com GitHub**
3. **"New Project" → "Deploy from GitHub repo"**
4. **Selecione seu repositório**
5. **Railway detecta automaticamente Python**
6. **Configure variáveis (se necessário):**
   - `PORT` (geralmente automático)
7. **Deploy automático!**

**Sua URL será:** `https://seu-projeto.up.railway.app`

---

### Opção 3: PythonAnywhere (⭐ Bom para Iniciantes)

**Vantagens:**
- ✅ Plano gratuito disponível
- ✅ Interface web simples
- ✅ Suporte Python direto

**Passo a Passo:**

1. **Crie conta:** https://www.pythonanywhere.com
2. **Vá em "Files" → Upload seus arquivos**
3. **Vá em "Web" → "Add a new web app"**
4. **Escolha "Manual configuration" → Python 3.9**
5. **Edite o arquivo WSGI:**
   ```python
   import sys
   path = '/home/seuusuario/pibic_dash'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import server as application
   ```
6. **Configure URL:** `seuusuario.pythonanywhere.com`

---

### Opção 4: Fly.io (⭐ Para Apps Mais Complexos)

**Vantagens:**
- ✅ 3 VMs grátis
- ✅ Deploy rápido
- ✅ Bom para produção

**Passo a Passo:**

1. **Instale Fly CLI:**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Crie arquivo `fly.toml`:**
   ```toml
   app = "seu-dashboard"
   primary_region = "gru"  # São Paulo
   
   [build]
   
   [http_service]
     internal_port = 8050
     force_https = true
     auto_stop_machines = true
     auto_start_machines = true
     min_machines_running = 0
   
   [[services]]
     protocol = "tcp"
     internal_port = 8050
   ```

4. **Deploy:**
   ```bash
   fly launch
   fly deploy
   ```

---

## 🔧 Preparar Projeto para Deploy

### 1. Criar arquivo `runtime.txt` (já existe, verifique versão):

```txt
python-3.9.18
```

### 2. Atualizar `Procfile` (já existe):

```txt
web: gunicorn app:server --workers 1 --timeout 120 --bind 0.0.0.0:$PORT
```

### 3. Criar `.gitignore` (se não existir):

```gitignore
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
*.xlsx
*.xls
*.csv
cache/
*.pkl
.DS_Store
*.log
```

### 4. Criar `render.yaml` (para Render.com):

```yaml
services:
  - type: web
    name: dashboard-ondas-calor
    env: python
    buildCommand: pip install -r requirements.txt && python setup_optimization.py
    startCommand: gunicorn app:server --host 0.0.0.0 --port $PORT --workers 1 --timeout 120
    envVars:
      - key: PORT
        value: 8050
      - key: PYTHON_VERSION
        value: 3.9.18
```

---

## 📝 Integração no Joomla (Após Deploy)

### Passo 1: Obter URL do Dashboard

Após deploy, você terá uma URL como:
- `https://dashboard-ondas-calor.onrender.com`
- `https://seu-projeto.up.railway.app`
- etc.

### Passo 2: Inserir no Joomla

1. **Acesse Joomla Admin**
2. **Conteúdo → Artigos → Novo Artigo**
3. **No editor, clique em "Código-fonte" (HTML)**
4. **Cole este código:**

```html
<div style="width: 100%; margin: 20px 0;">
    <iframe 
        src="https://SUA-URL-AQUI.onrender.com" 
        width="100%" 
        height="900px" 
        frameborder="0"
        style="border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px;"
        allowfullscreen
        loading="lazy">
        <p>Seu navegador não suporta iframes. 
        <a href="https://SUA-URL-AQUI.onrender.com" target="_blank">
            Acesse o dashboard diretamente
        </a>.</p>
    </iframe>
</div>
```

**Substitua `SUA-URL-AQUI` pela URL real do seu dashboard!**

### Passo 3: Versão Responsiva (Recomendada)

Para melhor visualização em mobile:

```html
<div style="position: relative; width: 100%; padding-bottom: 75%; height: 0; overflow: hidden; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px;">
    <iframe 
        src="https://SUA-URL-AQUI.onrender.com" 
        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
        allowfullscreen
        loading="lazy"
        title="Dashboard de Ondas de Calor">
    </iframe>
</div>
```

---

## 🚀 Deploy Rápido (Render.com - Recomendado)

### Script Automatizado:

```bash
# 1. Inicializar Git (se ainda não fez)
git init
git add .
git commit -m "Dashboard de Ondas de Calor"

# 2. Criar repositório no GitHub (via site ou GitHub CLI)
# 3. Conectar:
git remote add origin https://github.com/SEU_USUARIO/pibic-dash.git
git branch -M main
git push -u origin main

# 4. Ir para render.com e conectar repositório
# 5. Deploy automático!
```

---

## ⚙️ Configurações Importantes

### 1. Variáveis de Ambiente (se necessário)

No painel do Render/Railway, adicione:

```
PORT=8050
PYTHON_VERSION=3.9.18
```

### 2. Otimizar para Deploy

Antes de fazer commit, execute:

```bash
# Converter dados para Parquet
python convert_excel_to_parquet.py

# Converter imagens para WebP  
python convert_images_to_webp.py

# Testar localmente
python app.py
```

### 3. Arquivos para NÃO enviar ao Git

Adicione ao `.gitignore`:

```
*.xlsx
*.xls
*.csv
cache/
__pycache__/
*.pyc
```

**Importante:** Envie os arquivos `.parquet` em `processed/` e `.webp` em `images/webp/`!

---

## 🔒 Segurança Básica (Opcional)

Se quiser proteger o dashboard:

### Adicionar autenticação simples:

```python
# No app.py, adicione:
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == "admin" and password == "sua_senha_segura"

@app.server.before_request
@auth.login_required
def before_request():
    pass
```

E adicione ao `requirements.txt`:
```
flask-httpauth
```

---

## 📊 Comparação das Opções

| Serviço | Grátis? | Dorme? | Tempo Deploy | Dificuldade |
|---------|---------|--------|--------------|-------------|
| **Render.com** | ✅ Sim | ⚠️ Sim (15min) | 5-10min | ⭐ Fácil |
| **Railway.app** | ✅ $5/mês | ❌ Não | 3-5min | ⭐ Fácil |
| **PythonAnywhere** | ✅ Sim | ⚠️ Limitado | 10-15min | ⭐⭐ Médio |
| **Fly.io** | ✅ 3 VMs | ❌ Não | 5-8min | ⭐⭐⭐ Avançado |

**Recomendação:** Comece com **Render.com** (mais fácil) ou **Railway.app** (mais rápido).

---

## 🐛 Troubleshooting

### Problema: Dashboard não carrega

**Solução:**
- ✅ Verifique logs no painel do Render/Railway
- ✅ Teste URL diretamente no navegador
- ✅ Verifique se `requirements.txt` está completo
- ✅ Verifique se porta está configurada corretamente

### Problema: Erro 500

**Solução:**
- ✅ Verifique logs de erro
- ✅ Certifique-se que todos os arquivos estão no Git
- ✅ Verifique se dados Parquet foram enviados
- ✅ Teste localmente primeiro

### Problema: Dashboard muito lento

**Solução:**
- ✅ Use arquivos Parquet (já otimizado)
- ✅ Render "dorme" - primeira requisição demora ~30s
- ✅ Considere Railway.app (não dorme)

---

## ✅ Checklist Final

Antes de fazer deploy:

- [ ] Código testado localmente
- [ ] Dados convertidos para Parquet
- [ ] Imagens convertidas para WebP
- [ ] `.gitignore` configurado
- [ ] `requirements.txt` atualizado
- [ ] `Procfile` configurado
- [ ] Código enviado para GitHub
- [ ] Conta criada no Render/Railway
- [ ] Deploy realizado
- [ ] URL testada no navegador
- [ ] Iframe adicionado no Joomla

---

## 🎉 Pronto!

Seu dashboard está online e integrado no Joomla!

**URL do Dashboard:** `https://seu-dashboard.onrender.com`  
**Integrado em:** Sua página Joomla

Para atualizações futuras, basta fazer `git push` e o deploy será automático!

---

## 📞 Precisa de Ajuda?

1. **Logs do Deploy:** Verifique no painel do serviço
2. **Teste Local:** Sempre teste antes de fazer deploy
3. **Documentação:** Consulte docs do serviço escolhido

**Boa sorte com seu dashboard! 🚀**

