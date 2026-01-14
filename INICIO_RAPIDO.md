# ⚡ Início Rápido - Dashboard Online + Joomla

## 🎯 Objetivo
Colocar seu dashboard online de graça e integrar no Joomla em **15 minutos**.

---

## 📝 Passo a Passo Simplificado

### 1. Preparar Código (2 min)

```powershell
# No PowerShell, na pasta do projeto
cd c:\pibic_dash
git init
git add .
git commit -m "Dashboard inicial"
```

### 2. Criar Conta GitHub (3 min)

- Acesse: https://github.com
- Crie conta gratuita
- Confirme email

### 3. Criar Repositório (2 min)

- GitHub → "+" → "New repository"
- Nome: `pibic-dash`
- Marque: **Public**
- Crie

### 4. Enviar Código (3 min)

```powershell
git remote add origin https://github.com/SEU_USUARIO/pibic-dash.git
git branch -M main
git push -u origin main
```

### 5. Deploy Render.com (5 min)

1. Acesse: https://render.com
2. Login com GitHub
3. "New +" → "Web Service"
4. Selecione repositório `pibic-dash`
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:server --host 0.0.0.0 --port $PORT --workers 1 --timeout 120`
   - **Plan:** Free
6. "Create Web Service"
7. Aguarde 5-10 min

### 6. Obter URL

Após deploy: `https://dashboard-ondas-calor.onrender.com`

### 7. Colocar no Joomla (2 min)

No Joomla, em um Artigo, cole:

```html
<iframe 
    src="https://SUA-URL-AQUI.onrender.com" 
    width="100%" 
    height="900px" 
    frameborder="0"
    style="border: none;">
</iframe>
```

**Substitua pela sua URL real!**

---

## ✅ Pronto!

Dashboard online e no Joomla!

---

## 📚 Documentação Completa

- **Guia Completo:** `GUIA_DEPLOY_GRATUITO.md`
- **Passo a Passo Detalhado:** `COMO_COLOCAR_ONLINE.md`
- **Integração Joomla:** `GUIA_INTEGRACAO_JOOMLA.md`

---

## ⚠️ Dica Importante

Render "dorme" após 15min. Primeira requisição demora ~30s, depois fica rápido!

Para algo que não dorme, use **Railway.app** (tem $5 grátis/mês).

---

## 🆘 Problemas?

1. Verifique logs no Render
2. Teste URL no navegador
3. Consulte `GUIA_DEPLOY_GRATUITO.md`

**Boa sorte! 🚀**

