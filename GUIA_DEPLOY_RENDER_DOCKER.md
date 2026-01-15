# 🚀 Guia Completo: Deploy no Render com Docker

Este guia vai te ensinar passo a passo como fazer deploy do dashboard no Render usando Docker.

## 📋 Pré-requisitos

1. **Conta no GitHub** (gratuita)
2. **Conta no Render** (gratuita) - https://render.com
3. **Git instalado** no seu computador
4. **Código no GitHub** (repositório público ou privado)

## 🎯 Por Que Usar Docker no Render?

✅ **Ambiente Consistente** - Funciona igual no seu computador e no Render  
✅ **Controle Total** - Você define exatamente o que precisa  
✅ **Mais Rápido** - Build otimizado  
✅ **Fácil Debug** - Testa localmente antes de fazer deploy  

## 📝 Passo a Passo

### **Passo 1: Preparar o Código no GitHub**

Se você ainda não tem o código no GitHub:

```powershell
# 1. Ir para a pasta do projeto
cd C:\pibic_dash

# 2. Inicializar Git (se ainda não fez)
git init

# 3. Adicionar todos os arquivos
git add .

# 4. Fazer commit
git commit -m "Adicionar configuração Docker para Render"

# 5. Criar repositório no GitHub (via site) e depois:
git remote add origin https://github.com/SEU_USUARIO/pibic-dash.git
git branch -M main
git push -u origin main
```

**Importante:** Certifique-se de que estes arquivos estão no repositório:
- ✅ `Dockerfile`
- ✅ `requirements.txt`
- ✅ `app.py`
- ✅ Todos os arquivos Python necessários
- ✅ Pasta `assets/`
- ✅ Pasta `data/` (com os arquivos de dados)

### **Passo 2: Criar Conta no Render**

1. Acesse: https://render.com
2. Clique em **"Get Started for Free"**
3. Faça login com sua conta **GitHub**
4. Autorize o Render a acessar seus repositórios

### **Passo 3: Criar Web Service no Render**

1. No Dashboard do Render, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte seu repositório GitHub:
   - Se não aparecer, clique em **"Configure account"** e autorize
   - Selecione o repositório `pibic-dash` (ou o nome do seu)

### **Passo 4: Configurar o Deploy com Docker**

Configure assim:

#### **Configurações Básicas:**
- **Name:** `dashboard-ondas-calor` (ou outro nome)
- **Region:** Escolha a região mais próxima (ex: `Oregon (US West)`)
- **Branch:** `main` (ou `master`)
- **Root Directory:** (deixe vazio)

#### **Configurações Importantes - Docker:**
- **Environment:** **NÃO selecione Python!** Deixe vazio ou selecione **"Docker"**
- **Build Command:** (deixe vazio - o Dockerfile faz isso)
- **Start Command:** (deixe vazio - o Dockerfile define o CMD)

**⚠️ IMPORTANTE:** Se Render detectar automaticamente Python, você precisa mudar para Docker:
- Vá em **"Advanced"** → **"Docker"**
- Ou delete o serviço e crie novamente selecionando Docker

#### **Plano:**
- **Plan:** `Free` (para começar)

### **Passo 5: Variáveis de Ambiente (Opcional)**

O Render define automaticamente a variável `PORT`. Se precisar de outras:

1. Vá em **"Environment"**
2. Adicione variáveis se necessário:
   - `PYTHONUNBUFFERED=1` (já está no Dockerfile, mas pode adicionar aqui também)

### **Passo 6: Fazer Deploy**

1. Clique em **"Create Web Service"**
2. O Render vai:
   - Clonar seu repositório
   - Construir a imagem Docker (pode demorar 5-10 minutos na primeira vez)
   - Iniciar o container
   - Atribuir uma URL

### **Passo 7: Aguardar o Deploy**

Você verá os logs em tempo real:
- ✅ "Building Docker image..."
- ✅ "Installing dependencies..."
- ✅ "Starting container..."
- ✅ "Your service is live at https://..."

**Tempo estimado:** 5-10 minutos na primeira vez

### **Passo 8: Acessar o Dashboard**

Após o deploy, você terá uma URL como:
```
https://dashboard-ondas-calor.onrender.com
```

**Copie esta URL!** Ela é permanente.

## 🔧 Configuração Avançada: render.yaml (Opcional)

Se quiser usar o arquivo `render.yaml` para automatizar, atualize-o assim:

```yaml
services:
  - type: web
    name: dashboard-ondas-calor
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: PORT
        value: 8050
      - key: PYTHONUNBUFFERED
        value: 1
```

## 📦 Estrutura de Arquivos Necessários

Certifique-se de que estes arquivos estão no GitHub:

