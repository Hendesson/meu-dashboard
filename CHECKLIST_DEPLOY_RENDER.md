# ✅ Checklist: Deploy no Render com Docker

Use este checklist para garantir que tudo está pronto antes do deploy.

## 📦 Antes de Fazer Deploy

### Arquivos no GitHub
- [ ] `Dockerfile` está na raiz do repositório
- [ ] `render.yaml` está na raiz (opcional, mas recomendado)
- [ ] `requirements.txt` está completo e atualizado
- [ ] `app.py` e todos os arquivos Python estão commitados
- [ ] Pasta `assets/` está no repositório
- [ ] Pasta `data/` com arquivos está no repositório
- [ ] `.dockerignore` está presente (otimiza build)

### Teste Local
- [ ] Docker está instalado e funcionando
- [ ] Teste local passou: `docker build -t test .`
- [ ] Container roda localmente: `docker run -p 8050:8050 test`
- [ ] Dashboard funciona em http://localhost:8050

### Conta Render
- [ ] Conta Render criada (https://render.com)
- [ ] Login feito com GitHub
- [ ] Repositório GitHub conectado ao Render

## 🚀 Durante o Deploy

### Configuração no Render
- [ ] Web Service criado
- [ ] Repositório correto selecionado
- [ ] Branch correta selecionada (main/master)
- [ ] Environment: **Docker** (NÃO Python buildpack)
- [ ] Build Command: **vazio** (Dockerfile faz isso)
- [ ] Start Command: **vazio** (Dockerfile define)
- [ ] Plano selecionado (Free para começar)

### Deploy
- [ ] Deploy iniciado
- [ ] Logs mostram "Building Docker image..."
- [ ] Build completou com sucesso
- [ ] Container iniciou corretamente
- [ ] URL foi gerada

## ✅ Após o Deploy

### Verificação
- [ ] Dashboard acessível na URL do Render
- [ ] Página carrega sem erros
- [ ] Gráficos e visualizações funcionam
- [ ] Dados aparecem corretamente
- [ ] Logs não mostram erros críticos

### Otimização (Opcional)
- [ ] Configurado domínio customizado (se necessário)
- [ ] Variáveis de ambiente adicionadas (se necessário)
- [ ] Monitoramento configurado

## 🔄 Atualizações Futuras

### Processo de Atualização
- [ ] Mudanças feitas no código
- [ ] Testado localmente
- [ ] Commit feito: `git commit -m "Descrição"`
- [ ] Push feito: `git push`
- [ ] Render detectou mudanças
- [ ] Novo deploy iniciado automaticamente
- [ ] Deploy completou com sucesso
- [ ] Mudanças visíveis na URL

## 🐛 Se Algo Der Errado

### Problemas Comuns
- [ ] Verificou logs no Render Dashboard
- [ ] Testou build localmente
- [ ] Verificou se Dockerfile está correto
- [ ] Verificou se todos os arquivos estão no GitHub
- [ ] Verificou se requirements.txt está completo
- [ ] Tentou rebuild manual no Render

## 📝 Comandos Úteis

```powershell
# Testar build local
docker build -t pibic-dash .

# Testar container local
docker run -p 8050:8050 pibic-dash

# Verificar arquivos no Git
git status

# Fazer commit e push
git add .
git commit -m "Mensagem"
git push
```

## 🎯 Status Final

- [ ] ✅ Deploy completo e funcionando
- [ ] ✅ URL copiada e salva
- [ ] ✅ Dashboard testado e funcionando
- [ ] ✅ Documentação lida e entendida

---

**Quando todos os itens estiverem marcados, seu deploy está completo! 🎉**

