@echo off
rem Activar el entorno virtual
call .\zoevenv\Scripts\activate.bat

rem Configurar las variables de entorno si es necesario
rem set VARIABLE_DE_ENTORNO1=valor1
rem set VARIABLE_DE_ENTORNO2=valor2

rem Ejecutar el script Python
python main.py

rem Desactivar el entorno virtual al finalizar
call .\zoevenv\\Scripts\deactivate.bat