```
pibic_dash/
├── Dockerfile              ✅ OBRIGATÓRIO
├── requirements.txt        ✅ OBRIGATÓRIO
├── app.py                  ✅ OBRIGATÓRIO
├── data_processing.py      ✅ OBRIGATÓRIO
├── visualization.py        ✅ OBRIGATÓRIO
├── cache_manager.py        ✅ OBRIGATÓRIO
├── config_paths.py         ✅ OBRIGATÓRIO
├── assets/                 ✅ OBRIGATÓRIO
│   ├── *.png
│   └── custom.css
├── data/                   ✅ OBRIGATÓRIO (com arquivos)
│   ├── *.csv
│   ├── *.xlsx
│   └── mapa_interativo.html
└── .dockerignore           ✅ RECOMENDADO
```

## 🐛 Solução de Problemas

### **Problema: Render não detecta Docker**

**Solução:**
1. Certifique-se de que `Dockerfile` está na raiz do repositório
2. No Render, vá em **"Settings"** → **"Build & Deploy"**
3. Em **"Dockerfile Path"**, deixe vazio ou coloque `./Dockerfile`
4. Salve e faça **"Manual Deploy"**

### **Problema: Build falha**

**Solução:**
1. Veja os logs completos no Render
2. Verifique se `requirements.txt` está correto
3. Teste localmente: `docker build -t test .`
4. Verifique se todos os arquivos estão no GitHub

### **Problema: App não inicia**

**Solução:**
1. Verifique os logs: **"Logs"** no Render Dashboard
2. Certifique-se de que `app:server` está correto no Dockerfile
3. Verifique se a porta está configurada corretamente

### **Problema: Arquivos de dados não encontrados**

**Solução:**
1. Certifique-se de que a pasta `data/` está no GitHub
2. Verifique se os arquivos não estão no `.gitignore`
3. Se arquivos são muito grandes, considere usar volumes ou S3

### **Problema: Deploy muito lento**

**Solução:**
1. Primeira vez sempre demora (5-10 min)
2. Próximos deploys são mais rápidos (cache)
3. Considere usar `.dockerignore` para reduzir tamanho

## ⚡ Dicas de Otimização

### **1. Usar .dockerignore**

Já criamos o `.dockerignore` para você! Ele reduz o tamanho da imagem.

### **2. Cache de Dependências**

O Dockerfile já está otimizado para usar cache do pip.

### **3. Multi-stage Build (Avançado)**

Para imagens menores, você pode usar multi-stage build (não necessário agora).

## 🔄 Atualizar o Deploy

Sempre que fizer mudanças:

```powershell
# 1. Fazer commit
git add .
git commit -m "Descrição das mudanças"

# 2. Enviar para GitHub
git push

# 3. Render faz deploy automático em 2-3 minutos!
```

Ou faça deploy manual no Render Dashboard:
- **"Manual Deploy"** → **"Deploy latest commit"**

## 📊 Monitoramento

No Render Dashboard você pode:
- ✅ Ver logs em tempo real
- ✅ Ver uso de recursos (CPU, RAM)
- ✅ Ver histórico de deploys
- ✅ Configurar alertas

## 💰 Planos do Render

- **Free:** 
  - ✅ Gratuito
  - ⚠️ "Dorme" após 15 min sem uso
  - ⚠️ Primeira requisição pode demorar ~30s
  - ✅ 750 horas/mês grátis

- **Starter ($7/mês):**
  - ✅ Não dorme
  - ✅ Mais rápido
  - ✅ Melhor para produção

## ✅ Checklist Final

Antes de fazer deploy, verifique:

- [ ] `Dockerfile` está na raiz do repositório
- [ ] `requirements.txt` está completo e atualizado
- [ ] Todos os arquivos Python estão no GitHub
- [ ] Pasta `data/` com arquivos está no GitHub
- [ ] Pasta `assets/` está no GitHub
- [ ] Código testado localmente com Docker
- [ ] Conta Render criada e conectada ao GitHub
- [ ] Web Service criado com Docker (não Python buildpack)

## 🎓 Comandos Úteis

### **Testar Localmente Antes do Deploy**

```powershell
# Construir imagem
docker build -t pibic-dash .

# Rodar localmente
docker run -p 8050:8050 pibic-dash

# Testar se funciona
# Acesse: http://localhost:8050
```

### **Ver Logs no Render**

No Dashboard do Render:
- Vá em **"Logs"** para ver logs em tempo real
- Use **"Download Logs"** para salvar

## 🆘 Precisa de Ajuda?

1. **Logs do Render:** Sempre comece pelos logs
2. **Teste Local:** Teste com Docker localmente primeiro
3. **Documentação Render:** https://render.com/docs/docker
4. **Comunidade:** Render tem suporte via email

---

**Pronto! Seu dashboard estará online em poucos minutos! 🎉**

