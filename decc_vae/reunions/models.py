"""Modèles Reunion et Point — DECC/VAE."""
from django.conf import settings
from django.db import models


class Reunion(models.Model):
    LIEU_DECC = "decc"
    LIEU_VISIO = "visio"
    LIEU_AUTRE = "autre"
    LIEU_CHOICES = [
        (LIEU_DECC, "DECC"),
        (LIEU_VISIO, "Visioconférence"),
        (LIEU_AUTRE, "Autre"),
    ]

    TYPE_ORDINAIRE = "ordinaire"
    TYPE_EXTRAORDINAIRE = "extraordinaire"
    TYPE_DIRECTION = "direction"
    TYPE_SUIVI = "suivi"
    TYPE_PREPARATION = "preparation"
    TYPE_POST_EXAMENS = "post_examens"
    TYPE_AUTRE = "autre"
    TYPE_CHOICES = [
        (TYPE_ORDINAIRE, "Ordinaire"),
        (TYPE_EXTRAORDINAIRE, "Extraordinaire"),
        (TYPE_DIRECTION, "Direction / Général"),
        (TYPE_SUIVI, "Suivi"),
        (TYPE_PREPARATION, "Préparation"),
        (TYPE_POST_EXAMENS, "Post-examens"),
        (TYPE_AUTRE, "Autre"),
    ]

    date = models.DateField("Date")
    heure_debut = models.TimeField("Heure de début")
    heure_fin = models.TimeField("Heure de fin", blank=True, null=True)
    lieu = models.CharField("Lieu", max_length=32, choices=LIEU_CHOICES, default=LIEU_DECC)
    lieu_precision = models.CharField("Lieu (précision)", max_length=255, blank=True)
    type = models.CharField("Type", max_length=32, choices=TYPE_CHOICES, default=TYPE_ORDINAIRE)
    type_autre_precision = models.CharField("Type — autre à préciser", max_length=255, blank=True)
    president = models.CharField("Président", max_length=255)
    rapporteur = models.CharField("Rapporteur", max_length=255)
    nombre_participants = models.PositiveIntegerField("Nombre de participants", default=0)
    participants_presents = models.TextField("Présents", blank=True)
    participants_excuses = models.TextField("Excusés", blank=True)
    participants_absents = models.TextField("Absents", blank=True)
    prochaine_reunion = models.DateField("Prochaine réunion", blank=True, null=True)
    objet_prochaine = models.TextField("Objet de la prochaine réunion", blank=True)
    observations = models.TextField("Observations", blank=True)
    date_creation = models.DateTimeField("Créée le", auto_now_add=True)
    date_modification = models.DateTimeField("Modifiée le", auto_now=True)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reunions_crees",
        verbose_name="Créée par",
    )

    class Meta:
        ordering = ["-date", "-heure_debut"]
        verbose_name = "Réunion"
        verbose_name_plural = "Réunions"

    def __str__(self):
        return f"Réunion du {self.date:%d/%m/%Y} — {self.get_type_label()}"

    def get_type_label(self):
        label = self.get_type_display()
        if self.type == self.TYPE_AUTRE and self.type_autre_precision:
            return f"{label} ({self.type_autre_precision})"
        return label

    def get_lieu_label(self):
        label = self.get_lieu_display()
        if self.lieu == self.LIEU_AUTRE and self.lieu_precision:
            return f"{label} ({self.lieu_precision})"
        return label


