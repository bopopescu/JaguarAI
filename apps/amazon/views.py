from django.contrib.auth.views import LoginView
from django.db.models import Count, Q, F, DecimalField, Expression, \
    ExpressionWrapper
from django.http import HttpResponse
from django.views.generic import DetailView, ListView, TemplateView

from apps.amazon.models import Search, FavoriteProduct, SavedSearch, Product


class JaguarLoginView(LoginView):
    redirect_authenticated_user = True


class HomePageView(TemplateView):
    template_name = "amazon/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        # TODO: make this use last used instead of modified
        q = SavedSearch.objects.filter(
            user=self.request.user).order_by("-modified_at")[0:3]
        for _ in q:
            _.annotate_query_params()
        context["saved_searches"] = q

        # TODO: This annotate is used twice. Make it into a qset thingy
        q = Product.objects.exclude(fba_fee=float('nan')).filter(
            favoriteproduct__user=self.request.user
        ).annotate(
            revenue=ExpressionWrapper(
                (F('min_price') - F('fba_fee')) * F('est_sales'),
                output_field=DecimalField()
            )
        ).order_by('-revenue')[0:3]
        for o in q:
            fav = FavoriteProduct.objects.filter(
                user=self.request.user,
                product=o,
            ).first()
            o.user_likes = bool(fav)
            o.unit_cost = fav.unit_cost
        context["favorite_products"] = q

        # Get the query params as context
        def get(key, default=''):
            v = self.request.GET.get(key, default)
            if v is '':
                return default
            try:
                return int(v) if v is not None else 0
            except ValueError:
                return v
        context['params'] = dict(
            limit=get('limit', 500),
            min_volume=get('min_volume', 10),
            min_price=get('min_price', 20),
            max_price=get('max_price', 100),
            min_reviews=get('min_reviews', 1),
            max_reviews=get('max_reviews', 50),
            sorting=get('sorting', '-avg_volume'),
            category=get('category', None),
            query=get('query'),
        )
        return context


class AboutPageView(TemplateView):
    template_name = "amazon/about.html"


class SearchListView(ListView):
    model = Search

    def get_queryset(self):
        q = super().get_queryset()

        def get(key, default=''):
            v = self.request.GET.get(key, default)
            if v is '':
                return default
            try:
                return int(v) if v is not None else 0
            except ValueError:
                return v

        # Parse query params
        limit = get('limit', 500)
        min_volume = get('min_volume', 5)
        min_price = get('min_price', 5)
        max_price = get('max_price', 500)
        min_reviews = get('min_reviews', 1)
        max_reviews = get('max_reviews', 100)
        sorting = get('sorting', '-avg_revenue')
        category = get('category', None)
        query = get('query')

        # Build the queryset
        q = q.annotate(count=Count('products')).exclude(count=0)
        q = q.filter(avg_volume__gt=min_volume)
        q = q.filter(
            avg_price__gte=min_price, avg_price__lte=max_price)
        q = q.filter(
            avg_review_count__gt=min_reviews, avg_review_count__lt=max_reviews)
        if category:
            q = q.filter(browse_node__top_level_node=category)
        if query:
            q = q.filter(
                Q(name__icontains=query) | Q(products__name__icontains=query)
            )
        return q.order_by(sorting)[0:limit]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the query params as context
        def get(key, default=''):
            v = self.request.GET.get(key, default)
            if v is '':
                return default
            try:
                return int(v) if v is not None else 0
            except ValueError:
                return v
        context['params'] = dict(
            limit=get('limit', 500),
            min_volume=get('min_volume', 5),
            min_price=get('min_price', 5),
            max_price=get('max_price', 500),
            min_reviews=get('min_reviews', 1),
            max_reviews=get('max_reviews', 100),
            sorting=get('sorting', '-avg_volume'),
            category=get('category', None),
            query=get('query'),
        )

        # Get nice stats for subheader
        c = self.get_queryset().count()
        context['subheader_stat'] = f'{c:0,} Categories'
        context['sort_options'] = (
            ("-avg_volume", "Volume"),
            ("avg_price", "Price (Asc)"),
            ("-avg_price", "Price (Desc)"),
            ("-avg_revenue", "Avg Revenue"),
            ("-max_revenue", "Max Revenue"),
            ("avg_review_count", "Avg Reviews (Asc)"),
            ("-avg_review_count", "Avg Reviews (Desc)"),
        )
        return context


