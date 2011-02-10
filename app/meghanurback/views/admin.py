from meghanurback.forms import DeliciousSettingsForm
from meghanurback.models import DeliciousSettings
from meghanurback.views.utils import Handler
from meghanurback import delicious, forms, models

class DeliciousSettingsHandler(Handler):

    template = 'admin/delicious.html'
    admin_required = True

    def update(self):
        settings = DeliciousSettings.get()
        form = DeliciousSettingsForm(instance=settings)
        if self.request.method == 'POST':
            if self.request.POST.get("action") == "save":
                form = DeliciousSettingsForm(data=self.request.POST,
                                             instance=settings)
                if form.is_valid():
                    form.save()
            else:
                delicious.posts_all(refresh=True)
        self.context.update(locals())


class NewsAdminHandler(Handler):
    template = 'admin-news.html'
    admin_required = True

    def update(self):
        if self.request.method == "GET":
            form = forms.NewsItemForm()
        elif self.request.method == "POST":
            form = forms.NewsItemForm(data=self.request.POST)
            if form.is_valid():
                news_item = form.create()
                forms.NewsItemForm()
        news_items = models.NewsItem.all().fetch(100)
        self.context.update(locals())