class Point(models.Model):
    RUBRIQUE_ODJ = "odj"
    RUBRIQUE_ALERTE = "alerte"
    RUBRIQUE_DIVERS = "divers"
    RUBRIQUE_CHOICES = [
        (RUBRIQUE_ODJ, "ODJ"),
        (RUBRIQUE_ALERTE, "Alerte"),
        (RUBRIQUE_DIVERS, "Divers"),
    ]

    VOLET_EXAMENS = "examens"
    VOLET_CONCOURS = "concours"
    VOLET_CERTIFICATIONS = "certifications"
    VOLET_VAE = "vae"
    VOLET_DONNEES = "donnees"
    VOLET_AUTRE = "autre"
    VOLET_CHOICES = [
        (VOLET_EXAMENS, "Examens"),
        (VOLET_CONCOURS, "Concours"),
        (VOLET_CERTIFICATIONS, "Certifications"),
        (VOLET_VAE, "VAE"),
        (VOLET_DONNEES, "Gestion des Données"),
        (VOLET_AUTRE, "Autre"),
    ]

    STATUT_A_FAIRE = "a_faire"
    STATUT_EN_COURS = "en_cours"
    STATUT_FAIT = "fait"
    STATUT_REPORTE = "reporte"
    STATUT_CHOICES = [
        (STATUT_A_FAIRE, "À faire"),
        (STATUT_EN_COURS, "En cours"),
        (STATUT_FAIT, "Fait"),
        (STATUT_REPORTE, "Reporté"),
    ]

    URGENCE_CHOICES = [
        (1, "1 — Faible"),
        (2, "2 — Modérée"),
        (3, "3 — Moyenne"),
        (4, "4 — Urgente"),
        (5, "5 — Critique"),
    ]

    reunion = models.ForeignKey(
        Reunion,
        on_delete=models.CASCADE,
        related_name="points",
        verbose_name="Réunion",
    )
    numero = models.PositiveIntegerField("N°", default=0)
    rubrique = models.CharField("Rubrique", max_length=16, choices=RUBRIQUE_CHOICES, default=RUBRIQUE_ODJ)
    volet = models.CharField("Volet", max_length=32, choices=VOLET_CHOICES)
    volet_autre_precision = models.CharField("Volet — autre à préciser", max_length=255, blank=True)
    sujet = models.TextField("Sujet")
    decision = models.TextField("Décision prise", blank=True)
    action = models.TextField("Action à mener", blank=True)
    responsable = models.CharField("Responsable", max_length=255, blank=True)
    delai = models.DateField("Délai", blank=True, null=True)
    urgence = models.PositiveSmallIntegerField("Niveau d'urgence", choices=URGENCE_CHOICES, default=3)
    statut = models.CharField("Statut", max_length=16, choices=STATUT_CHOICES, default=STATUT_A_FAIRE)
    date_creation = models.DateTimeField("Créé le", auto_now_add=True)
    date_modification = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        ordering = ["numero"]
        unique_together = [("reunion", "numero")]
        verbose_name = "Point"
        verbose_name_plural = "Points"

    def __str__(self):
        return f"Point {self.numero} — {self.sujet[:60]}"

    def get_volet_label(self):
        label = self.get_volet_display()
        if self.volet == self.VOLET_AUTRE and self.volet_autre_precision:
            return f"{label} ({self.volet_autre_precision})"
        return label

    def save(self, *args, **kwargs):
        if not self.numero:
            last = (
                Point.objects.filter(reunion=self.reunion)
                .exclude(pk=self.pk)
                .order_by("-numero")
                .values_list("numero", flat=True)
                .first()
            )
            self.numero = (last or 0) + 1
        super().save(*args, **kwargs)


class Parametre(models.Model):
    """Paramètres uniques de l'application (logo, nom)."""

    logo = models.FileField(
        upload_to="logos/",
        blank=True,
        null=True,
        verbose_name="Logo personnalisé",
    )
    logo_actif = models.BooleanField(default=True, verbose_name="Logo actif")
    nom_application = models.CharField(
        max_length=100,
        default="DECC/VAE",
        verbose_name="Nom de l'application",
    )
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètre"
        verbose_name_plural = "Paramètres"

    def __str__(self):
        return "Paramètres de l'application"

    @classmethod
    def get_instance(cls):
        instance, _created = cls.objects.get_or_create(pk=1)
        return instance

    @property
    def logo_url(self):
        if self.logo and self.logo_actif:
            return self.logo.url
        return None
