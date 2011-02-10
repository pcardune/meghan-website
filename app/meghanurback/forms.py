from google.appengine.ext.db import djangoforms
from django import newforms
from meghanurback import models

class NavigationItemForm(newforms.Form):
    navigation_title = newforms.CharField()
    navigation_order = newforms.IntegerField()
    navigation_url = newforms.CharField()
    enabled = newforms.BooleanField(required=False)
    navigation_align_left = newforms.BooleanField(required=False)

class PhotosetForm(NavigationItemForm):
    photoset_id = newforms.CharField()
    about_text = newforms.CharField(widget=newforms.Textarea, required=False)

class FileUploadForm(NavigationItemForm):
    pass

class NewsItemForm(newforms.Form):
    title = newforms.CharField()
    description = newforms.CharField(widget=newforms.Textarea, required=False)
    location = newforms.CharField(required=False)
    url = newforms.CharField()
    start_date = newforms.DateField()
    end_date = newforms.DateField()

    def create(self):
        cd = self.clean_data
        news_item = models.NewsItem(**cd)
        news_item.put()
        return news_item

class PageAddForm(NavigationItemForm):
    pass

class DeliciousSettingsForm(djangoforms.ModelForm):
    class Meta:
        model = models.DeliciousSettings
        exclue = ('class,')


class FlickrSettingsForm(djangoforms.ModelForm):
    class Meta:
        model = models.FlickrSettings

class SettingsForm(djangoforms.ModelForm):
    class Meta:
        model = models.Settings


class PageForm(NavigationItemForm):
    content = newforms.CharField(widget=newforms.Textarea, required=False)
