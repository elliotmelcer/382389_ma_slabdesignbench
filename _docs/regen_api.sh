#!/usr/bin/env bash
# Erzeugt die API-Seiten neu (nested) und baut HTML.
# Aus dem docs/-Ordner mit aktivierter .venv ausführen: bash regen_api.sh
set -e
sphinx-apidoc -f --separate -o api --templatedir _templates/apidoc ../core
sphinx-apidoc -f --separate -o api --templatedir _templates/apidoc ../slab_construction
rm -f api/modules.rst
# Create empty description files for any new packages (preserves existing ones)
python -c "
import pathlib, re
for f in pathlib.Path('api').glob('*.rst'):
    m = re.search(r'\.\. include:: \.\./(_descriptions/[^\n]+)', f.read_text())
    if m:
        p = pathlib.Path(m.group(1))
        p.parent.mkdir(exist_ok=True)
        if not p.exists(): p.write_text('')
"   # nicht benoetigt; index.rst verweist direkt auf api/core und api/slab_construction
make html
echo "Fertig. Oeffne _build/html/index.html"
