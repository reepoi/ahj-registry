from django.apps import apps
from django.contrib import admin


for model in apps.all_models['ahj_app'].values():
    admin.site.register(model)
