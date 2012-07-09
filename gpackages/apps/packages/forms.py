from django import forms
from .models import ArchesModel, RepositoryModel, CategoryModel, HerdsModel, \
                    UseFlagModel, MaintainerModel, LicenseModel
from .widgets import DivCheckboxSelectMultiple

# Need rerun if database are empty
arches = ArchesModel.objects.exclude(name = '*').order_by('name').values_list('name', 'name')


class ArchChoiceForm(forms.Form):
    arches = forms.MultipleChoiceField(
            widget = DivCheckboxSelectMultiple,
            #widget = forms.CheckboxSelectMultiple(attrs = {'class': 'inline checkbox'}),
            choices = arches)

class FilteringForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FilteringForm, self).__init__(*args, **kwargs)
        repos = RepositoryModel.objects.all().order_by('name'). \
            values_list('name', 'name')

        categories = CategoryModel.objects.all().order_by('category'). \
            values_list('category', 'category')

        herds = HerdsModel.objects.all().order_by('name'). \
            values_list('name','name')

        uses = UseFlagModel.objects.all().order_by('name'). \
            values_list('name', 'name')

        #maintainers = MaintainerModel.all().order_by('email'). \
        #    values_list('pk', 'email')

        licenses = LicenseModel.objects.all().order_by('name'). \
            values_list('name', 'name')
        
        names = ['repos', 'categories', 'herds', 'uses', 'licenses']
        values = [repos, categories, herds, uses, licenses]
        for k, v in zip(names, values):
            self.fields[k].choices = v

    repos = forms.MultipleChoiceField(required = False)
    categories = forms.MultipleChoiceField(required = False)
    herds = forms.MultipleChoiceField(required = False)
    uses = forms.MultipleChoiceField(required = False)
    licenses = forms.MultipleChoiceField(required = False)
