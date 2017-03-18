from xml.dom import minidom
import urllib2
import os

__doc__ = """Functions for reading image urls out of picasa web feeds."""

def test():
    url='http://picasaweb.google.com/data/feed/base/user/gundlach/albumid/5159955729066625985?kind=photo&alt=rss&hl=en_US'
    nails=getthumbnailsfromurl(url)
    print nails

def getthumbnailsfromurl(feedurl):
    """Get a list of all thumbnail image urls from the given feed url."""
    return getthumbnailsfromfile(urllib2.urlopen(feedurl))

def getthumbnailsfromfile(feedfile):
    """Get a list of all thumbnail image urls from the given feed file."""

    xmldoc = minidom.parse(feedfile)
    elements = xmldoc.getElementsByTagName("media:thumbnail")

    # For each image basename, record all heights and their urls.
    imgorder = []
    imgdata = {}
    for x in elements:
        imgurl = x.getAttribute("url")
        imgname = os.path.split(imgurl)[1]
        imgheight = int(x.getAttribute("height"))
        if imgname not in imgorder:
            imgorder.append(imgname) # to remember order later
            imgdata[imgname] = {}    # maps height to url
        imgdata[imgname][imgheight] = imgurl

    # Return a list of one url per image: the smallest height available.
    result = []
    for imgname in imgorder:
        urls = imgdata[imgname]
        smallest_height = min(urls.keys()) # heights
        result.append(urls[smallest_height])

    return result
