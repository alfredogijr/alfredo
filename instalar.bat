@echo off
chcp 65001 >nul
echo.
echo ============================================
echo   Google Ads MCC - Instalacao Automatica
echo ============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Acesse python.org/downloads, baixe e instale o Python.
    echo IMPORTANTE: marque "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)
echo [OK] Python encontrado.

:: Instalar dependencias
echo.
echo Instalando dependencias...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.

:: Verificar .env
if not exist .env (
    echo.
    echo [AVISO] Arquivo .env nao encontrado.
    echo Copiando .env.example para .env...
    copy .env.example .env
    echo.
    echo IMPORTANTE: Abra o arquivo .env com o Bloco de Notas
    echo e preencha com suas credenciais antes de continuar.
    echo.
    pause
)

:: Testar conexao
echo.
echo Testando conexao com o Google Ads...
echo.
python test_connection.py

:: Configurar Claude Desktop
echo.
echo Configurando Claude Desktop...

set CONFIG_DIR=%APPDATA%\Claude
set CONFIG_FILE=%CONFIG_DIR%\claude_desktop_config.json
set PROJECT_DIR=%~dp0

if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

:: Normalizar caminho (remover barra final)
if "%PROJECT_DIR:~-1%"=="\" set PROJECT_DIR=%PROJECT_DIR:~0,-1%

:: Escapar barras para JSON
set JSON_PATH=%PROJECT_DIR:\=\\%

echo {> "%CONFIG_FILE%"
echo   "mcpServers": {>> "%CONFIG_FILE%"
echo     "google-ads-mcc": {>> "%CONFIG_FILE%"
echo       "command": "python",>> "%CONFIG_FILE%"
echo       "args": ["-m", "mcp_server.server"],>> "%CONFIG_FILE%"
echo       "cwd": "%JSON_PATH%",>> "%CONFIG_FILE%"
echo       "env": {>> "%CONFIG_FILE%"
echo         "PYTHONPATH": "%JSON_PATH%">> "%CONFIG_FILE%"
echo       }>> "%CONFIG_FILE%"
echo     }>> "%CONFIG_FILE%"
echo   }>> "%CONFIG_FILE%"
echo }>> "%CONFIG_FILE%"

echo [OK] Claude Desktop configurado em:
echo      %CONFIG_FILE%

echo.
echo ============================================
echo   PRONTO! Agora:
echo   1. Feche e reabra o Claude Desktop
echo   2. Procure o icone de martelo no chat
echo   3. Pergunte: "Liste as campanhas da conta 1154035135"
echo ============================================
echo.
pause
