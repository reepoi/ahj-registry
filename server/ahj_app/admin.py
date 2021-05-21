from django.apps import apps
from django.contrib import admin

for model in apps.all_models['ahj_app'].values():
    model_fields = [field for field in model._meta.get_fields()]


    class AdminWithSearch(admin.ModelAdmin):
        search_fields = [field.name for field in model_fields if field.__class__.__name__ == 'CharField']
        list_display = search_fields
        raw_id_fields = [field.name for field in model_fields if field.__class__.__name__ == 'ForeignKey']

    print(AdminWithSearch.raw_id_fields)
    admin.site.register(model, AdminWithSearch)
