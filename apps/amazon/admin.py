from django.contrib import admin
from apps.amazon import models


admin.site.register(models.Product)


class SearchAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('name', 'last_updated_at', )
    list_filter = ('last_updated_at', )
admin.site.register(models.Search, SearchAdmin)


class BrowseNodeAdmin(admin.ModelAdmin):
    search_fields = ('full_name', )
    list_display = ('full_name', 'follow', )
    list_editable = ('follow', )
admin.site.register(models.BrowseNode, BrowseNodeAdmin)


class SavedSearchAdmin(admin.ModelAdmin):
    search_fields = ('name', 'user__email', )
    list_display = ('user', 'name', 'param_string', )
admin.site.register(models.SavedSearch, SavedSearchAdmin)


class FavoriteProductAdmin(admin.ModelAdmin):
    search_fields = ('product__name', 'user__email', )
    list_display = ('user', 'product', )
    readonly_fields = ('product', )
admin.site.register(models.FavoriteProduct, FavoriteProductAdmin)
