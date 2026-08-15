from django import forms
from django.forms import inlineformset_factory

from .models import Point, Reunion


class ReunionForm(forms.ModelForm):
    class Meta:
        model = Reunion
        fields = [
            "date",
            "heure_debut",
            "heure_fin",
            "lieu",
            "type",
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
            "lieu": forms.TextInput(attrs={"class": "form-control"}),
            "type": forms.Select(attrs={"class": "form-select"}),
            "president": forms.TextInput(attrs={"class": "form-control"}),
            "rapporteur": forms.TextInput(attrs={"class": "form-control"}),
            "nombre_participants": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "participants_presents": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "participants_excuses": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "participants_absents": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "prochaine_reunion": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "objet_prochaine": forms.TextInput(attrs={"class": "form-control"}),
            "observations": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class PointForm(forms.ModelForm):
    class Meta:
        model = Point
        fields = [
            "rubrique",
            "service",
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
            "service": forms.Select(attrs={"class": "form-select"}),
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
    service = forms.ChoiceField(
        required=False,
        choices=[("", "Tous les services")] + list(Point.SERVICE_CHOICES),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Service",
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
            attrs={"class": "form-control", "placeholder": "Rechercher (président, lieu, objet…)"}
        ),
        label="Recherche",
    )
