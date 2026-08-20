# Generated manually for DocumentReunion

from django.db import migrations, models
import django.db.models.deletion
import reunions.models


class Migration(migrations.Migration):

    dependencies = [
        ("reunions", "0002_parametre"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentReunion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=200, verbose_name="Nom du document")),
                (
                    "fichier",
                    models.FileField(
                        storage=reunions.models.documents_storage,
                        upload_to=reunions.models.document_reunion_upload_to,
                        verbose_name="Fichier",
                    ),
                ),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                ("date_ajout", models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")),
                (
                    "reunion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="reunions.reunion",
                        verbose_name="Réunion",
                    ),
                ),
            ],
            options={
                "verbose_name": "Document de réunion",
                "verbose_name_plural": "Documents de réunion",
                "ordering": ["-date_ajout"],
            },
        ),
    ]
