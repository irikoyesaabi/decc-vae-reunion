from django.contrib import admin

from .models import DocumentReunion, Parametre, Point, Reunion


class PointInline(admin.TabularInline):
    model = Point
    extra = 1


class DocumentReunionInline(admin.TabularInline):
    model = DocumentReunion
    extra = 0


@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display = ("date", "type", "lieu", "president", "rapporteur", "nombre_participants")
    list_filter = ("type", "lieu", "date")
    search_fields = ("president", "rapporteur", "observations")
    inlines = [PointInline, DocumentReunionInline]


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ("numero", "reunion", "rubrique", "volet", "urgence", "statut", "responsable")
    list_filter = ("volet", "urgence", "statut", "rubrique")
    search_fields = ("sujet", "decision", "action", "responsable")


@admin.register(DocumentReunion)
class DocumentReunionAdmin(admin.ModelAdmin):
    list_display = ("nom", "reunion", "date_ajout")
    list_filter = ("date_ajout",)
    search_fields = ("nom", "description")


@admin.register(Parametre)
class ParametreAdmin(admin.ModelAdmin):
    list_display = ("nom_application", "logo_actif", "date_modification")

    def has_add_permission(self, request):
        return not Parametre.objects.exists()
