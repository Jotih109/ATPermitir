@echo off
chcp 65001 > nul
title Permitir PDF - PEP Medicina Direta

cd /d "%~dp0"

echo =======================================================
echo    INICIANDO CONFIGURAÇÃO DE PERMITIR PDF (PEP)
echo =======================================================
echo.

if not exist ".env" (
    echo [AVISO] Arquivo .env não encontrado!
    if exist ".env.example" (
        echo Copiando .env.example para .env...
        copy .env.example .env
        echo Por favor, configure suas credenciais no arquivo .env antes de continuar.
        echo.
        pause
        exit /b 1
    )
)

echo [1/1] Executando script de automação...
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo =======================================================
    echo [ERRO] Ocorreu uma falha durante a execução do script!
    echo =======================================================
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo =======================================================
echo    CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!
echo =======================================================
echo.
pause
