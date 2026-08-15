from django.contrib import admin

from .models import Point, Reunion


class PointInline(admin.TabularInline):
    model = Point
    extra = 1


@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display = ("date", "type", "lieu", "president", "rapporteur", "nombre_participants")
    list_filter = ("type", "date")
    search_fields = ("president", "rapporteur", "lieu", "observations")
    inlines = [PointInline]


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ("numero", "reunion", "rubrique", "service", "urgence", "statut", "responsable")
    list_filter = ("service", "urgence", "statut", "rubrique")
    search_fields = ("sujet", "decision", "action", "responsable")
