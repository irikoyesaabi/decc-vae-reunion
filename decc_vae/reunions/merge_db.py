"""Fusion de fichiers SQLite DECC/VAE (réattribution des ID, doublons ignorés)."""
import sqlite3
from pathlib import Path

from django.db import transaction

from .models import Point, Reunion


def _row_to_dict(cursor, row):
    cols = [c[0] for c in cursor.description]
    return dict(zip(cols, row))


def _has_column(cols, name):
    return name in cols


def merge_sqlite_file(sqlite_path):
    path = Path(sqlite_path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%reunion%'"
        )
        tables = [r[0] for r in cur.fetchall()]
        reunion_table = next((t for t in tables if t.endswith("reunion") or t == "reunions_reunion"), None)
        if not reunion_table:
            raise ValueError("Aucune table de réunions reconnue dans ce fichier.")
        point_table = reunion_table.replace("reunion", "point")
        cur.execute(f"SELECT * FROM {reunion_table}")
        reunions_src = [_row_to_dict(cur, row) for row in cur.fetchall()]
        try:
            cur.execute(f"SELECT * FROM {point_table}")
            points_src = [_row_to_dict(cur, row) for row in cur.fetchall()]
        except sqlite3.Error:
            points_src = []
    finally:
        conn.close()

    added_r = 0
    added_p = 0
    skipped = 0
    id_map = {}

    with transaction.atomic():
        for src in reunions_src:
            date = src.get("date")
            heure = src.get("heure_debut")
            typ = src.get("type") or Reunion.TYPE_ORDINAIRE
            president = src.get("president") or ""
            exists = Reunion.objects.filter(
                date=date, heure_debut=heure, type=typ, president=president
            ).first()
            if exists:
                id_map[src.get("id")] = exists.pk
                skipped += 1
                continue
            lieu = src.get("lieu") or Reunion.LIEU_DECC
            if lieu not in dict(Reunion.LIEU_CHOICES):
                lieu_prec = str(lieu)
                lieu = Reunion.LIEU_AUTRE
            else:
                lieu_prec = src.get("lieu_precision") or ""
            if typ not in dict(Reunion.TYPE_CHOICES):
                typ_prec = src.get("type_autre_precision") or str(typ)
                typ = Reunion.TYPE_AUTRE
            else:
                typ_prec = src.get("type_autre_precision") or ""
            reunion = Reunion(
                date=date,
                heure_debut=heure,
                heure_fin=src.get("heure_fin"),
                lieu=lieu,
                lieu_precision=lieu_prec,
                type=typ,
                type_autre_precision=typ_prec,
                president=president,
                rapporteur=src.get("rapporteur") or "",
                nombre_participants=src.get("nombre_participants") or 0,
                participants_presents=src.get("participants_presents") or "",
                participants_excuses=src.get("participants_excuses") or "",
                participants_absents=src.get("participants_absents") or "",
                prochaine_reunion=src.get("prochaine_reunion"),
                objet_prochaine=src.get("objet_prochaine") or "",
                observations=src.get("observations") or "",
            )
            reunion.save()
            id_map[src.get("id")] = reunion.pk
            added_r += 1

        for src in points_src:
            new_rid = id_map.get(src.get("reunion_id") or src.get("reunion"))
            if not new_rid:
                continue
            sujet = src.get("sujet") or ""
            if Point.objects.filter(reunion_id=new_rid, sujet=sujet).exists():
                skipped += 1
                continue
            volet = src.get("volet") or src.get("service") or Point.VOLET_AUTRE
            if volet in ("si", "scolarite"):
                volet = Point.VOLET_DONNEES if volet == "si" else Point.VOLET_AUTRE
            if volet not in dict(Point.VOLET_CHOICES):
                volet_prec = src.get("volet_autre_precision") or str(volet)
                volet = Point.VOLET_AUTRE
            else:
                volet_prec = src.get("volet_autre_precision") or ""
            Point.objects.create(
                reunion_id=new_rid,
                numero=0,
                rubrique=src.get("rubrique") or Point.RUBRIQUE_ODJ,
                volet=volet,
                volet_autre_precision=volet_prec,
                sujet=sujet,
                decision=src.get("decision") or "",
                action=src.get("action") or "",
                responsable=src.get("responsable") or "",
                delai=src.get("delai"),
                urgence=int(src.get("urgence") or 3),
                statut=src.get("statut") or Point.STATUT_A_FAIRE,
            )
            added_p += 1

    return {
        "reunions_ajoutees": added_r,
        "points_ajoutes": added_p,
        "doublons": skipped,
    }
