#!/usr/bin/env bash
# Erzeugt die API-Seiten neu (nested) und baut HTML.
# Aus dem docs/-Ordner mit aktivierter .venv ausführen: bash regen_api.sh
set -e
sphinx-apidoc -f --separate -o api --templatedir _templates/apidoc ../core
sphinx-apidoc -f --separate -o api --templatedir _templates/apidoc ../slab_construction
rm -f api/modules.rst   # nicht benoetigt; index.rst verweist direkt auf api/core und api/slab_construction
make html
echo "Fertig. Oeffne _build/html/index.html"
