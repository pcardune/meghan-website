"""Access to delicious with caching layer."""
import logging
import simplejson
from google.appengine.api import memcache
from meghanurback import models
from google.appengine.api.urlfetch import fetch

def _get_api():
    settings = models.DeliciousSettings.get()
    return DeliciousAPI(settings.username, settings.password)

def posts_all(refresh=False):
    data = memcache.get("delicious_posts_all")
    if data is None or refresh:
        settings = models.DeliciousSettings.get()
        raw = fetch('http://feeds.delicious.com/v2/json/%s' % settings.username).content
        logging.info("got raw data:%s", raw)
        data = simplejson.loads(raw)
        data = [{'url':item['u'], 'description':item['d'], 'tags':item['t']} for item in data]
        # data = _get_api().posts_all()
        memcache.set("delicious_posts_all",data)
    return data
