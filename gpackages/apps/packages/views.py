from django.views.generic import DetailView, FormView, ListView
from generic.views import ContextListView, ContextTemplateView, ContextView, \
                          MultipleFilterListViewMixin, RightAtom1Feed, \
                          FeedWithUpdated

from .models import CategoryModel, HerdsModel, MaintainerModel, \
                    RepositoryModel, LicenseGroupModel, EbuildModel, \
                    PackageModel, UseFlagModel, PortageNewsModel, \
                    UseFlagDescriptionModel, LicenseModel
from .forms import ArchChoiceForm, FilteringForm
from django.core.urlresolvers import reverse

from django.shortcuts import get_object_or_404
from django.http import Http404
from package_info.parse_cp import EbuildParseCPVR, PackageParseCPR
from django.contrib.sitemaps import Sitemap

arches = ['alpha', 'amd64', 'arm', 'hppa', 'ia64', 'ppc', 'ppc64', 'sparc', 'x86']

class ArchesViewMixin(object):
    def get_arches(self):
        arches_s = self.request.session.get('arches')
        return arches_s or arches
        

class ArchesContexView(ArchesViewMixin, ContextView):
    def get_context_data(self, **kwargs):
        ret = super(ArchesContexView, self).get_context_data(**kwargs)
        ret.update({'arches': self.get_arches()})
        return ret

    def get_queryset(self):
        query = super(ArchesContexView, self).get_queryset()
        return query.prefetch_keywords(self.get_arches())

class ContextArchListView(ArchesContexView, ListView):
    pass

class CategoriesListView(ContextListView):
    extra_context = {'page_name': 'Categories',}
    template_name = 'categories.html'
    queryset = CategoryModel.objects.defer('metadata_hash').all()
    context_object_name = 'categories'

class HerdsListView(ContextListView):
    extra_context = {'page_name': 'Herds',}
    template_name = 'herds.html'
    queryset = HerdsModel.objects.only('name', 'email', 'description').all()
    context_object_name = 'herds'

class MaintainersListView(ContextListView):
    paginate_by = 40
    extra_context = {'page_name': 'Maintainers',}
    template_name = 'maintainers.html'
    queryset = MaintainerModel.objects.only('name', 'email' ).all()
    context_object_name = 'maintainers'

class RepositoriesListView(ContextListView):
    extra_context = {'page_name': 'Repsitories',}
    template_name = 'repositories.html'
    queryset = RepositoryModel.objects.only('name', 'description' ).all()
    context_object_name = 'repositories'

class LicenseGroupsView(ContextListView):
    extra_context = {'page_name': 'License Groups',}
    queryset = LicenseGroupModel.objects.all().prefetch_related('licenses')
    template_name = 'license_groups.html'
    context_object_name = 'license_groups'

class EbuildsListView(ContextArchListView):
    paginate_by = 40
    extra_context = {'page_name': 'Ebuilds', 'arches' : arches}
    template_name = 'ebuilds.html'
    context_object_name = 'ebuilds'
    queryset = EbuildModel.objects.all(). \
        select_related('package',
                       'package__virtual_package',
                       'package__virtual_package__category'). \
                       prefetch_related('package__repository')

class AtomDetailViewMixin(ArchesContexView, DetailView):
    parsing_class = EbuildParseCPVR

    def get_parsed(self):
        parsed, atom = self.kwargs.get('parsed'), self.kwargs.get('atom')
        if parsed is not None:
            return parsed
        else:
            return self.parsing_class(atom)

class EbuildDetailView(AtomDetailViewMixin):
    parsing_class = EbuildParseCPVR
    template_name = 'ebuild.html'
    extra_context = {'page_name': 'Ebuild', 'arches': arches}
    context_object_name = 'ebuild'
    queryset = EbuildModel.objects.all(). \
        select_related('package',
                       'package__virtual_package',
                       'package__virtual_package__category')


    def get_object(self, queryset = None):
        pk = self.kwargs.get('pk')
        if pk is not None:
            return super(EbuildDetailView, self).get_object(queryset)
        if queryset is None:
            queryset = self.get_queryset()

        eo = self.get_parsed()
        category, name = eo.category, eo.name
        version, revision = eo.version, eo.revision_for_q
        repository = eo.repository_for_q
        obj = get_object_or_404(queryset, package__virtual_package__name = name,
                                          package__virtual_package__category__category = category,
                                          package__repository__name = repository,
                                          version = version,
                                          revision = revision)
        return obj

class PackagesListsView(MultipleFilterListViewMixin, ContextArchListView):
    allowed_filter = { 'category':'virtual_package__category__category',
                       'repo':'repository__name',
                       'herd':'herds__name',
                       'maintainer': 'maintainers__pk',
                       'license': 'ebuildmodel__licenses__name',
                       'use': 'ebuildmodel__use_flags__name'
                    }

    m2m_filter = set(['herd', 'maintainer', 'license', 'use'])

    allowed_order = { 'create': 'created_datetime',
                      'update': 'updated_datetime',
                      'rand':'?', # it slow
                      None: '-updated_datetime'
                    }
    allowed_many = {'repo': 5, 'use' : 3, 'herd': 4, 'category': 4, 'license': 3}

    paginate_by = 40
    extra_context = {'page_name': 'Packages', 'arches': arches}
    template_name = 'packages.html'
    context_object_name = 'packages'
    # Faster query !!
    #SELECT t.id, t.virtual_package_id, t.description, t.repository_id, vp.id
    #as virtual_package__name FROM 
    #(SELECT * FROM packages_packagemodel 
    #ORDER BY updated_datetime DESC LIMIT 3 ) as t 
    #INNER JOIN packages_virtualpackagemodel vp 
    #ON( `vp`.id = t.virtual_package_id) INNER JOIN `packages_categorymodel` cp
    #ON (vp.category_id = cp.id);
    queryset = PackageModel.objects.all(). \
        select_related('virtual_package',
                       'virtual_package__category'). \
        prefetch_related('repository', 'herds', 
                         'maintainers', 'latest_ebuild__homepages')

