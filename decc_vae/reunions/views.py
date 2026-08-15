"""Vues CRUD, tableau de bord, filtres et exports — DECC/VAE."""
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe

from .export_excel import export_all_reunions_xlsx, export_reunion_xlsx
from .export_pdf import export_reunion_pdf
from .export_word import export_reunion_docx
from .forms import PointForm, PointFormSet, ReunionFilterForm, ReunionForm
from .models import Point, Reunion


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next") or request.POST.get("next")
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect("dashboard")
        error = "Identifiant ou mot de passe incorrect."
    return render(request, "reunions/login.html", {"error": error})


def logout_view(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect("login")


def dashboard(request):
    points = Point.objects.all()
    reunions = Reunion.objects.all()
    stats = {
        "nb_reunions": reunions.count(),
        "nb_critiques": points.filter(urgence=5).count(),
        "nb_urgents": points.filter(urgence__gte=4).count(),
        "nb_faits": points.filter(statut=Point.STATUT_FAIT).count(),
        "nb_en_cours": points.filter(statut=Point.STATUT_EN_COURS).count(),
        "nb_a_faire": points.filter(statut=Point.STATUT_A_FAIRE).count(),
    }
    types = list(
        reunions.values("type").annotate(total=Count("id")).order_by("type")
    )
    type_labels = dict(Reunion.TYPE_CHOICES)
    chart_types = {
        "labels": [type_labels.get(row["type"], row["type"]) for row in types],
        "data": [row["total"] for row in types],
    }
    by_month = (
        reunions.annotate(mois=TruncMonth("date"))
        .values("mois")
        .annotate(total=Count("id"))
        .order_by("mois")
    )
    chart_mois = {
        "labels": [row["mois"].strftime("%m/%Y") if row["mois"] else "" for row in by_month],
        "data": [row["total"] for row in by_month],
    }
    services = list(points.values("service").annotate(total=Count("id")).order_by("service"))
    service_labels = dict(Point.SERVICE_CHOICES)
    chart_services = {
        "labels": [service_labels.get(row["service"], row["service"]) for row in services],
        "data": [row["total"] for row in services],
    }
    urgences = []
    for level in range(1, 6):
        urgences.append(points.filter(urgence=level).count())
    return render(
        request,
        "reunions/dashboard.html",
        {
            "stats": stats,
            "dernieres": reunions[:5],
            "points_critiques": points.filter(urgence=5).select_related("reunion")[:15],
            "chart_types": mark_safe(json.dumps(chart_types)),
            "chart_mois": mark_safe(json.dumps(chart_mois)),
            "chart_services": mark_safe(json.dumps(chart_services)),
            "chart_urgences": mark_safe(json.dumps(urgences)),
        },
    )


def _filtered_reunions(request):
    form = ReunionFilterForm(request.GET or None)
    qs = Reunion.objects.all().prefetch_related("points")
    if form.is_valid():
        data = form.cleaned_data
        if data.get("date_debut"):
            qs = qs.filter(date__gte=data["date_debut"])
        if data.get("date_fin"):
            qs = qs.filter(date__lte=data["date_fin"])
        if data.get("type"):
            qs = qs.filter(type__in=data["type"])
        if data.get("service"):
            qs = qs.filter(points__service=data["service"]).distinct()
        if data.get("urgence"):
            qs = qs.filter(points__urgence=int(data["urgence"])).distinct()
        if data.get("statut"):
            qs = qs.filter(points__statut=data["statut"]).distinct()
        q = (data.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(president__icontains=q)
                | Q(rapporteur__icontains=q)
                | Q(lieu__icontains=q)
                | Q(observations__icontains=q)
                | Q(objet_prochaine__icontains=q)
                | Q(points__sujet__icontains=q)
            ).distinct()
    return form, qs


def reunion_list(request):
    form, qs = _filtered_reunions(request)
    return render(request, "reunions/reunion_list.html", {"form": form, "reunions": qs})


def reunion_detail(request, pk):
    reunion = get_object_or_404(Reunion.objects.prefetch_related("points"), pk=pk)
    return render(request, "reunions/reunion_detail.html", {"reunion": reunion})


def reunion_create(request):
    reunion = Reunion()
    if request.method == "POST":
        form = ReunionForm(request.POST)
        formset = PointFormSet(request.POST, instance=reunion)
        if form.is_valid():
            reunion = form.save(commit=False)
            reunion.cree_par = request.user
            reunion.save()
            formset = PointFormSet(request.POST, instance=reunion)
            if formset.is_valid():
                formset.save()
                messages.success(request, "La réunion a été créée.")
                return redirect("reunion_detail", pk=reunion.pk)
            reunion.delete()
            messages.error(request, "Corrigez les erreurs des points de réunion.")
            reunion = Reunion()
            form = ReunionForm(request.POST)
            formset = PointFormSet(request.POST, instance=reunion)
    else:
        form = ReunionForm()
        formset = PointFormSet(instance=reunion)
    return render(
        request,
        "reunions/reunion_form.html",
        {"form": form, "formset": formset, "titre": "Nouvelle réunion"},
    )


def reunion_update(request, pk):
    reunion = get_object_or_404(Reunion, pk=pk)
    if request.method == "POST":
        form = ReunionForm(request.POST, instance=reunion)
        formset = PointFormSet(request.POST, instance=reunion)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "La réunion a été mise à jour.")
            return redirect("reunion_detail", pk=reunion.pk)
        messages.error(request, "Corrigez les erreurs du formulaire.")
    else:
        form = ReunionForm(instance=reunion)
        formset = PointFormSet(instance=reunion)
    return render(
        request,
        "reunions/reunion_form.html",
        {"form": form, "formset": formset, "titre": "Modifier la réunion", "reunion": reunion},
    )


