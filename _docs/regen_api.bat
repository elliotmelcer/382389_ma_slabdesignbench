@ECHO OFF
REM Erzeugt die API-Seiten neu (nested) und baut HTML.
REM Aus dem docs\-Ordner mit aktivierter .venv ausfuehren: regen_api.bat
sphinx-apidoc -f --separate -o api --templatedir _templates\apidoc ..\core
sphinx-apidoc -f --separate -o api --templatedir _templates\apidoc ..\slab_construction
if exist api\modules.rst del api\modules.rst
REM Create empty description files for any new packages (preserves existing ones)
python -c "import pathlib, re; [p.parent.mkdir(exist_ok=True) or p.write_text('') for f in pathlib.Path('api').glob('*.rst') for m in [re.search(r'\.\. include:: \.\./(_descriptions/[^\n]+)', f.read_text())] if m for p in [pathlib.Path(m.group(1))] if not p.exists()]"
call make.bat html
echo Fertig. Oeffne _build\html\index.html
