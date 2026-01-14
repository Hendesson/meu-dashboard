# 🚀 Como Colocar Dashboard Online GRATUITAMENTE

## ⚡ Método Mais Rápido (15 minutos)

### 1️⃣ Preparar Código (2 min)

Abra o PowerShell na pasta do projeto:

```powershell
# Verificar se está na pasta certa
cd c:\pibic_dash

# Inicializar Git
git init

# Adicionar arquivos
git add .

# Fazer commit
git commit -m "Dashboard de Ondas de Calor"
```

### 2️⃣ Criar Conta no GitHub (3 min)

1. Acesse: https://github.com
2. Clique em **"Sign up"**
3. Crie sua conta (é grátis!)
4. Confirme email

### 3️⃣ Criar Repositório (2 min)

1. No GitHub, clique no **"+"** → **"New repository"**
2. Nome: `pibic-dash`
3. Marque: **Public**
4. **NÃO** marque "Add README"
5. Clique: **"Create repository"**

### 4️⃣ Enviar Código (3 min)

No PowerShell:

```powershell
# Substitua SEU_USUARIO pelo seu usuário do GitHub
git remote add origin https://github.com/SEU_USUARIO/pibic-dash.git
git branch -M main
git push -u origin main
```

**Se pedir login:** Use seu usuário e senha do GitHub

### 5️⃣ Deploy no Render.com (5 min)

1. Acesse: https://render.com
2. Clique: **"Get Started for Free"**
3. Faça login com **GitHub** (botão azul)
4. Autorize o Render acessar seus repositórios
5. Clique: **"New +"** → **"Web Service"**
6. Selecione seu repositório: `pibic-dash`
7. Configure:
   - **Name:** `dashboard-ondas-calor`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:server --host 0.0.0.0 --port $PORT --workers 1 --timeout 120`
   - **Plan:** `Free`
8. Clique: **"Create Web Service"**
9. Aguarde 5-10 minutos (primeira vez demora)

### 6️⃣ Obter URL

Após o deploy, você verá:
- ✅ **URL:** `https://dashboard-ondas-calor.onrender.com`

**Copie esta URL!**

### 7️⃣ Colocar no Joomla (2 min)

1. Acesse seu Joomla Admin
2. **Conteúdo → Artigos → Novo Artigo**
3. No editor, clique em **"Código-fonte"** ou **"HTML"**
4. Cole este código:

```html
<div style="width: 100%; margin: 20px 0;">
    <iframe 
        src="https://dashboard-ondas-calor.onrender.com" 
        width="100%" 
        height="900px" 
        frameborder="0"
        style="border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px;">
    </iframe>
</div>
```

**⚠️ IMPORTANTE:** Substitua pela sua URL real!

5. Salve e publique

---

## ✅ Pronto!

Seu dashboard está:
- ✅ Online e gratuito
- ✅ Com HTTPS automático
- ✅ Integrado no Joomla

---

## 🔄 Atualizar Dashboard

Sempre que fizer mudanças:

```powershell
git add .
git commit -m "Atualização"
git push
```

O Render atualiza automaticamente!

---

## ⚠️ Importante

**Render "dorme" após 15 minutos sem uso:**
- Primeira requisição: ~30 segundos
- Depois: rápido!

**Solução:** Use Railway.app (não dorme, mas tem limite de $5/mês grátis)

---

## 🆘 Problemas?

### Erro no Deploy
- Verifique logs no Render (aba "Logs")
- Certifique-se que `requirements.txt` está completo
- Teste localmente: `python app.py`

### Dashboard não aparece
- Teste a URL no navegador primeiro
- Aguarde alguns minutos (primeira vez)
- Verifique se iframe está correto

### Muito lento
- Primeira requisição sempre demora
- Depois fica rápido
- Considere Railway.app

---

## 📋 Checklist

- [ ] Git inicializado
- [ ] Conta GitHub criada
- [ ] Repositório criado
- [ ] Código enviado
- [ ] Conta Render criada
- [ ] Web Service criado
- [ ] Deploy concluído
- [ ] URL copiada
- [ ] Iframe no Joomla
- [ ] Testado!

**Tempo total: ~15 minutos! 🎉**

---

## 🎯 Alternativa: Railway.app (Mais Rápido)

Se quiser algo que não "dorme":

1. Acesse: https://railway.app
2. Login com GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Selecione `pibic-dash`
5. Deploy automático!

**Vantagem:** Não dorme, sempre rápido!  
**Limite:** $5 grátis/mês (suficiente para dashboard)

---

## 📞 Precisa de Ajuda?

1. **Logs:** Sempre verifique os logs no Render
2. **Teste Local:** Sempre teste antes: `python app.py`
3. **Documentação:** https://render.com/docs

**Boa sorte! 🚀**

