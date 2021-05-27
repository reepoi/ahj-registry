from operator import attrgetter

from django.apps import apps
from django.contrib import admin
from django.contrib.gis import admin as geo_admin

from .actions import user_reset_password, user_generate_api_token

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
    """
    Custom admin site for the AHJ Registry. Changes include:
    site_header, site_title, index_title, categorized models.
    """
    site_header = 'AHJ Registry Admin Dashboard'
    site_title = 'AHJ Registry Admin Dashboard'
    index_title = 'AHJ Registry Admin Dashboard'

    def get_custom_app_dict(self, name, app_label, app_url, has_module_perms, models):
        """
        Helper to categorize models under a fake application label.
        """
        return {
            'name': name,
            'app_label': app_label,
            'app_url': app_url,
            'has_module_perms': has_module_perms,
            'models': models
        }

    def get_app_list(self, request):
        """
        Creates a list of dict to tell the admin site index page
        how to group the models of the installed apps. This was overridden
        to create custom groupings for the models of the ahj_app.
        """
        app_list = super().get_app_list(request)
        ahj_app = [app for app in app_list if app['app_label'] == 'ahj_app']
        if len(ahj_app) == 0:
            """
            Sometimes the super class' get_app_list returns an empty list.
            """
            return app_list
        ahj_app = ahj_app[0]

        """
        Puts the ahj_app models into these categories: User Data, AHJ Data, Polygon Data.
        """
        user_data_models = [model for model in ahj_app['models'] if model['object_name'] in USER_DATA_MODELS]
        ahj_data_models = [model for model in ahj_app['models'] if model['object_name'] not in USER_DATA_MODELS.union(POLYGON_DATA_MODELS)]
        polygon_data_models = [model for model in ahj_app['models'] if model['object_name'] in POLYGON_DATA_MODELS]
        new_app_list = []
        new_app_list.append(self.get_custom_app_dict('User Data', 'user_data', ahj_app['app_url'], ahj_app['has_module_perms'], user_data_models))
        new_app_list.append(self.get_custom_app_dict('AHJ Data', 'ahj_data', ahj_app['app_url'], ahj_app['has_module_perms'], ahj_data_models))
        new_app_list.append(self.get_custom_app_dict('Polygon Data', 'polygon_data', ahj_app['app_url'], ahj_app['has_module_perms'], polygon_data_models))
        return new_app_list


"""
Tell Django to use our custom admin site.
"""
admin.site = AHJRegistryAdminSite()


def get_default_model_admin_class(model, geo=False):
    """
    For a given model, returns a default admin model with:
    - A search bar that searches all CharField fields of the model.
    - A table to display the primary key and all CharField fields of the model.
    - Turned-off dropdown selection of related models in the model detail view.
    If geo=True, then creates a OSMGeoAdmin for a nicer view of the GIS features.
    """
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
    """
    Returns a function to be added to a class definition (an admin model) that takes
    an object and returns an attribute value (possibly nested). If the attribute is
    callable, it returns the value the callable attribute returns.
    """
    def temp_func(self, obj):
        value = attrgetter(dotted_path)(obj)
        if callable(value):
            return value()
        return value
    temp_func.__name__ = name
    temp_func.admin_order_field = admin_order_field
    temp_func.short_description = short_description
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


def get_action_info_dict(name, function):
    return {
        'name': name,
        'function': function
    }


user_admin_model = model_admin_dict['User']['admin_model']
admin_actions_to_add = []
admin_actions_to_add.append(get_action_info_dict('user_reset_password', user_reset_password))
admin_actions_to_add.append(get_action_info_dict('user_generate_api_token', user_generate_api_token))
for action in admin_actions_to_add:
    setattr(user_admin_model, action['name'], action['function'])
    user_admin_model.actions.append(action['name'])


for v in model_admin_dict.values():
    admin.site.register(v['model'], v['admin_model'])
