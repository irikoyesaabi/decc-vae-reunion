from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", login_required(views.dashboard), name="dashboard"),
    path("reunions/", login_required(views.reunion_list), name="reunion_list"),
    path("reunions/nouvelle/", login_required(views.reunion_create), name="reunion_create"),
    path("reunions/export-excel/", login_required(views.export_excel_all), name="export_excel_all"),
    path("reunions/rapport/", login_required(views.rapport_complet), name="rapport_complet"),
    path("reunions/fusion/", login_required(views.merge_databases), name="merge_db"),
    path("reunions/modele-excel/", login_required(views.download_excel_template), name="excel_template"),
    path("reunions/<int:pk>/", login_required(views.reunion_detail), name="reunion_detail"),
    path("reunions/<int:pk>/modifier/", login_required(views.reunion_update), name="reunion_update"),
    path("reunions/<int:pk>/supprimer/", login_required(views.reunion_delete), name="reunion_delete"),
    path("reunions/<int:pk>/export/pdf/", login_required(views.export_pdf), name="export_pdf"),
    path("reunions/<int:pk>/export/word/", login_required(views.export_word), name="export_word"),
    path("reunions/<int:pk>/export/excel/", login_required(views.export_excel), name="export_excel"),
    path("reunions/<int:pk>/import-excel/", login_required(views.import_excel), name="import_excel"),
    path("reunions/<int:pk>/documents/", login_required(views.documents_reunion), name="documents_reunion"),
    path("documents/supprimer/<int:pk>/", login_required(views.supprimer_document), name="supprimer_document"),
    path("reunions/<int:pk>/points/ajouter/", login_required(views.point_create), name="point_create"),
    path("points/<int:pk>/modifier/", login_required(views.point_update), name="point_update"),
    path("points/<int:pk>/supprimer/", login_required(views.point_delete), name="point_delete"),
    path("parametres/", views.parametres, name="parametres"),
    path("parametres/supprimer-logo/", views.supprimer_logo, name="supprimer_logo"),
]

admin.site.site_header = "Administration DECC/VAE"
admin.site.site_title = "DECC/VAE"
admin.site.index_title = "Gestion des réunions"
