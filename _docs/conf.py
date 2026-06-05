"""Sphinx-Konfiguration für die HP-Shell Benchmarking Suite.

Diese Datei liegt in <projekt-root>/_docs/. Der Projekt-Root (mit den Paketen
'core' und 'slab_construction') ist eine Ebene darüber.

WICHTIG: Den Build aus der aktivierten .venv ausführen, in der structuralcodes,
ioh, numpy und matplotlib installiert sind. autodoc IMPORTIERT die Module — sind
die Abhängigkeiten nicht da, scheitert der Import. (Siehe autodoc_mock_imports.)
"""

import os
import sys
from datetime import datetime

# -- Pfad-Setup --------------------------------------------------------------
# conf.py liegt in _docs/, der Projekt-Root ist eine Ebene höher.
sys.path.insert(0, os.path.abspath(".."))

# -- Projektinformationen ----------------------------------------------------
project = "SlabDesignBench"
author = "Elliot Melcer"
copyright = f"{datetime.now():%Y}, Elliot Melcer"
release = "0.1"

# -- Allgemeine Konfiguration ------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",       # zieht Docstrings aus dem Code
    # "sphinx.ext.autosummary",   # generiert Übersichtstabellen
    "sphinx.ext.napoleon",      # versteht NumPy- (und Google-) Style
    "sphinx.ext.viewcode",      # Link "[source]" zum Quelltext
    "sphinx.ext.intersphinx",   # Querverweise zu Python/NumPy-Doku (braucht Internet beim Build)
    "sphinx.ext.mathjax",       # Formel-Satz in HTML
    "sphinxcontrib.bibtex",     # Quellen
]

bibtex_bibfiles = ["refs.bib"]
bibtex_default_style = "plain"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "_descriptions"]
language = "de"

# -- autodoc / autosummary ---------------------------------------------------
# autosummary_generate = True
# "signature": Type-Hints bleiben in der Funktionssignatur. Alternativen:
#   "description" -> Hints in die Parameterliste ziehen
#   "none"        -> Hints ausblenden (Typen kommen dann nur aus dem Docstring)
autodoc_typehints = "signature"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    # undoc-members bewusst AUS: nur dokumentierte Objekte erscheinen.
    # So siehst du deinen Fortschritt — was noch keinen Docstring hat, taucht nicht auf.
    "undoc-members": False,
    "show-inheritance": True,
    "private-members": True,
}
# Fallback: Wenn du NICHT aus der .venv baust, kannst du schwere Drittpakete mocken.
# ACHTUNG: Klassen, die von structuralcodes erben (z.B. UserDefined, Material),
# vertragen sich schlecht mit Mocks — dann lieber aus der .venv bauen und Liste leer lassen.
autodoc_mock_imports = []

# -- napoleon (NumPy-Style) --------------------------------------------------
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_attr_annotations = True

# -- intersphinx -------------------------------------------------------------
# Verlinkt Typen wie 'float' oder 'numpy.ndarray' auf die offizielle Doku.
# Benötigt Internet beim Build; sonst gibt es nur eine Warnung (unkritisch).
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

# -- HTML-Ausgabe ------------------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
html_title = "SlabDesignBench"

# Verhindert, dass Funktionen und Klassen in der Seitenleisten-Navigation erscheinen.
# Ohne diese Option zieht furo jeden automodule-Member (Funktionen, Klassen) in den Baum.
toc_object_entries_show_parents = "hide"
toc_object_entries = False

# Modulprefix weglassen
add_module_names = False

# -- LaTeX / PDF-Ausgabe -----------------------------------------------------
# Deine Docstrings enthalten Unicode (ε, κ, χ, ², ³, ‰, →, …). Das Standard-
# 'pdflatex' scheitert daran. 'xelatex' verarbeitet Unicode nativ.
# Voraussetzung: eine TeX-Distribution (TeX Live / MiKTeX) ist installiert.
latex_engine = "xelatex"
latex_elements = {
    "papersize": "a4paper",
    "pointsize": "11pt",
    # Fallback-Zuordnungen für Sonderzeichen, falls die Standardschrift sie nicht hat.
    # Bei Bedarf weitere Zeichen ergänzen.
    "preamble": r"""
\usepackage{newunicodechar}
\newunicodechar{‰}{\textperthousand}
\newunicodechar{→}{$\rightarrow$}
""",
}
latex_documents = [
    (
        "index",                        # Startdokument
        "slabdesignbench.tex",          # Ausgabedateiname
        "SlabDesignBench",              # Titel
        "Elliot Melcer",                # Autor
        "manual",                       # Dokumentklasse (manual = report)
    ),
]