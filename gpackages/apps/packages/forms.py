from django import forms
from .models import ArchesModel
from .widgets import DivCheckboxSelectMultiple

# Need rerun if database are empty
arches = ArchesModel.objects.exclude(name = '*').order_by('name').values_list('name', 'name')


class ArchChoiceForm(forms.Form):
    arches = forms.MultipleChoiceField(
            widget = DivCheckboxSelectMultiple,
            #widget = forms.CheckboxSelectMultiple(attrs = {'class': 'inline checkbox'}),
            choices = arches)
