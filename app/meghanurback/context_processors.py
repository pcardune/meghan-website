from django.conf import settings
from re import compile
from copy import copy
from google.appengine.api import users
from meghanurback import models

navigation_model = [
#    dict(title='Home', url='/', regex=compile(r'^$'), order=0),
    dict(title='Portfolio', url='/gallery/', regex=compile(r'^gallery/'), order=0),
    dict(title='Events', url='/events/', regex=compile(r'^events/$'), order=10),
#    dict(title='Bio', url='/bio/', regex=compile(r'^bio/$'), order=0),
#    dict(title='Stationery', css_class="etsy", url='http://meghanurback.etsy.com',
#         regex=compile(r'^etsy/$'), order=30),
]

def navigation(request):
    "A context processor that provides navigational state for the base template."

    request_url = request.path[1:]

    nav = []

    for item in navigation_model:
        nav_item = copy(item)
        nav_item['selected'] = item['regex'].match(request_url) is not None
        nav.append(nav_item)

    nav_models = list(models.FileUpload.all())+list(models.Page.all())
    for nav_model in nav_models:
        if not nav_model.navigation_enabled:
            continue
        nav_item = dict(title=nav_model.navigation_title,
                        order=nav_model.navigation_order,
                        url=nav_model.absolute_url)
        nav_item['selected'] = request_url.startswith(nav_item['url'][1:])
        nav.append(nav_item)

    del_settings = models.DeliciousSettings.get()
    if del_settings.enabled:
        nav.append(dict(title="Links",
                        order=20,
                        url="/links/",
                        selected=request_url.startswith("links/")))

    nav.sort(key=lambda n: n.get('order'))

    return {
        'NAVIGATION': nav,
        'SETTINGS': settings,
        'SITE_SETTINGS': models.Settings.get_settings(),
        'LOGIN':{'logout_url':users.create_logout_url('/'),
                 'is_admin':users.is_current_user_admin()}
    }
