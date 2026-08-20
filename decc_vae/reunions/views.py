"""Vues CRUD, tableau de bord, filtres, import, rapport et fusion."""
import json
import tempfile
from pathlib import Path

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe

from .export_utils import (
    excel_template,
    export_all_reunions_xlsx,
    export_rapport_pdf,
    export_rapport_word,
    export_reunion_docx,
    export_reunion_pdf,
    export_reunion_xlsx,
    import_points_from_xlsx,
)
from .forms import (
    DocumentForm,
    DocumentFormSet,
    ImportExcelForm,
    MergeDbForm,
    ParametreForm,
    PointForm,
    PointFormSet,
    RapportForm,
    ReunionFilterForm,
    ReunionForm,
)
from .merge_db import merge_sqlite_file
from .models import DocumentReunion, Parametre, Point, Reunion


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
    volets = list(points.values("volet").annotate(total=Count("id")).order_by("volet"))
    volet_labels = dict(Point.VOLET_CHOICES)
    chart_volets = {
        "labels": [volet_labels.get(row["volet"], row["volet"]) for row in volets],
        "data": [row["total"] for row in volets],
    }
    return render(
        request,
        "reunions/dashboard.html",
        {
            "stats": stats,
            "dernieres": reunions[:10],
            "points_critiques": points.filter(urgence=5).select_related("reunion")[:15],
            "chart_volets": mark_safe(json.dumps(chart_volets)),
        },
    )


def _filtered_reunions(request):
    form = ReunionFilterForm(request.GET or None)
    qs = Reunion.objects.all().annotate(
        nb_points=Count("points", distinct=True),
        nb_documents=Count("documents", distinct=True),
    )
    if form.is_valid():
        data = form.cleaned_data
        if data.get("date_debut"):
            qs = qs.filter(date__gte=data["date_debut"])
        if data.get("date_fin"):
            qs = qs.filter(date__lte=data["date_fin"])
        if data.get("type"):
            qs = qs.filter(type__in=data["type"])
        if data.get("volet"):
            qs = qs.filter(points__volet=data["volet"]).distinct()
        if data.get("urgence"):
            qs = qs.filter(points__urgence=int(data["urgence"])).distinct()
        if data.get("statut"):
            qs = qs.filter(points__statut=data["statut"]).distinct()
        q = (data.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(president__icontains=q)
                | Q(rapporteur__icontains=q)
                | Q(observations__icontains=q)
                | Q(objet_prochaine__icontains=q)
                | Q(type_autre_precision__icontains=q)
                | Q(points__sujet__icontains=q)
            ).distinct()
    return form, qs


def reunion_list(request):
    form, qs = _filtered_reunions(request)
    return render(request, "reunions/reunion_list.html", {"form": form, "reunions": qs})


def reunion_detail(request, pk):
    reunion = get_object_or_404(
        Reunion.objects.prefetch_related("points", "documents"),
        pk=pk,
    )
    return render(request, "reunions/reunion_detail.html", {"reunion": reunion})


def reunion_create(request):
    reunion = Reunion()
    if request.method == "POST":
        form = ReunionForm(request.POST)
        if form.is_valid():
            reunion = form.save(commit=False)
            reunion.cree_par = request.user
            reunion.save()
            formset = PointFormSet(request.POST, instance=reunion)
            document_formset = DocumentFormSet(request.POST, request.FILES, instance=reunion)
            if formset.is_valid() and document_formset.is_valid():
                formset.save()
                document_formset.save()
                messages.success(request, "La réunion a été créée.")
                return redirect("reunion_detail", pk=reunion.pk)
            reunion.delete()
            messages.error(request, "Corrigez les erreurs des points ou des documents.")
            reunion = Reunion()
            form = ReunionForm(request.POST)
            formset = PointFormSet(request.POST, instance=reunion)
            document_formset = DocumentFormSet(request.POST, request.FILES, instance=reunion)
        else:
            formset = PointFormSet(request.POST, instance=reunion)
            document_formset = DocumentFormSet(request.POST, request.FILES, instance=reunion)
    else:
        form = ReunionForm()
        formset = PointFormSet(instance=reunion)
        document_formset = DocumentFormSet(instance=reunion)
    return render(
        request,
        "reunions/reunion_form.html",
        {
            "form": form,
            "formset": formset,
            "document_formset": document_formset,
            "titre": "Nouvelle réunion",
        },
    )


def reunion_update(request, pk):
    reunion = get_object_or_404(Reunion, pk=pk)
    if request.method == "POST":
        form = ReunionForm(request.POST, instance=reunion)
        formset = PointFormSet(request.POST, instance=reunion)
        document_formset = DocumentFormSet(request.POST, request.FILES, instance=reunion)
        if form.is_valid() and formset.is_valid() and document_formset.is_valid():
            form.save()
            formset.save()
            document_formset.save()
            messages.success(request, "La réunion a été mise à jour.")
            return redirect("reunion_detail", pk=reunion.pk)
        messages.error(request, "Corrigez les erreurs du formulaire.")
    else:
        form = ReunionForm(instance=reunion)
        formset = PointFormSet(instance=reunion)
        document_formset = DocumentFormSet(instance=reunion)
    return render(
        request,
        "reunions/reunion_form.html",
        {
            "form": form,
            "formset": formset,
            "document_formset": document_formset,
            "titre": "Modifier la réunion",
            "reunion": reunion,
        },
    )


