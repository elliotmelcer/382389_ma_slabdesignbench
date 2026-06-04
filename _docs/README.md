# Sphinx-Doku — Einrichtung & Build

Diese `docs/`-Struktur gehört in den **Projekt-Root**, also neben die Pakete
`core/` und `slab_construction/`:

```
382389_ma_benchmarking_suite_hp_shell/
├── core/
├── slab_construction/
└── docs/            <- dieser Ordner
    ├── conf.py
    ├── index.rst
    ├── api/
    ├── Makefile
    └── make.bat
```

## Einmalig: Abhängigkeiten installieren

Bei **aktivierter** Projekt-`.venv` (wichtig — siehe unten):

```bash
pip install -r docs/requirements-docs.txt
```

## HTML bauen (für die Schnellkontrolle)

```bash
# Linux / macOS
cd docs
make html

# Windows
cd docs
make.bat html
```

Ergebnis: `docs/_build/html/index.html` im Browser öffnen.

## PDF bauen

Voraussetzung: eine TeX-Distribution ist installiert (TeX Live unter Linux/macOS,
MiKTeX unter Windows). Die `conf.py` nutzt **xelatex**, weil deine Docstrings
Unicode-Zeichen (ε, κ, χ, ², ‰, →) enthalten, an denen das übliche pdflatex
scheitern würde.

```bash
cd docs
make latexpdf      # bzw. make.bat latexpdf unter Windows
```

Ergebnis: `docs/_build/latex/hp_shell_suite.pdf`.

## Wichtig: aus der `.venv` bauen

`autodoc` **importiert** deine Module, um die Docstrings zu lesen. Daher müssen
`structuralcodes`, `ioh`, `numpy` und `matplotlib` im aktiven Interpreter verfügbar
sein. Am einfachsten: `.venv` aktivieren und von dort bauen. Sonst schlägt der
Import fehl (besonders bei Klassen, die von `structuralcodes` erben).

## So testest du deine erste umgestellte Datei

In der `conf.py` ist `undoc-members = False` gesetzt: Es erscheinen **nur**
Objekte mit Docstring. Das heißt, dein Fortschritt ist direkt sichtbar — nach dem
Umstellen einer Datei einfach neu bauen, und die fertig dokumentierten Funktionen
tauchen auf.

Die Module sind bereits in `api/analysis_core.rst`, `api/slab_construction.rst`
und `api/ioh_core.rst` eingetragen. Stellst du z.B. zuerst `section_methods.py` um,
ist es über `api/analysis_core.rst` schon verdrahtet — `make html`, fertig.

## Später: API-Seiten automatisch erzeugen

Wenn alle Dateien umgestellt sind, kannst du die `api/*.rst` auch automatisch
generieren lassen statt sie zu pflegen:

```bash
cd docs
sphinx-apidoc -o api ../core
sphinx-apidoc -o api ../slab_construction
```

(Die Verifikations-/Testskripte unter `_mains/` bewusst nicht einbinden — die
führen teils Code beim Import aus.)