class SearchDetailView(DetailView):
    model = Search

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sorting = self.request.GET.get('sorting', '-revenue')
        context['products'] = context['object'].products.exclude(fba_fee=float('nan')).order_by(
            sorting
        ).annotate(
            revenue=ExpressionWrapper(
                (F('min_price') - F('fba_fee')) * F('est_sales'),
                output_field=DecimalField()
            )
        )
        for o in context['products']:
            o.user_likes = FavoriteProduct.objects.filter(
                user=self.request.user,
                product=o,
            ).exists()
        context['params'] = self.request.GET

        c = context["products"].count()
        context['subheader_stat'] = f'{c:0,} Products on 1st Page'
        context['sort_options'] = (
            ("-est_sales", "Volume"),
            ("min_price", "Price (Asc)"),
            ("-min_price", "Price (Desc)"),
            ("-revenue", "Revenue"),  # TODO: Annotate
            ("review_count", "# Reviews (Asc)"),
            ("-review_count", "# Reviews (Desc)"),
        )
        return context


class FavoriteProductsListView(ListView):
    model = Product
    template_name = "amazon/favoriteproduct_list.html"

    def get_queryset(self):
        q = super().get_queryset()
        sorting = self.request.GET.get('sorting', '-est_sales')
        q = q.filter(
            favoriteproduct__user=self.request.user
        ).annotate(
            revenue=ExpressionWrapper(
                (F('min_price') - F('fba_fee')) * F('est_sales'),
                output_field=DecimalField()
            )
        ).order_by(sorting)
        return q

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for o in context['object_list']:
            fav = FavoriteProduct.objects.filter(
                user=self.request.user,
                product=o,
            ).first()
            o.user_likes = bool(fav)
            o.unit_cost = fav.unit_cost

        c = self.get_queryset().count()
        context['subheader_stat'] = f'{c:0,} Favorite Products'
        context['sort_options'] = (
            ("-est_sales", "Volume"),
            ("min_price", "Price (Asc)"),
            ("-min_price", "Price (Desc)"),
            ("-revenue", "Revenue"),  # TODO: Annotate
            ("review_count", "# Reviews (Asc)"),
            ("-review_count", "# Reviews (Desc)"),
        )
        return context

    def post(self, request):
        asin = request.POST['asin']
        unit_cost = request.POST.get('unit_cost')

        if unit_cost is not None:
            p = FavoriteProduct.objects.get(
                product__asin=asin, user=request.user)
            p.unit_cost = unit_cost
            p.save()
            return HttpResponse(status=200)
        else:
            p = Product.objects.get(asin=asin)
            FavoriteProduct.objects.get_or_create(
                product=p, user=request.user)
            return HttpResponse(status=201)

    def delete(self, request):
        asin = request.GET['asin']
        p = Product.objects.get(asin=asin)
        FavoriteProduct.objects.filter(
            product=p, user=request.user
        ).delete()
        return HttpResponse(status=201)


class SavedSearchesListView(ListView):
    model = SavedSearch

    def get_queryset(self):
        q = super().get_queryset()
        q = q.filter(user=self.request.user)
        for _ in q:
            _.annotate_query_params()
        return q

    def post(self, request):
        string = request.POST['paramString']
        name = request.POST['name']
        SavedSearch.objects.get_or_create(
            user=request.user, param_string=string, name=name)
        return HttpResponse(status=201)

    def delete(self, request):
        sid = request.GET['id']
        SavedSearch.objects.filter(id=sid, user=request.user).delete()
        return HttpResponse(status=201)
