from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reunions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Parametre",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("logo", models.FileField(blank=True, null=True, upload_to="logos/", verbose_name="Logo personnalisé")),
                ("logo_actif", models.BooleanField(default=True, verbose_name="Logo actif")),
                ("nom_application", models.CharField(default="DECC/VAE", max_length=100, verbose_name="Nom de l'application")),
                ("date_modification", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Paramètre", "verbose_name_plural": "Paramètres"},
        ),
    ]
