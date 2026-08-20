from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import DocumentReunion, Parametre, Point, Reunion

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sujet"].required = False
        self.fields["volet"].required = False

    def is_empty(self):
        if not hasattr(self, "cleaned_data"):
            return True
        data = self.cleaned_data
        return not any(
            [
                (data.get("sujet") or "").strip(),
                (data.get("decision") or "").strip(),
                (data.get("action") or "").strip(),
                (data.get("responsable") or "").strip(),
                data.get("delai"),
            ]
        )

    def clean(self):
        cleaned = super().clean()
        sujet = (cleaned.get("sujet") or "").strip()
        decision = (cleaned.get("decision") or "").strip()
        action = (cleaned.get("action") or "").strip()
        responsable = (cleaned.get("responsable") or "").strip()
        if not any([sujet, decision, action, responsable, cleaned.get("delai")]):
            return cleaned
        if not sujet:
            self.add_error("sujet", "Le sujet est obligatoire.")
        if not cleaned.get("volet"):
            self.add_error("volet", "Le volet est obligatoire.")
        cleaned["sujet"] = sujet
        return cleaned


class BasePointFormSet(BaseInlineFormSet):
    def save_new_objects(self, commit=True):
        self.new_objects = []
        for form in self.extra_forms:
            if not hasattr(form, "cleaned_data") or form.is_empty():
                continue
            if self.can_delete and self._should_delete_form(form):
                continue
            self.new_objects.append(self.save_new(form, commit=commit))
            if not commit:
                self.saved_forms.append(form)
        return self.new_objects


PointFormSet = inlineformset_factory(
    Reunion,
    Point,
    form=PointForm,
    formset=BasePointFormSet,
    extra=1,
    max_num=50,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


class DocumentForm(forms.ModelForm):
    class Meta:
        model = DocumentReunion
        fields = ["nom", "fichier", "description"]
        widgets = {
            "nom": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nom du document"}
            ),
            "fichier": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Description (optionnel)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nom"].required = False
        self.fields["fichier"].required = False
        self.fields["description"].required = False

    def is_empty(self):
        if not hasattr(self, "cleaned_data"):
            return True
        data = self.cleaned_data
        return not any(
            [
                (data.get("nom") or "").strip(),
                data.get("fichier"),
                (data.get("description") or "").strip(),
            ]
        )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        nom = (cleaned.get("nom") or "").strip()
        fichier = cleaned.get("fichier")
        description = (cleaned.get("description") or "").strip()
        if not nom and not fichier and not description:
            return cleaned
        if not nom:
            self.add_error("nom", "Le nom du document est obligatoire.")
        if not fichier and not self.instance.pk:
            self.add_error("fichier", "Le fichier est obligatoire.")
        cleaned["nom"] = nom
        cleaned["description"] = description
        return cleaned


class BaseDocumentFormSet(BaseInlineFormSet):
    def save_new_objects(self, commit=True):
        self.new_objects = []
        for form in self.extra_forms:
            if not hasattr(form, "cleaned_data") or form.is_empty():
                continue
            if self.can_delete and self._should_delete_form(form):
                continue
            self.new_objects.append(self.save_new(form, commit=commit))
            if not commit:
                self.saved_forms.append(form)
        return self.new_objects


DocumentFormSet = inlineformset_factory(
    Reunion,
    DocumentReunion,
    form=DocumentForm,
    formset=BaseDocumentFormSet,
    extra=1,
    max_num=50,
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
