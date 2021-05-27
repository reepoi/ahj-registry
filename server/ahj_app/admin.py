from operator import attrgetter

from django.apps import apps
from django.contrib import admin
from django.contrib.gis import admin as geo_admin


USER_DATA_MODELS = {
    'AHJUserMaintains',
    'APIToken',
    'Comment',
    'Edit',
    'User',
    'WebpageToken'
}

POLYGON_DATA_MODELS = {
    'StatePolygon',
    'CountyPolygon',
    'CityPolygon',
    'CountySubdivisionPolygon',
    'StateTemp',
    'CountyTemp',
    'CityTemp',
    'CousubTemp'
}


class AHJRegistryAdminSite(admin.AdminSite):
    site_header = 'AHJ Registry Admin Dashboard'
    site_title = 'AHJ Registry Admin Dashboard'
    index_title = 'AHJ Registry Admin Dashboard'

    def get_custom_app_dict(self, name, app_label, app_url, has_module_perms, models):
        return {
            'name': name,
            'app_label': app_label,
            'app_url': app_url,
            'has_module_perms': has_module_perms,
            'models': models
        }

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        ahj_app = [app for app in app_list if app['app_label'] == 'ahj_app'][0]
        user_data_models = [model for model in ahj_app['models'] if model['object_name'] in USER_DATA_MODELS]
        ahj_data_models = [model for model in ahj_app['models'] if model['object_name'] not in USER_DATA_MODELS.union(POLYGON_DATA_MODELS)]
        polygon_data_models = [model for model in ahj_app['models'] if model['object_name'] in POLYGON_DATA_MODELS]
        new_app_list = []
        new_app_list.append(self.get_custom_app_dict('User Data', 'user_data', ahj_app['app_url'], ahj_app['has_module_perms'], user_data_models))
        new_app_list.append(self.get_custom_app_dict('AHJ Data', 'ahj_data', ahj_app['app_url'], ahj_app['has_module_perms'], ahj_data_models))
        new_app_list.append(self.get_custom_app_dict('Polygon Data', 'polygon_data', ahj_app['app_url'], ahj_app['has_module_perms'], polygon_data_models))
        return new_app_list


admin.site = AHJRegistryAdminSite()


def get_default_model_admin_class(model, geo=False):
    model_fields = [field for field in model._meta.get_fields()]
    if geo:
        class DefaultPolygonAdmin(geo_admin.OSMGeoAdmin):
            search_fields = [field.name for field in model_fields if field.__class__.__name__ == 'CharField']
            list_display = [model._meta.pk.name] + search_fields
            raw_id_fields = [field.name for field in model_fields
                             if field.__class__.__name__ == 'ForeignKey' or field.__class__.__name__ == 'OneToOneField']
        return DefaultPolygonAdmin
    else:
        class DefaultAdmin(admin.ModelAdmin):
            search_fields = [field.name for field in model_fields if field.__class__.__name__ == 'CharField']
            list_display = [model._meta.pk.name] + search_fields
            raw_id_fields = [field.name for field in model_fields
                             if field.__class__.__name__ == 'ForeignKey' or field.__class__.__name__ == 'OneToOneField']
        return DefaultAdmin


model_admin_dict = {}
for model in apps.all_models['ahj_app'].values():
    if 'Polygon' in model.__name__:
        admin_model = get_default_model_admin_class(model, geo=True)
    else:
        admin_model = get_default_model_admin_class(model)
    model_admin_dict[model.__name__] = {
        'model': model,
        'admin_model': admin_model
    }


def create_admin_get_attr_function(name, dotted_path, admin_order_field, short_description):
    def temp_func(self, obj):
        value = attrgetter(dotted_path)(obj)
        if callable(value):
            return value()
        return value
    temp_func.__name__ = name
    setattr(temp_func, 'admin_order_field', admin_order_field)
    setattr(temp_func, 'short_description', short_description)
    return temp_func


def get_attr_info_dict(name, dotted_path, admin_order_field, short_description):
    return {
        'name': name,
        'dotted_path': dotted_path,
        'admin_order_field': admin_order_field,
        'short_description': short_description
    }


api_token_admin_model = model_admin_dict['APIToken']['admin_model']
admin_attrs_to_add = []
model_attrs_to_add = ['created']
admin_attrs_to_add.append(get_attr_info_dict('get_user_email', 'user.Email', 'email', 'Email'))
admin_attrs_to_add.append(get_attr_info_dict('get_user_company_affiliation', 'user.CompanyAffiliation', 'company_affiliation', 'Company Affiliation'))
admin_attrs_to_add.append(get_attr_info_dict('get_user_is_ahj_official', 'user.is_ahj_official', 'ahj_official', 'Is AHJ Official'))
for attr in admin_attrs_to_add:
    setattr(api_token_admin_model, attr['name'],
            create_admin_get_attr_function(attr['name'], attr['dotted_path'], attr['admin_order_field'], attr['short_description']))
    api_token_admin_model.list_display.append(attr['name'])
for field in model_attrs_to_add:
    api_token_admin_model.list_display.append(field)

for v in model_admin_dict.values():
    admin.site.register(v['model'], v['admin_model'])
