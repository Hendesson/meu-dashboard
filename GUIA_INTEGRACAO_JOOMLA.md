# Guia de Integração do Dashboard no Joomla

Este guia explica como integrar o dashboard Dash em uma página do Joomla.

## Opções de Integração

### Opção 1: Iframe (Recomendado - Mais Simples)

A forma mais simples é usar um iframe para embutir o dashboard.

#### Passo 1: Deploy do Dashboard

O dashboard precisa estar rodando em um servidor acessível. Opções:

**A) Servidor separado (Recomendado)**
- Deploy em servidor Python (Heroku, PythonAnywhere, AWS, etc.)
- URL: `https://seu-dashboard.com`

**B) Mesmo servidor (Subdomínio)**
- Deploy em subdomínio: `dashboard.seudominio.com`
- Configurar proxy reverso no Apache/Nginx

**C) Mesmo servidor (Porta diferente)**
- Dashboard na porta 8050
- Joomla na porta 80/443
- Configurar proxy reverso

#### Passo 2: Criar Página no Joomla

1. **Via Editor HTML:**
   - Acesse: Conteúdo → Artigos → Novo Artigo
   - No editor, clique em "Código-fonte" (HTML)
   - Cole o código abaixo:

```html
<div style="width: 100%; height: 100vh; border: none;">
    <iframe 
        src="https://seu-dashboard.com" 
        width="100%" 
        height="100vh" 
        frameborder="0"
        style="border: none; min-height: 800px;"
        allowfullscreen>
    </iframe>
</div>
```

2. **Via Módulo Custom HTML:**
   - Extensões → Módulos → Novo
   - Tipo: Custom HTML
   - Posição: onde deseja exibir
   - Cole o código HTML acima

#### Passo 3: Ajustar CSS (Opcional)

Adicione CSS customizado para melhor integração:

```css
/* No template do Joomla ou via Custom CSS */
.dashboard-container {
    width: 100%;
    height: 100vh;
    min-height: 800px;
    border: none;
    overflow: hidden;
}

.dashboard-container iframe {
    width: 100%;
    height: 100%;
    border: none;
}
```

### Opção 2: Proxy Reverso (Avançado)

Se o dashboard estiver no mesmo servidor, configure proxy reverso.

#### Apache (.htaccess ou VirtualHost)

```apache
<VirtualHost *:80>
    ServerName dashboard.seudominio.com
    
    ProxyPreserveHost On
    ProxyPass / http://localhost:8050/
    ProxyPassReverse / http://localhost:8050/
    
    # Headers necessários
    ProxyPass /_dash-layout http://localhost:8050/_dash-layout
    ProxyPass /_dash-dependencies http://localhost:8050/_dash-dependencies
    ProxyPass /_dash-update-component http://localhost:8050/_dash-update-component
    ProxyPass /_dash-component-suites http://localhost:8050/_dash-component-suites
    ProxyPass /assets http://localhost:8050/assets
</VirtualHost>
```

#### Nginx

```nginx
server {
    listen 80;
    server_name dashboard.seudominio.com;
    
    location / {
        proxy_pass http://localhost:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (se necessário)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Opção 3: Widget Customizado (PHP)

Crie um módulo PHP customizado no Joomla:

```php
<?php
// modules/mod_dashboard/mod_dashboard.php
defined('_JEXEC') or die;

$dashboard_url = $params->get('dashboard_url', 'http://localhost:8050');
$height = $params->get('height', '800px');
?>

<div class="dashboard-wrapper">
    <iframe 
        src="<?php echo htmlspecialchars($dashboard_url); ?>" 
        width="100%" 
        height="<?php echo htmlspecialchars($height); ?>"
        frameborder="0"
        style="border: none;">
    </iframe>
</div>
```

## Configurações do Dashboard para Integração

### 1. Ajustar CORS (Se necessário)

Se o dashboard estiver em domínio diferente, adicione ao `app.py`:

```python
from flask import Flask
from flask_cors import CORS

