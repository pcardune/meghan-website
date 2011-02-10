import logging
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

from django.http import Http404

from rwproperty import getproperty, setproperty
from meghanurback import flickr


class NavigationItem(db.Model):
    title = db.StringProperty()
    order = db.IntegerProperty()
    url = db.StringProperty()
    enabled = db.BooleanProperty()
    align_left = db.BooleanProperty()

    def __repr__(self):
        return "<%s url=%r key=%s>" % (self.__class__.__name__,
                                       self.url,
                                       self.key())

class NavigationDelegator(object):

    @getproperty
    def navigation_title(self):
        return self.navigation_item.title
    @setproperty
    def navigation_title(self, val):
        self.navigation_item.title = val

    @getproperty
    def navigation_order(self):
        return self.navigation_item.order
    @setproperty
    def navigation_order(self, val):
        self.navigation_item.order = val

    @getproperty
    def navigation_url(self):
        return self.navigation_item.url
    @setproperty
    def navigation_url(self, val):
        self.navigation_item.url = val

    @getproperty
    def navigation_enabled(self):
        return self.navigation_item.enabled
    @setproperty
    def navigation_enabled(self, val):
        self.navigation_item.enabled = val

    @getproperty
    def navigation_align_left(self):
        return self.navigation_item.align_left
    @setproperty
    def navigation_align_left(self, val):
        self.navigation_item.align_left = val


    @getproperty
    def enabled(self):
        return self.navigation_item.enabled
    @setproperty
    def enabled(self, val):
        self.navigation_item.enabled = val

    @property
    def absolute_url(self):
        return '/%s/%s' % (self.navigation_prefix, self.navigation_url)

    @classmethod
    def from_nav(cls, navigation_url):
        logging.info("Getting nav item for url %r", navigation_url)
        nav_items = list(db.GqlQuery("SELECT * FROM NavigationItem WHERE url = :1", navigation_url.lower()))
        if len(nav_items) == 0:
            logging.warn("Did not find navigation item with url %s", navigation_url.lower())
            raise Http404()
        for nav_item in nav_items:
            logging.info("Found nav item %r", nav_item)
            file_uploads = list(db.GqlQuery("SELECT * FROM %s WHERE navigation_item = :1" % cls.__name__, nav_item))
            if len(file_uploads) == 0:
                logging.warn("Did not find %s object with navigation item %s", cls.__name__, nav_item)
            else:
                return file_uploads[0]
        raise Http404()


class Photoset(db.Model):
    navigation_prefix = 'gallery'
    photoset_id = db.StringProperty()
    navigation_title = db.StringProperty()
    navigation_order = db.IntegerProperty()
    navigation_url = db.StringProperty()
    enabled = db.BooleanProperty()
    about_text = db.TextProperty()
    navigation_align_left = db.BooleanProperty()

    @property
    def absolute_url(self):
        return '/%s/%s' % (self.navigation_prefix, self.navigation_url)

    def get_photos(self):
        return flickr.get_photoset(self.photoset_id)

    def get_thumbnail(self):
        return self.get_photos()[0]
        #return flickr.Photo(self._metadata)

    def __len__(self):
        return int(self._metadata['photos'])

    _cached_metadata = None
    @property
    def _metadata(self):
        if self._cached_metadata is None:
            self._cached_metadata = flickr.get_photoset_metadata(self.photoset_id)
        return self._cached_metadata

    def get_metadata(self):
        return self._metadata

    @property
    def description(self):
        return self.about_text or self._metadata['description']['_content']

    @property
    def title(self):
        return self._metadata['title']['_content']

    def __unicode__(self):
        return self.navigation_title


class FileUpload(db.Model, NavigationDelegator):
    navigation_prefix = 'file'
    navigation_item = db.ReferenceProperty(NavigationItem)
    filename = db.StringProperty()
    data = db.BlobProperty()
    content_type = db.StringProperty()

    def put(self):
        self.navigation_item.put()
        super(FileUpload, self).put()

    def __unicode__(self):
        return self.navigation_title

    def delete(self):
        self.navigation_item.delete()
        super(FileUpload, self).delete()


class Page(db.Model, NavigationDelegator):
    navigation_prefix = 'page'
    navigation_item = db.ReferenceProperty(NavigationItem)
    content = db.TextProperty()

    def put(self):
        self.navigation_item.put()
        super(Page, self).put()

    def __unicode__(self):
        return self.navigation_title

    def delete(self):
        self.navigation_item.delete()
        super(Page, self).delete()


class NewsItem(db.Model):
    title = db.StringProperty()
    description = db.TextProperty()
    location = db.StringProperty()
    url = db.LinkProperty()
    start_date = db.DateProperty()
    end_date = db.DateProperty()


class SingletonModel(polymodel.PolyModel):

    def put(self):
        if self.__class__.all().get() and not self.key():
            raise Exception("Can't have more than one Settings objects")
        return super(SingletonModel, self).put()

    @classmethod
    def get(cls):
        settings = cls.all().get()
        if not settings:
            settings = cls()
            settings.put()
        return settings


class DeliciousSettings(db.Model):
    """Settings for delicious integration"""
    username = db.StringProperty()
    tags = db.StringListProperty(default=None)
    enabled = db.BooleanProperty(default=False)

    def put(self):
        if self.__class__.all().get() and not self.key():
            raise Exception("Can't have more than one Settings objects")
        return super(DeliciousSettings, self).put()

    def __repr__(self):
        return "<%s username=%r tags=%r>" % (self.__class__.__name__,
                                             self.username,
                                             self.tags)

    @classmethod
    def get(cls):
        settings = cls.all().get()
        if not settings:
            settings = cls()
            settings.put()
        return settings


class FlickrSettings(SingletonModel):
    """Settings for the flickr service"""
    flickr_user_id = db.StringProperty()


class Settings(SingletonModel):
    """SiteWide settings"""
    site_description = db.TextProperty()
    site_keywords = db.TextProperty()

    @staticmethod
    def get_settings():
        return Settings.get()
