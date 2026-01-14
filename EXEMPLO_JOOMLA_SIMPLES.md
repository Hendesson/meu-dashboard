# Integração Rápida no Joomla - Passo a Passo

## Método Mais Simples (5 minutos)

### Passo 1: Iniciar o Dashboard

No servidor onde está o dashboard:

```bash
# Opção A: Modo normal
python app.py

# Opção B: Modo embed (recomendado para iframe)
python app_embed.py

# Opção C: Com Gunicorn (produção)
gunicorn app:server --bind 0.0.0.0:8050 --workers 2 --timeout 120
```

O dashboard estará disponível em: `http://seu-servidor:8050`

### Passo 2: Inserir no Joomla

1. **Acesse o Joomla:**
   - Conteúdo → Artigos → Novo Artigo (ou edite um existente)

2. **No editor:**
   - Clique no botão "Código-fonte" ou "HTML" (depende do editor)
   - Cole este código:

```html
<iframe 
    src="http://seu-servidor:8050" 
    width="100%" 
    height="900px" 
    frameborder="0"
    style="border: none; min-height: 900px;">
</iframe>
```

**Substitua `seu-servidor:8050` pela URL real do seu dashboard!**

3. **Salve e publique o artigo**

### Passo 3: Testar

- Acesse a página no Joomla
- O dashboard deve aparecer dentro da página

## Versão Responsiva (Recomendada)

Para melhor visualização em mobile, use este código:

```html
<div style="position: relative; width: 100%; padding-bottom: 75%; height: 0; overflow: hidden;">
    <iframe 
        src="http://seu-servidor:8050" 
        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
        allowfullscreen>
    </iframe>
</div>
```

## Se o Dashboard Estiver em Outro Servidor

Se o dashboard estiver em um servidor diferente (ex: `https://dashboard.exemplo.com`):

```html
<iframe 
    src="https://dashboard.exemplo.com" 
    width="100%" 
    height="900px" 
    frameborder="0"
    style="border: none;">
</iframe>
```

## Problemas Comuns

### Iframe não aparece
- ✅ Verifique se o dashboard está rodando
- ✅ Teste acessar a URL diretamente no navegador
- ✅ Verifique firewall/portas

### Dashboard muito lento
- ✅ Use os arquivos Parquet (já otimizado)
- ✅ Verifique conexão de rede
- ✅ Aumente workers do Gunicorn

### Erro de CORS
Se o dashboard estiver em domínio diferente, adicione ao `app.py`:

```python
from flask_cors import CORS
CORS(app.server)
```

## Exemplo Completo com Estilos

```html
<div class="dashboard-wrapper" style="width: 100%; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
    <iframe 
        src="http://seu-servidor:8050" 
        width="100%" 
        height="900px" 
        frameborder="0"
        style="border: none; display: block;"
        allowfullscreen
        title="Dashboard de Ondas de Calor">
    </iframe>
</div>
```

## Pronto! 🎉

Seu dashboard está integrado no Joomla!

Para mais opções avançadas, consulte `GUIA_INTEGRACAO_JOOMLA.md`

