from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import Parametre, Point, Reunion

LOGO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}


class ReunionForm(forms.ModelForm):
    class Meta:
        model = Reunion
        fields = [
            "date",
            "heure_debut",
            "heure_fin",
            "lieu",
            "lieu_precision",
            "type",
            "type_autre_precision",
            "president",
            "rapporteur",
            "nombre_participants",
            "participants_presents",
            "participants_excuses",
            "participants_absents",
            "prochaine_reunion",
            "objet_prochaine",
            "observations",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "heure_debut": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "heure_fin": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "lieu": forms.Select(attrs={"class": "form-select", "id": "id_lieu"}),
            "lieu_precision": forms.TextInput(attrs={"class": "form-control", "id": "id_lieu_precision"}),
            "type": forms.Select(attrs={"class": "form-select", "id": "id_type"}),
            "type_autre_precision": forms.TextInput(
                attrs={"class": "form-control", "id": "id_type_autre_precision"}
            ),
            "president": forms.TextInput(attrs={"class": "form-control"}),
            "rapporteur": forms.TextInput(attrs={"class": "form-control"}),
            "nombre_participants": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "participants_presents": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "participants_excuses": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "participants_absents": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "prochaine_reunion": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "objet_prochaine": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "observations": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class PointForm(forms.ModelForm):
    class Meta:
        model = Point
        fields = [
            "rubrique",
            "volet",
            "volet_autre_precision",
            "sujet",
            "decision",
            "action",
            "responsable",
            "delai",
            "urgence",
            "statut",
        ]
        widgets = {
            "rubrique": forms.Select(attrs={"class": "form-select"}),
            "volet": forms.Select(attrs={"class": "form-select js-volet"}),
            "volet_autre_precision": forms.TextInput(attrs={"class": "form-control js-volet-autre"}),
            "sujet": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "decision": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "action": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "responsable": forms.TextInput(attrs={"class": "form-control"}),
            "delai": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "urgence": forms.Select(attrs={"class": "form-select"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
        }


PointFormSet = inlineformset_factory(
    Reunion,
    Point,
    form=PointForm,
    extra=2,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


class ReunionFilterForm(forms.Form):
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Date de début",
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Date de fin",
    )
    type = forms.MultipleChoiceField(
        required=False,
        choices=Reunion.TYPE_CHOICES,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": "4"}),
        label="Type",
    )
    volet = forms.ChoiceField(
        required=False,
        choices=[("", "Tous les volets")] + list(Point.VOLET_CHOICES),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Volet",
    )
    urgence = forms.ChoiceField(
        required=False,
        choices=[("", "Toutes")] + [(str(i), str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Urgence",
    )
    statut = forms.ChoiceField(
        required=False,
        choices=[("", "Tous les statuts")] + list(Point.STATUT_CHOICES),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Statut des points",
    )
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Rechercher (président, sujet…)"}
        ),
        label="Recherche",
    )


class ImportExcelForm(forms.Form):
    fichier = forms.FileField(
        label="Fichier Excel (.xlsx)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx"}),
    )


class RapportForm(forms.Form):
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Date de début",
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Date de fin",
    )
    format = forms.ChoiceField(
        choices=[("pdf", "PDF"), ("word", "Word")],
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Format",
        initial="pdf",
    )


class MergeDbForm(forms.Form):
    fichier = forms.FileField(
        label="Base SQLite à fusionner (.sqlite3 / .db)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".sqlite3,.db,.sqlite"}),
    )


class ParametreForm(forms.ModelForm):
    class Meta:
        model = Parametre
        fields = ["logo", "logo_actif", "nom_application"]
        widgets = {
            "logo": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/png,image/jpeg,image/svg+xml"}
            ),
            "logo_actif": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "nom_application": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get("logo")
        if not logo:
            return logo
        name = getattr(logo, "name", "") or ""
        ext = name[name.rfind(".") :].lower() if "." in name else ""
        if ext not in LOGO_EXTENSIONS:
            raise ValidationError("Formats acceptés : PNG, JPG, SVG.")
        if ext != ".svg":
            try:
                from PIL import Image

                logo.seek(0)
                image = Image.open(logo)
                if image.width > 200 or image.height > 200:
                    raise ValidationError("Le logo ne doit pas dépasser 200 × 200 pixels.")
                logo.seek(0)
            except ValidationError:
                raise
            except Exception:
                raise ValidationError("Fichier image invalide.")
        return logo
