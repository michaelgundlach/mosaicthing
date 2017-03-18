from google.appengine.api import memcache
from google.appengine.api import urlfetch

POST = urlfetch.POST
GET = urlfetch.GET
PUT = urlfetch.PUT

def fetch(url, **kwargs):
    """Fetch using urlfetch, unless we've already successfully fetched
    from the given url using identical arguments.  Only support
    method=GET."""
    if 'method' in kwargs and kwargs['method'] != GET:
        raise Exception, 'Only GET is supported by CachedFetch.'

    key = 'cachedfetch_%s_%s' % (url, repr(kwargs))
    result = memcache.get(key)

    if not result:
        result = urlfetch.fetch(url, **kwargs)
        if result.status_code == 200:
            memcache.add(key, result, time=60*60) # don't cache failure

    return result
