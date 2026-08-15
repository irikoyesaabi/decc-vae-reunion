"""Modèles Reunion et Point — DECC/VAE."""
from django.conf import settings
from django.db import models


class Reunion(models.Model):
    TYPE_HEBDOMADAIRE = "hebdomadaire"
    TYPE_MENSUELLE = "mensuelle"
    TYPE_EXTRAORDINAIRE = "extraordinaire"
    TYPE_TECHNIQUE = "technique"
    TYPE_COORDINATION = "coordination"
    TYPE_CHOICES = [
        (TYPE_HEBDOMADAIRE, "Hebdomadaire"),
        (TYPE_MENSUELLE, "Mensuelle"),
        (TYPE_EXTRAORDINAIRE, "Extraordinaire"),
        (TYPE_TECHNIQUE, "Technique"),
        (TYPE_COORDINATION, "Coordination"),
    ]

    date = models.DateField("Date")
    heure_debut = models.TimeField("Heure de début")
    heure_fin = models.TimeField("Heure de fin", blank=True, null=True)
    lieu = models.CharField("Lieu", max_length=255, default="DECC/VAE — Niamey")
    type = models.CharField("Type", max_length=32, choices=TYPE_CHOICES, default=TYPE_HEBDOMADAIRE)
    president = models.CharField("Président", max_length=255)
    rapporteur = models.CharField("Rapporteur", max_length=255)
    nombre_participants = models.PositiveIntegerField("Nombre de participants", default=0)
    participants_presents = models.TextField("Présents", blank=True)
    participants_excuses = models.TextField("Excusés", blank=True)
    participants_absents = models.TextField("Absents", blank=True)
    prochaine_reunion = models.DateField("Prochaine réunion", blank=True, null=True)
    objet_prochaine = models.CharField("Objet de la prochaine réunion", max_length=255, blank=True)
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
        return f"Réunion du {self.date:%d/%m/%Y} — {self.get_type_display()}"

    def points_par_statut(self, statut):
        return self.points.filter(statut=statut).count()


class Point(models.Model):
    RUBRIQUE_ODJ = "odj"
    RUBRIQUE_ALERTE = "alerte"
    RUBRIQUE_DIVERS = "divers"
    RUBRIQUE_CHOICES = [
        (RUBRIQUE_ODJ, "ODJ"),
        (RUBRIQUE_ALERTE, "Alerte"),
        (RUBRIQUE_DIVERS, "Divers"),
    ]

    SERVICE_EXAMENS = "examens"
    SERVICE_CONCOURS = "concours"
    SERVICE_CERTIFICATIONS = "certifications"
    SERVICE_VAE = "vae"
    SERVICE_SCOLARITE = "scolarite"
    SERVICE_SI = "si"
    SERVICE_AUTRE = "autre"
    SERVICE_CHOICES = [
        (SERVICE_EXAMENS, "Examens"),
        (SERVICE_CONCOURS, "Concours"),
        (SERVICE_CERTIFICATIONS, "Certifications"),
        (SERVICE_VAE, "VAE"),
        (SERVICE_SCOLARITE, "Scolarité"),
        (SERVICE_SI, "SI"),
        (SERVICE_AUTRE, "Autre"),
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
    service = models.CharField("Service concerné", max_length=32, choices=SERVICE_CHOICES)
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
