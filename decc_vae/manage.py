#!/usr/bin/env python
"""Point d'entrée Django — DECC/VAE."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "decc_vae.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django introuvable. Exécutez install.bat avant de lancer l'application."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
