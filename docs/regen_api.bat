@ECHO OFF
REM Erzeugt die API-Seiten neu (nested) und baut HTML.
REM Aus dem docs\-Ordner mit aktivierter .venv ausfuehren: regen_api.bat
sphinx-apidoc -f --separate -o api --templatedir _templates\apidoc ..\core
sphinx-apidoc -f --separate -o api --templatedir _templates\apidoc ..\slab_construction
if exist api\modules.rst del api\modules.rst
call make.bat html
echo Fertig. Oeffne _build\html\index.html
