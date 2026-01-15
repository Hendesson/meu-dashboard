# ⚡ Deploy Rápido no Render com Docker - 5 Minutos

Guia super rápido para fazer deploy no Render usando Docker.

## 🚀 Passos Rápidos

### 1. Código no GitHub (2 min)

```powershell
cd C:\pibic_dash
git add .
git commit -m "Configuração Docker para Render"
git push
```

### 2. Criar Web Service no Render (2 min)

1. Acesse: https://render.com
2. **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Configure:
   - **Name:** `dashboard-ondas-calor`
   - **Environment:** **Deixe vazio** ou selecione **"Docker"**
   - **Build Command:** (deixe vazio)
   - **Start Command:** (deixe vazio)
   - **Plan:** `Free`
5. Clique **"Create Web Service"**

### 3. Aguardar Deploy (1 min)

- Render constrói a imagem Docker automaticamente
- Aguarde ~5-10 minutos na primeira vez
- Você verá a URL: `https://dashboard-ondas-calor.onrender.com`

## ✅ Pronto!

Seu dashboard está online! 🎉

## 📝 Arquivos Importantes

Certifique-se de que estão no GitHub:
- ✅ `Dockerfile`
- ✅ `render.yaml` (opcional, mas ajuda)
- ✅ `requirements.txt`
- ✅ Todos os arquivos Python
- ✅ Pasta `data/` com arquivos
- ✅ Pasta `assets/`

## 🔄 Atualizar

Sempre que fizer mudanças:

```powershell
git add .
git commit -m "Atualização"
git push
```

Render atualiza automaticamente em 2-3 minutos!

## 🆘 Problema?

- Veja os logs no Render Dashboard
- Certifique-se que `Dockerfile` está na raiz
- Teste localmente: `docker build -t test .`

---

**Mais detalhes? Veja `GUIA_DEPLOY_RENDER_DOCKER.md`**