def reunion_delete(request, pk):
    reunion = get_object_or_404(Reunion, pk=pk)
    if request.method == "POST":
        reunion.delete()
        messages.success(request, "La réunion a été supprimée.")
        return redirect("reunion_list")
    return render(request, "reunions/reunion_confirm_delete.html", {"reunion": reunion})


def point_create(request, pk):
    reunion = get_object_or_404(Reunion, pk=pk)
    if request.method == "POST":
        form = PointForm(request.POST)
        if form.is_valid():
            point = form.save(commit=False)
            point.reunion = reunion
            point.numero = 0
            point.save()
            messages.success(request, "Le point a été ajouté.")
            return redirect("reunion_detail", pk=reunion.pk)
    else:
        form = PointForm()
    return render(
        request,
        "reunions/point_form.html",
        {"form": form, "reunion": reunion, "titre": "Ajouter un point"},
    )


def point_update(request, pk):
    point = get_object_or_404(Point.objects.select_related("reunion"), pk=pk)
    if request.method == "POST":
        form = PointForm(request.POST, instance=point)
        if form.is_valid():
            form.save()
            messages.success(request, "Le point a été modifié.")
            return redirect("reunion_detail", pk=point.reunion_id)
    else:
        form = PointForm(instance=point)
    return render(
        request,
        "reunions/point_form.html",
        {"form": form, "reunion": point.reunion, "titre": "Modifier un point"},
    )


def point_delete(request, pk):
    point = get_object_or_404(Point.objects.select_related("reunion"), pk=pk)
    reunion_id = point.reunion_id
    if request.method == "POST":
        point.delete()
        messages.success(request, "Le point a été supprimé.")
        return redirect("reunion_detail", pk=reunion_id)
    return render(request, "reunions/point_confirm_delete.html", {"point": point})


def export_pdf(request, pk):
    reunion = get_object_or_404(Reunion.objects.prefetch_related("points"), pk=pk)
    buffer = export_reunion_pdf(reunion)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="reunion_{reunion.date}_{reunion.pk}.pdf"'
    return response


def export_word(request, pk):
    reunion = get_object_or_404(Reunion.objects.prefetch_related("points"), pk=pk)
    buffer = export_reunion_docx(reunion)
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    response["Content-Disposition"] = f'attachment; filename="reunion_{reunion.date}_{reunion.pk}.docx"'
    return response


def export_excel(request, pk):
    reunion = get_object_or_404(Reunion.objects.prefetch_related("points"), pk=pk)
    buffer = export_reunion_xlsx(reunion)
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="reunion_{reunion.date}_{reunion.pk}.xlsx"'
    return response


def export_excel_all(request):
    _form, qs = _filtered_reunions(request)
    buffer = export_all_reunions_xlsx(qs)
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="decc_vae_reunions.xlsx"'
    return response
