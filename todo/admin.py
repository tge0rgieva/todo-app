from django.contrib import admin
from .models import Todo


# To customize the admin panel
class TodoAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)


admin.site.register(Todo, TodoAdmin)