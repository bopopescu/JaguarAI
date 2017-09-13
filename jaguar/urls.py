from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

from apps.amazon import views as amazon
from apps.users import views as users

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', amazon.JaguarLoginView.as_view(), name='login'),
    url(r'^reset-password/$',
        users.PasswordResetView.as_view(),
        name='reset-password'),
    url(r'^accounts/login/$', amazon.JaguarLoginView.as_view(), name='login'),
    url(r'^logout/$', login_required(LogoutView.as_view()), name='logout'),
    url(r'^about/$', amazon.AboutPageView.as_view(), name='about'),
    url(r'^home/$', login_required(amazon.HomePageView.as_view()), name='home'),
    url(r'^searches/$',
        login_required(amazon.SearchListView.as_view()),
        name='search-list'),
    url(r'^search/(?P<pk>[-\w]+)/$',
        login_required(amazon.SearchDetailView.as_view()),
        name='search-detail'),
    url(r'^favorites/$',
        login_required(amazon.FavoriteProductsListView.as_view()),
        name='favorite-products'),
    url(r'^saved-searches/$',
        login_required(amazon.SavedSearchesListView.as_view()),
        name='saved-searches'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

