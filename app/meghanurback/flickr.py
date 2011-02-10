import logging
import re
import simplejson
import flickrapi
from django.conf import settings
from google.appengine.api.urlfetch import DownloadError

FLICKR_KEY = '492b04c740650375b72a075723eaf28a'
FLICKR_SECRET = '162c4a5d283b470b'

F = flickrapi.FlickrAPI(FLICKR_KEY, format='json', store_token=False, cache=True)

json_wrapper_regex = re.compile(r'^jsonFlickrApi\((.*)\)$')
def unwrap(responseText):
    match = json_wrapper_regex.match(responseText)
    if match:
        return match.groups()[0]
    return False

def get_user_id(username):
    try:
        return F.people_findByUsername(username=username)
    except flickrapi.FlickrError, e:
        logging.warn("Error with flickr: %s", e)
    return False

class Photo(object):
    def __init__(self, json):
        self.json = json

    def __photo_url_prefix(self):
        return u'http://farm%(farm)s.static.flickr.com/%(server)s/%(id)s_%(secret)s' % self.json

    @property
    def photo_url(self):
        return self.__photo_url_prefix()+'.jpg'

    @property
    def square_photo_url(self):
        return self.__photo_url_prefix()+'_s.jpg'

    @property
    def thumbnail_photo_url(self):
        return self.__photo_url_prefix()+'_t.jpg'

    @property
    def small_photo_url(self):
        return self.__photo_url_prefix()+'_m.jpg'

    medium_photo_url = photo_url

    @property
    def large_photo_url(self):
        return self.__photo_url_prefix()+'_b.jpg'

    @property
    def page_url(self):
        return 'http://www.flickr.com/photos/%(owner)s/%(id)s' % self.json

    def __unicode__(self):
        return self.small_photo_url

def get_photoset_list(user_id='36146893@N07'):
    if settings.OFFLINE:
        return []
    try:
        data = simplejson.loads(unwrap(F.photosets_getList(user_id=user_id)))
        logging.info("Got flickr data: %r", data)

        result = data.get('photosets', {}).get('photoset')
        for r in result:
            r['title'] = r.get('title',{}).get("_content", "")
        return result
    except flickrapi.FlickrError, e:
        logging.warn("Error getting photoset list from flickr: %s", e)
    except DownloadError, e:
        logging.warn("Download error while getting photoset list from flickr: %s", e)
    return []

def get_photoset_metadata(photoset_id='72157617324778431'):
    if settings.OFFLINE:
        return []
    try:
        data = simplejson.loads(unwrap(F.photosets_getInfo(photoset_id=photoset_id)))
        photoset_data = data.get('photoset',{})
        logging.info("Got metadata for photoset %s", photoset_id)
        return photoset_data
    except flickrapi.FlickrError, e:
        logging.warn("Error getting photoset metadata from flickr: %s", e)
    except DownloadError, e:
        logging.warn("Download error while getting photoset metadata from flickr: %s", e)
    return []

def get_photoset(photoset_id='72157617324778431'):
    if settings.OFFLINE:
        return []
    try:
        data = simplejson.loads(unwrap(F.photosets_getPhotos(photoset_id=photoset_id)))
        result = []
        photoset_data = data.get('photoset',{})
        for p in photoset_data.get('photo'):
            p['owner'] = photoset_data.get('owner')
            result.append(Photo(p))
        logging.info("Got %s photos from flickr photoset %s", len(result), photoset_id)
        return result
    except flickrapi.FlickrError, e:
        logging.warn("Error getting photoset from flickr: %s", e)
    except DownloadError, e:
        logging.warn("Download error while getting photoset from flickr: %s", e)
    return []

def get_public_photos(user_id='36146893@N07'):
    if settings.OFFLINE:
        return []
    try:
        data = simplejson.loads(unwrap(F.people_getPublicPhotos(user_id=user_id)))
        result = [Photo(p) for p in data.get('photos',{}).get('photo')]
        logging.info("Got %s photos from flickr for user %s", len(result), user_id)
        return result
    except flickrapi.FlickrError, e:
        logging.warn("Error getting public photos from flickr: %s", e)
    except DownloadError, e:
        logging.warn("Download error while getting public photos from flickr: %s", e)
    return []
