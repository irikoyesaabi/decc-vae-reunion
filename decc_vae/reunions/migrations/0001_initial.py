# Generated manually for portable DECC/VAE
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Reunion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(verbose_name="Date")),
                ("heure_debut", models.TimeField(verbose_name="Heure de début")),
                ("heure_fin", models.TimeField(blank=True, null=True, verbose_name="Heure de fin")),
                ("lieu", models.CharField(choices=[("decc", "DECC"), ("visio", "Visioconférence"), ("autre", "Autre")], default="decc", max_length=32, verbose_name="Lieu")),
                ("lieu_precision", models.CharField(blank=True, max_length=255, verbose_name="Lieu (précision)")),
                ("type", models.CharField(choices=[("ordinaire", "Ordinaire"), ("extraordinaire", "Extraordinaire"), ("direction", "Direction / Général"), ("suivi", "Suivi"), ("preparation", "Préparation"), ("post_examens", "Post-examens"), ("autre", "Autre")], default="ordinaire", max_length=32, verbose_name="Type")),
                ("type_autre_precision", models.CharField(blank=True, max_length=255, verbose_name="Type — autre à préciser")),
                ("president", models.CharField(max_length=255, verbose_name="Président")),
                ("rapporteur", models.CharField(max_length=255, verbose_name="Rapporteur")),
                ("nombre_participants", models.PositiveIntegerField(default=0, verbose_name="Nombre de participants")),
                ("participants_presents", models.TextField(blank=True, verbose_name="Présents")),
                ("participants_excuses", models.TextField(blank=True, verbose_name="Excusés")),
                ("participants_absents", models.TextField(blank=True, verbose_name="Absents")),
                ("prochaine_reunion", models.DateField(blank=True, null=True, verbose_name="Prochaine réunion")),
                ("objet_prochaine", models.TextField(blank=True, verbose_name="Objet de la prochaine réunion")),
                ("observations", models.TextField(blank=True, verbose_name="Observations")),
                ("date_creation", models.DateTimeField(auto_now_add=True, verbose_name="Créée le")),
                ("date_modification", models.DateTimeField(auto_now=True, verbose_name="Modifiée le")),
                ("cree_par", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reunions_crees", to=settings.AUTH_USER_MODEL, verbose_name="Créée par")),
            ],
            options={"ordering": ["-date", "-heure_debut"], "verbose_name": "Réunion", "verbose_name_plural": "Réunions"},
        ),
        migrations.CreateModel(
            name="Point",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero", models.PositiveIntegerField(default=0, verbose_name="N°")),
                ("rubrique", models.CharField(choices=[("odj", "ODJ"), ("alerte", "Alerte"), ("divers", "Divers")], default="odj", max_length=16, verbose_name="Rubrique")),
                ("volet", models.CharField(choices=[("examens", "Examens"), ("concours", "Concours"), ("certifications", "Certifications"), ("vae", "VAE"), ("donnees", "Gestion des Données"), ("autre", "Autre")], max_length=32, verbose_name="Volet")),
                ("volet_autre_precision", models.CharField(blank=True, max_length=255, verbose_name="Volet — autre à préciser")),
                ("sujet", models.TextField(verbose_name="Sujet")),
                ("decision", models.TextField(blank=True, verbose_name="Décision prise")),
                ("action", models.TextField(blank=True, verbose_name="Action à mener")),
                ("responsable", models.CharField(blank=True, max_length=255, verbose_name="Responsable")),
                ("delai", models.DateField(blank=True, null=True, verbose_name="Délai")),
                ("urgence", models.PositiveSmallIntegerField(choices=[(1, "1 — Faible"), (2, "2 — Modérée"), (3, "3 — Moyenne"), (4, "4 — Urgente"), (5, "5 — Critique")], default=3, verbose_name="Niveau d'urgence")),
                ("statut", models.CharField(choices=[("a_faire", "À faire"), ("en_cours", "En cours"), ("fait", "Fait"), ("reporte", "Reporté")], default="a_faire", max_length=16, verbose_name="Statut")),
                ("date_creation", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("date_modification", models.DateTimeField(auto_now=True, verbose_name="Modifié le")),
                ("reunion", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="points", to="reunions.reunion", verbose_name="Réunion")),
            ],
            options={"ordering": ["numero"], "verbose_name": "Point", "verbose_name_plural": "Points", "unique_together": {("reunion", "numero")}},
        ),
    ]
