@echo off
REM Gera o executavel do MARILIA para Windows (dist\MARILIA.exe).
REM Pode abrir com dois cliques ou rodar no terminal:
REM   PowerShell: .\gerar_executavel.bat
REM   Prompt de comando (cmd): gerar_executavel.bat
REM Se existir a pasta .venv na raiz do projeto, ela e ativada automaticamente.
cd /d "%~dp0"

if exist "..\.venv\Scripts\activate.bat" call "..\.venv\Scripts\activate.bat"

where flet >/dev/null 2>nul
if errorlevel 1 (
    echo Nao encontrei o comando flet.
    echo Crie o ambiente virtual na raiz do projeto e instale as dependencias:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt pyinstaller
    pause
    exit /b 1
)

python -c "import PyInstaller" >/dev/null 2>nul
if errorlevel 1 (
    echo Falta o PyInstaller. Com o ambiente virtual ativado, rode:
    echo   pip install pyinstaller
    pause
    exit /b 1
)

flet pack main.py --name MARILIA --product-name MARILIA --file-description "MARILIA - tutoria de robotica" --product-version 1.6.0 --file-version 1.6.0 -y
if errorlevel 1 (
    echo.
    echo Deu erro ao gerar o executavel. Veja as mensagens acima.
    pause
    exit /b 1
)

echo.
echo Executavel gerado em: %~dp0dist\MARILIA.exe
pause
