# 🚀 Deploy Rápido e Gratuito - Passo a Passo Simplificado

## Método Mais Rápido: Render.com (15 minutos)

### Passo 1: Preparar Código (5 min)

```bash
# 1. Certifique-se que está na pasta do projeto
cd c:\pibic_dash

# 2. Inicialize Git (se ainda não fez)
git init

# 3. Adicione todos os arquivos
git add .

# 4. Faça commit
git commit -m "Dashboard de Ondas de Calor - Versão inicial"
```

### Passo 2: Criar Repositório no GitHub (3 min)

1. Acesse: https://github.com/new
2. Nome: `pibic-dash` (ou outro nome)
3. Marque: **Public** (gratuito)
4. Clique: **Create repository**
5. **NÃO** marque "Initialize with README"

### Passo 3: Enviar Código para GitHub (2 min)

```bash
# Substitua SEU_USUARIO pelo seu usuário do GitHub
git remote add origin https://github.com/SEU_USUARIO/pibic-dash.git
git branch -M main
git push -u origin main
```

**Se pedir login:** Use seu usuário e senha do GitHub (ou token)

### Passo 4: Deploy no Render.com (5 min)

1. Acesse: https://render.com
2. Clique: **"Get Started for Free"**
3. Faça login com **GitHub**
4. Clique: **"New +"** → **"Web Service"**
5. Conecte seu repositório: `pibic-dash`
6. Configure:
   - **Name:** `dashboard-ondas-calor`
   - **Region:** `Oregon (US West)` ou mais próximo
   - **Branch:** `main`
   - **Root Directory:** (deixe vazio)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:server --host 0.0.0.0 --port $PORT`
   - **Plan:** `Free`
7. Clique: **"Create Web Service"**
8. Aguarde 5-10 minutos

### Passo 5: Obter URL (1 min)

Após deploy, você verá:
- **URL:** `https://dashboard-ondas-calor.onrender.com`

**Copie esta URL!**

### Passo 6: Integrar no Joomla (2 min)

1. Acesse seu Joomla Admin
2. **Conteúdo → Artigos → Novo Artigo**
3. No editor, clique em **"Código-fonte"** ou **"HTML"**
4. Cole este código:

```html
<iframe 
    src="https://dashboard-ondas-calor.onrender.com" 
    width="100%" 
    height="900px" 
    frameborder="0"
    style="border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
</iframe>
```

**Substitua pela sua URL real!**

5. Salve e publique

### ✅ Pronto!

Seu dashboard está online e no Joomla!

---

## ⚠️ Importante: Primeira Requisição

Render.com "dorme" após 15 minutos sem uso. A primeira requisição pode demorar ~30 segundos. Depois fica rápido!

---

## 🔄 Atualizar Dashboard

Sempre que fizer mudanças:

```bash
git add .
git commit -m "Atualização do dashboard"
git push
```

O Render atualiza automaticamente em 2-3 minutos!

---

## 🆘 Problemas?

### Erro no Deploy
- Verifique logs no Render
- Certifique-se que `requirements.txt` está completo
- Teste localmente primeiro: `python app.py`

### Dashboard não aparece no Joomla
- Teste a URL diretamente no navegador
- Verifique se o iframe está correto
- Aguarde alguns minutos (primeira vez demora)

### Muito lento
- Primeira requisição sempre demora (~30s)
- Depois fica rápido
- Considere Railway.app (não dorme)

---

## 📝 Checklist Rápido

- [ ] Git inicializado
- [ ] Código no GitHub
- [ ] Conta Render criada
- [ ] Web Service criado
- [ ] Deploy concluído
- [ ] URL copiada
- [ ] Iframe no Joomla
- [ ] Testado no navegador

**Tempo total: ~15 minutos! 🎉**