# Após criar o app
CORS(app.server, resources={r"/*": {"origins": ["https://seudominio.com"]}})
```

### 2. Remover Barra de Navegação (Opcional)

Para integração mais limpa, você pode criar uma versão "embed" do dashboard:

```python
# Adicione parâmetro de query para modo embed
@app.callback(
    Output('main-container', 'style'),
    [Input('url', 'pathname')]
)
def hide_header(pathname):
    # Verifica se está em modo embed
    if 'embed' in str(pathname) or 'embed=true' in str(pathname):
        return {'padding-top': '0px'}
    return {}
```

### 3. Configurar Tamanho Responsivo

Adicione meta tags no layout do Dash:

```python
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''
```

## Deploy do Dashboard

### Opção A: Servidor Dedicado

1. **Instale dependências:**
```bash
pip install -r requirements.txt
```

2. **Configure Gunicorn:**
```bash
gunicorn app:server --bind 0.0.0.0:8050 --workers 2 --timeout 120
```

3. **Use systemd para manter rodando:**
```ini
# /etc/systemd/system/dashboard.service
[Unit]
Description=Dashboard Dash App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/dashboard
Environment="PATH=/var/www/dashboard/venv/bin"
ExecStart=/var/www/dashboard/venv/bin/gunicorn app:server --bind 0.0.0.0:8050 --workers 2

[Install]
WantedBy=multi-user.target
```

### Opção B: Docker

Crie `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8050

CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:8050", "--workers", "2", "--timeout", "120"]
```

### Opção C: Serviços Cloud

- **Heroku:** Use o `Procfile` existente
- **PythonAnywhere:** Deploy direto
- **AWS Elastic Beanstalk:** Configure para Python
- **Google Cloud Run:** Containerize e deploy

## Segurança

### 1. Autenticação

Se necessário, adicione autenticação básica:

```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == "admin" and password == "senha_segura"

@app.server.before_request
@auth.login_required
def before_request():
    pass
```

### 2. HTTPS

Sempre use HTTPS em produção:

```python
# No app.py, force HTTPS
@app.server.before_request
def force_https():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        return redirect(request.url.replace('http://', 'https://'), 301)
```

### 3. Rate Limiting

Proteja contra abuso:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app.server,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## Troubleshooting

### Problema: Iframe não carrega

**Solução:**
- Verifique se o dashboard está acessível diretamente
- Verifique CORS se domínios diferentes
- Verifique firewall/portas

### Problema: Dashboard muito lento

**Solução:**
- Use cache (já implementado)
- Otimize dados (Parquet)
- Aumente workers do Gunicorn
- Use CDN para assets

### Problema: Estilos quebrados

**Solução:**
- Verifique se CSS está sendo carregado
- Adicione `!important` se necessário
- Verifique conflitos com tema Joomla

## Exemplo Completo: Iframe no Joomla

```html
<!-- Artigo ou Módulo Custom HTML no Joomla -->
<div class="dashboard-embed" style="position: relative; width: 100%; padding-bottom: 75%; height: 0; overflow: hidden;">
    <iframe 
        src="https://dashboard.seudominio.com" 
        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
        allowfullscreen
        loading="lazy">
        <p>Seu navegador não suporta iframes. 
        <a href="https://dashboard.seudominio.com" target="_blank">Acesse o dashboard diretamente</a>.</p>
    </iframe>
</div>
```

## Checklist de Deploy

- [ ] Dashboard rodando e acessível
- [ ] HTTPS configurado
- [ ] CORS configurado (se necessário)
- [ ] Teste iframe em página Joomla
- [ ] Teste responsividade
- [ ] Verificar performance
- [ ] Configurar backup
- [ ] Monitorar logs

## Suporte

Para problemas específicos:
1. Verifique logs do dashboard
2. Verifique logs do servidor web
3. Teste acesso direto ao dashboard
4. Verifique console do navegador (F12)