def documents_reunion(request, pk):
    reunion = get_object_or_404(Reunion, pk=pk)
    documents = reunion.documents.all()
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid() and not form.is_empty():
            doc = form.save(commit=False)
            doc.reunion = reunion
            doc.save()
            messages.success(request, "Document ajouté avec succès.")
            return redirect("documents_reunion", pk=reunion.pk)
        if form.is_empty():
            form.add_error("nom", "Indiquez un nom et un fichier.")
        messages.error(request, "Corrigez les erreurs du formulaire.")
    else:
        form = DocumentForm()
    return render(
        request,
        "reunions/documents_reunion.html",
        {"reunion": reunion, "documents": documents, "form": form},
    )


def supprimer_document(request, pk):
    doc = get_object_or_404(DocumentReunion.objects.select_related("reunion"), pk=pk)
    reunion_id = doc.reunion_id
    if doc.fichier:
        doc.fichier.delete(save=False)
    doc.delete()
    messages.success(request, "Document supprimé avec succès.")
    return redirect("documents_reunion", pk=reunion_id)


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
    data = export_reunion_pdf(reunion)
    response = HttpResponse(data, content_type="application/pdf")
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


def download_excel_template(request):
    buffer = excel_template()
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="modele_points_decc_vae.xlsx"'
    return response


def import_excel(request, pk):
    reunion = get_object_or_404(Reunion, pk=pk)
    if request.method == "POST":
        form = ImportExcelForm(request.POST, request.FILES)
        if form.is_valid():
            created, errors = import_points_from_xlsx(reunion, form.cleaned_data["fichier"])
            if created:
                messages.success(request, f"{created} point(s) importé(s).")
            for err in errors:
                messages.warning(request, err)
            if created:
                return redirect("reunion_detail", pk=reunion.pk)
    else:
        form = ImportExcelForm()
    return render(request, "reunions/import_excel.html", {"form": form, "reunion": reunion})


def rapport_complet(request):
    form = RapportForm(request.GET or None)
    reunions = Reunion.objects.none()
    if form.is_valid() and (form.cleaned_data.get("date_debut") or form.cleaned_data.get("date_fin") or request.GET):
        reunions = Reunion.objects.all().prefetch_related("points")
        if form.cleaned_data.get("date_debut"):
            reunions = reunions.filter(date__gte=form.cleaned_data["date_debut"])
        if form.cleaned_data.get("date_fin"):
            reunions = reunions.filter(date__lte=form.cleaned_data["date_fin"])
        if request.GET.get("download"):
            fmt = form.cleaned_data.get("format") or "pdf"
            if fmt == "word":
                buffer = export_rapport_word(reunions)
                response = HttpResponse(
                    buffer.getvalue(),
                    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
                response["Content-Disposition"] = 'attachment; filename="rapport_decc_vae.docx"'
                return response
            data = export_rapport_pdf(reunions)
            response = HttpResponse(data, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="rapport_decc_vae.pdf"'
            return response
    return render(
        request,
        "reunions/rapport_complet.html",
        {"form": form, "reunions": reunions},
    )


def merge_databases(request):
    if request.method == "POST":
        form = MergeDbForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data["fichier"]
            with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as tmp:
                for chunk in uploaded.chunks():
                    tmp.write(chunk)
                tmp_path = Path(tmp.name)
            try:
                summary = merge_sqlite_file(tmp_path)
                messages.success(
                    request,
                    (
                        f"Fusion terminée : {summary['reunions_ajoutees']} réunion(s) ajoutée(s), "
                        f"{summary['points_ajoutes']} point(s), "
                        f"{summary['doublons']} doublon(s) ignoré(s)."
                    ),
                )
            except Exception as exc:
                messages.error(request, f"Fusion impossible : {exc}")
            finally:
                tmp_path.unlink(missing_ok=True)
            return redirect("merge_db")
    else:
        form = MergeDbForm()
    return render(request, "reunions/merge_db.html", {"form": form})


@staff_member_required
def parametres(request):
    instance = Parametre.get_instance()
    if request.method == "POST":
        form = ParametreForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Paramètres mis à jour.")
            return redirect("parametres")
        messages.error(request, "Corrigez les erreurs du formulaire.")
    else:
        form = ParametreForm(instance=instance)
    return render(
        request,
        "reunions/parametres.html",
        {"form": form, "instance": instance, "titre": "Paramètres de l'application"},
    )


@staff_member_required
def supprimer_logo(request):
    instance = Parametre.get_instance()
    if instance.logo:
        instance.logo.delete(save=False)
        instance.logo = None
        instance.save()
        messages.success(request, "Logo personnalisé supprimé. Le logo par défaut est rétabli.")
    return redirect("parametres")
