@echo off
echo ========================================
echo   Iniciando Dashboard no Docker
echo ========================================
echo.

REM Verifica se o Docker está rodando
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Docker nao esta rodando!
    echo Por favor, inicie o Docker Desktop e tente novamente.
    pause
    exit /b 1
)

echo [1/3] Construindo a imagem Docker...
docker-compose build
if errorlevel 1 (
    echo [ERRO] Falha ao construir a imagem!
    pause
    exit /b 1
)

echo.
echo [2/3] Iniciando o container...
docker-compose up -d
if errorlevel 1 (
    echo [ERRO] Falha ao iniciar o container!
    pause
    exit /b 1
)

echo.
echo [3/3] Verificando status...
timeout /t 3 /nobreak >nul
docker-compose ps

echo.
echo ========================================
echo   Dashboard iniciado com sucesso!
echo ========================================
echo.
echo Acesse: http://localhost:8050
echo.
echo Para ver os logs: docker-compose logs -f
echo Para parar: docker-compose down
echo.
pause

