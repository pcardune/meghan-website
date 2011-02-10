import simplejson
import logging
from django.conf import settings
from google.appengine.api.urlfetch import fetch, DownloadError

ETSY_API_KEY = 'jg9hpfpv9cjq7xg6zrc5qa6w'
ETSY_SERVER_ROOT = 'http://beta-api.etsy.com/v1'

def _build_url(path, query={}):
    query['api_key'] = ETSY_API_KEY
    query_string = "&".join(["%s=%s" % (key, val) for key, val in query.items()])
    return "%s%s?%s" % (ETSY_SERVER_ROOT, path, query_string)

def call(path, query={}, single=False):
    url = _build_url(path, query=query)
    logging.info("Fetching url: %s", url)
    try:
        response = fetch(url)
    except DownloadError, e:
        logging.error("Failed to fetch %s:%s", url, e)
        return False
    if 200 <= response.status_code < 300:
        logging.info("Retrieved %s bytes", len(response.content))
        data = simplejson.loads(response.content)['results']
        if single:
            return data[0]
        return data
    logging.warn("Failed to fetch %s.  Status code: %s\n%s",
                url, response.status_code, response.content)
    return False

def ping():
    if settings.OFFLINE:
        return None
    return call('/server/ping.json', single=True)

def get_user_details(user_id, detail_level='high'):
    if settings.OFFLINE:
        return None
    return call('/users/%s.json' % user_id,
            query={'detail_level':detail_level},
            single=True)