class PackageDetailView(AtomDetailViewMixin):
    parsing_class = PackageParseCPR
    template_name = 'package.html'
    extra_context = {'page_name': 'Package', 'arches': arches}
    context_object_name = 'package'
    queryset = PackageModel.objects.all(). \
        select_related('virtual_package',
                       'virtual_package__category'). \
        prefetch_related('repository')

    def get_object(self, queryset = None):
        pk = self.kwargs.get('pk')
        if pk is not None:
            return super(PackageDetailView, self).get_object(queryset)
        if queryset is None:
            queryset = self.get_queryset()

        po = self.get_parsed()
        if not po.is_valid:
            raise Http404
        category, name = po.category, po.name
        repository = po.repository_for_q
        obj = get_object_or_404(queryset, name = name,
                                          category = category,
                                          repository__name = repository)
        return obj

class GlobalUseListView(ContextListView):
    extra_context = {'page_name': 'Global Use', }
    template_name = 'global_use.html'
    context_object_name = 'uses'
    queryset = UseFlagModel.objects.exclude(description = '') 

class LocalUseListView(ContextListView):
    extra_context = {'page_name': 'Local Use'}
    template_name = 'local_use.html'
    context_object_name = 'uses'
    queryset = UseFlagDescriptionModel.objects.all().\
        select_related('use_flag', 'package', 'package__category')

class NewsListView(ContextListView):
    extra_context = {'page_name': 'News'}
    template_name = 'portage_news.html'
    context_object_name = 'news'
    paginate_by = 20
    queryset = PortageNewsModel.objects.filter(lang = 'en'). \
        prefetch_related('authors', 'translators')

class NewsDetailView(ContextView, DetailView):
    extra_context = {'page_name': 'News Item'}
    template_name = 'portage_news_item.html'
    context_object_name = 'news_item'
    slug_field = 'name'
    queryset = PortageNewsModel.objects.filter(lang = 'en'). \
        prefetch_related('authors', 'translators')

class LicensesListView(ContextListView):
    extra_context = {'page_name': 'Licens'}
    template_name = 'licenses.html'
    context_object_name = 'licenses'
    paginate_by = 20
    queryset = LicenseModel.objects.all()

class LicenseDetailView(ContextView, DetailView):
    extra_context = {'page_name': 'Licens'}
    template_name = 'license.html'
    context_object_name = 'license'
    slug_field = 'name'
    queryset = LicenseModel.objects.all()
    
class ArchChoiceView(ContextView, ArchesViewMixin, FormView):
    form_class = ArchChoiceForm
    template_name = 'arch_choice.html'
    success_url = '/'
    extra_context = {'page_name': 'Select arches', 
                     'default_arches': arches}

    def __init__(self, *args, **kwargs):
        super(ArchChoiceView, self).__init__(*args, **kwargs)
        self.next_url = None

    def get_initial(self):
        arches = self.get_arches()
        return {'arches': arches }

    def get_success_url(self):
        val = super(ArchChoiceView, self).get_success_url()
        return  self.next_url or val

    def form_valid(self, form):
        arches = sorted(form.cleaned_data['arches'])
        # Maybe save it to cookies ?
        # arches_str = ','.join(arches)
        self.request.session['arches'] = arches
        self.next_url = form.cleaned_data['next']
        return super(ArchChoiceView, self).form_valid(form)

class FilteringView(FormView):
    form_class = FilteringForm
    template_name = 'filtering_view.html'
    success_url = '/'
    params_dict = { 'repos': 'repo',
                    'herds': 'herd',
                    'categories': 'category',
                    'licenses': 'license',
                    'uses': 'use'
                  }

    def form_valid(self, form):
        self.form_data = form.cleaned_data
        return super(FilteringView, self).form_valid(form)

    def get_success_url(self):
        dct = {}
        for k, v in self.params_dict.iteritems():
            vv = self.form_data[k]
            if vv:
                dct[v] = ','.join(vv)
        return reverse('packages', kwargs = dct)

class RepoDetailView(DetailView):
    template_name = 'repository.html'
    context_object_name = 'repository'
    slug_field = 'name'
    queryset = RepositoryModel.objects.all()

class MainPageFeed(FeedWithUpdated):
    title = 'Feed'
    link = '/rss/'
    description = 'Descr'

    def items(self):
        return EbuildModel.objects.all()[:40]

    def item_title(self, item):
        return item.cpv_or_cpvr()

    def item_description(self, item):
        return item.description

    def item_pubdate(self, item):
        return item.created_datetime

    def item_update(self, item):
        return item.updated_datetime

class MainPageFeedAtom(MainPageFeed):
    link = '/atom/'
    feed_type = RightAtom1Feed

class PackageSitemap(Sitemap):
    priority = 0.9
    changefreq = "hourly"

    def items(self):
        return PackageModel.objects.all()[:1000]

    def lastmod(self, obj):
        return obj.updated_datetime

def auto_package_or_ebuild(request, atom):
    v_atom = EbuildParseCPVR(atom)
    if v_atom.is_valid:
        return EbuildDetailView.as_view()(request, parsed = v_atom)
    p_atom = PackageParseCPR(atom)
    if p_atom.is_valid:
        return PackageDetailView.as_view()(request, parsed = p_atom)
    else:
        raise Http404
