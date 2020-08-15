from django.contrib import admin
from .models import Box

# Register your models here.

#for  modifying the default view of admin pannel
class BoxAdmin(admin.ModelAdmin):
    # a list of displayed columns name.
    list_display = ['id', 'length', 'breadth', 'height', 'area', 'volume', 'created_by']
    # define search columns list, then a search box will be added at the top of Department list page.
    search_fields = ['length', 'breadth', 'height', 'area', 'volume', 'created_by__username']


admin.site.register(Box,BoxAdmin)

