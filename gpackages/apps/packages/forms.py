from django import forms
from .models import ArchesModel, RepositoryModel, CategoryModel, HerdsModel, \
                    UseFlagModel, MaintainerModel, LicenseModel
from .widgets import DivCheckboxSelectMultiple
from django.core.cache import cache

# Need rerun if database are empty
arches = ArchesModel.objects.exclude(name = '*').order_by('name').values_list('name', 'name')


class ArchChoiceForm(forms.Form):
    arches = forms.MultipleChoiceField(
            widget = DivCheckboxSelectMultiple,
            #widget = forms.CheckboxSelectMultiple(attrs = {'class': 'inline checkbox'}),
            choices = arches)

def get_all_choices():
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
    
    values = (repos, categories, herds, uses, licenses)
    return values

class FilteringForm(forms.Form):
    names = ['repos', 'categories', 'herds', 'uses', 'licenses']
    f_names = ['repo', 'category', 'herd', 'use', 'license']

    def __init__(self, *args, **kwargs):
        super(FilteringForm, self).__init__(*args, **kwargs)
        names = self.names
        names_cache = map(lambda x: x+'_f_list', names)
        cache_vals = cache.get_many(names_cache)
        f = False
        values = []
        for item in names_cache:
            v = cache_vals.get(item, None)
            if v is None:
                f = True
                break
            values.append(v)

        if f:
            values = get_all_choices()
            cache.set_many(dict(zip(names_cache, values)))

        for k, v in zip(names, values):
            self.fields[k].choices = v

    repos = forms.MultipleChoiceField(required = False)
    categories = forms.MultipleChoiceField(required = False)
    herds = forms.MultipleChoiceField(required = False)
    uses = forms.MultipleChoiceField(required = False)
    licenses = forms.MultipleChoiceField(required = False)
