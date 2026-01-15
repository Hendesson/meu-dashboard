# 🐳 Guia Completo: Como Colocar o Dashboard no Docker

Este guia vai te ensinar passo a passo como colocar seu dashboard no Docker.

## 📋 Pré-requisitos

Antes de começar, você precisa ter instalado:

1. **Docker Desktop** (Windows/Mac) ou **Docker Engine** (Linux)
   - Download: https://www.docker.com/products/docker-desktop
   - Verificar instalação: `docker --version`

2. **Docker Compose** (geralmente vem com Docker Desktop)
   - Verificar instalação: `docker-compose --version`

## 🚀 Passo a Passo

### **Passo 1: Verificar os Arquivos**

Certifique-se de que você tem estes arquivos na pasta do projeto:
- ✅ `Dockerfile` - Define como construir a imagem
- ✅ `docker-compose.yml` - Facilita o gerenciamento
- ✅ `requirements.txt` - Dependências Python
- ✅ `app.py` - Aplicação principal

### **Passo 2: Abrir o Terminal**

Abra o PowerShell ou Prompt de Comando no Windows e navegue até a pasta do projeto:

```powershell
cd C:\pibic_dash
```

### **Passo 3: Construir a Imagem Docker**

Primeiro, vamos construir a imagem Docker. Isso vai:
- Baixar a imagem Python
- Instalar todas as dependências
- Preparar o ambiente

**Comando:**
```powershell
docker-compose build
```

**O que acontece:**
- Pode demorar alguns minutos na primeira vez
- Você verá várias mensagens de instalação
- No final, verá "Successfully built"

**💡 Dica:** Se der erro, verifique se o Docker está rodando (ícone do Docker na bandeja do sistema).

### **Passo 4: Iniciar o Container**

Agora vamos iniciar o dashboard:

**Comando:**
```powershell
docker-compose up -d
```

**O que significa:**
- `up` - Inicia os containers
- `-d` - Roda em background (detached mode)

**O que acontece:**
- O container será criado e iniciado
- O dashboard começará a rodar
- Você verá mensagens de inicialização

### **Passo 5: Verificar se Está Funcionando**

**Ver os logs:**
```powershell
docker-compose logs -f
```

Isso mostra os logs em tempo real. Para sair, pressione `Ctrl+C`.

**Verificar status:**
```powershell
docker-compose ps
```

Deve mostrar o container como "Up" (rodando).

### **Passo 6: Acessar o Dashboard**

Abra seu navegador e acesse:

**URL:** http://localhost:8050

Você deve ver o dashboard funcionando! 🎉

## 📝 Comandos Úteis

### **Ver os Logs**
```powershell
docker-compose logs -f dashboard
```

### **Parar o Dashboard**
```powershell
docker-compose stop
```

### **Iniciar Novamente**
```powershell
docker-compose start
```

### **Parar e Remover o Container**
```powershell
docker-compose down
```

### **Reconstruir Após Mudanças no Código**
```powershell
docker-compose up -d --build
```

### **Ver o Que Está Rodando**
```powershell
docker ps
```

### **Acessar o Shell do Container**
```powershell
docker-compose exec dashboard bash
```

## 🔧 Solução de Problemas

### **Problema: "docker-compose: command not found"**

**Solução:** Use `docker compose` (sem hífen) em versões mais novas:
```powershell
docker compose up -d
```

### **Problema: Porta 8050 já está em uso**

**Solução 1:** Pare o processo que está usando a porta
```powershell
# No Windows, encontre o processo
netstat -ano | findstr :8050
# Depois mate o processo (substitua PID pelo número)
taskkill /PID <PID> /F
```

**Solução 2:** Mude a porta no `docker-compose.yml`:
```yaml
ports:
  - "8051:8050"  # Mude 8051 para outra porta livre
```

### **Problema: Container não inicia**

**Solução:** Veja os logs para identificar o erro:
```powershell
docker-compose logs dashboard
```

### **Problema: Erro ao construir a imagem**

**Solução:** Limpe e reconstrua:
```powershell
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

### **Problema: Mudanças no código não aparecem**

**Solução:** Reconstrua a imagem:
```powershell
docker-compose up -d --build
```

## 🎯 Fluxo Completo (Resumo)

```powershell
# 1. Ir para a pasta do projeto
cd C:\pibic_dash

# 2. Construir a imagem (primeira vez)
docker-compose build

# 3. Iniciar o dashboard
docker-compose up -d

# 4. Ver os logs
docker-compose logs -f

# 5. Acessar no navegador
# http://localhost:8050

# 6. Quando terminar, parar
docker-compose down
```

## 📦 O Que São Volumes?

Os volumes no `docker-compose.yml` fazem com que os dados sejam salvos mesmo quando você para o container:

- `./data:/app/data` - Dados brutos
- `./cache:/app/cache` - Cache da aplicação
- `./processed:/app/processed` - Dados processados
- `./assets:/app/assets` - Imagens e arquivos estáticos

Isso significa que seus dados **não serão perdidos** ao reiniciar o container!

## 🎓 Entendendo os Arquivos

### **Dockerfile**
- Define como construir a imagem
- Instala Python e dependências
- Configura o ambiente

### **docker-compose.yml**
- Facilita o gerenciamento
- Define portas, volumes e variáveis
- Permite iniciar com um comando simples

### **.dockerignore**
- Lista arquivos que NÃO vão para a imagem
- Reduz o tamanho da imagem
- Acelera o build

## ✅ Checklist Final

- [ ] Docker instalado e rodando
- [ ] Arquivos Dockerfile e docker-compose.yml criados
- [ ] Comando `docker-compose build` executado com sucesso
- [ ] Comando `docker-compose up -d` executado
- [ ] Dashboard acessível em http://localhost:8050
- [ ] Logs mostram que está funcionando

## 🆘 Precisa de Ajuda?

Se algo não funcionar:
1. Verifique os logs: `docker-compose logs -f`
2. Verifique se o Docker está rodando
3. Tente reconstruir: `docker-compose up -d --build`
4. Verifique se a porta 8050 está livre

---

**Pronto! Agora você sabe como colocar seu dashboard no Docker! 🎉**

