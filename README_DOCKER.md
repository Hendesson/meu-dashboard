# Docker - Dashboard de Ondas de Calor

Este documento explica como executar o dashboard usando Docker.

## Pré-requisitos

- Docker instalado
- Docker Compose instalado (geralmente vem com o Docker Desktop)

## Como usar

### Opção 1: Usando Docker Compose (Recomendado)

1. **Construir e iniciar o container:**
```bash
docker-compose up -d
```

2. **Ver os logs:**
```bash
docker-compose logs -f
```

3. **Parar o container:**
```bash
docker-compose down
```

4. **Reconstruir após mudanças:**
```bash
docker-compose up -d --build
```

### Opção 2: Usando Docker diretamente

1. **Construir a imagem:**
```bash
docker build -t pibic-dashboard .
```

2. **Executar o container:**
```bash
docker run -d \
  --name pibic_dashboard \
  -p 8050:8050 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/processed:/app/processed \
  -v $(pwd)/cache:/app/cache \
  -v $(pwd)/assets:/app/assets \
  -v $(pwd)/images:/app/images \
  pibic-dashboard
```

3. **Ver os logs:**
```bash
docker logs -f pibic_dashboard
```

4. **Parar o container:**
```bash
docker stop pibic_dashboard
docker rm pibic_dashboard
```

## Acessar o Dashboard

Após iniciar o container, acesse:
- **URL:** http://localhost:8050

## Volumes

Os seguintes diretórios são montados como volumes para persistir dados:
- `data/` - Dados brutos
- `processed/` - Dados processados
- `cache/` - Cache da aplicação
- `assets/` - Assets estáticos
- `images/` - Imagens

## Variáveis de Ambiente

Você pode personalizar a porta alterando a variável `PORT` no `docker-compose.yml` ou passando via `-e PORT=8080` no comando `docker run`.

## Troubleshooting

### Container não inicia
```bash
docker-compose logs dashboard
```

### Reconstruir do zero
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Acessar o shell do container
```bash
docker-compose exec dashboard bash
```

