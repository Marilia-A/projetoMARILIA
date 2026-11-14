@echo off
REM Gera o executavel do MARILIA para Windows (dist\MARILIA.exe).
REM Rodar dentro da pasta frontend, com o ambiente virtual ativado:
REM   pip install -r ..\requirements.txt pyinstaller
REM   gerar_executavel.bat
cd /d "%~dp0"
flet pack main.py --name MARILIA --product-name MARILIA --file-description "MARILIA - tutoria de robotica" --product-version 1.2.0 --file-version 1.2.0 -y
echo.
echo Executavel gerado em: %~dp0dist\MARILIA.exe
pause
