@echo off
setlocal
cd /d "%~dp0"

echo =======================================================
echo    INICIANDO CONFIGURACAO DE PERMITIR PDF (PEP)
echo =======================================================
echo.

if not exist ".env" (
    echo [AVISO] Arquivo .env nao encontrado!
    if exist ".env.example" (
        echo Criando .env a partir do .env.example...
        copy /y ".env.example" ".env" > nul
        echo Configure suas credenciais no arquivo .env antes de continuar.
        echo.
        pause
        exit /b 1
    )
)

echo [1/1] Executando script de automacao...
python main.py

if errorlevel 1 (
    echo.
    echo =======================================================
    echo [ERRO] Ocorreu uma falha durante a execucao do script!
    echo =======================================================
    echo.
    pause
    exit /b 1
)

echo.
echo =======================================================
echo    CONFIGURACAO CONCLUIDA COM SUCESSO!
echo =======================================================
echo.
pause
