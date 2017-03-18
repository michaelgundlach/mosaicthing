from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import images
from getImageInfo import getImageInfo

from StringIO import StringIO

import logging
import time
import picasafeed
import random
import cachedfetch

from Models import *


class Mosaic(webapp.RequestHandler):
    def get(self):
        self.redirect('/')

    def post(self):
        req = self.request
        errorUrl = '/?error=true'

        # is targetUrl a valid image?
        leadImgFetch = urlfetch.fetch(req.get("targetUrl"))
        if leadImgFetch.status_code != 200:
            self.redirect(errorUrl)
            return

        try:
            # verify it's an image, and convert to PNG
            lead_img = images.crop(leadImgFetch.content,
                    0.0, 0.0, 1.0, 1.0, output_encoding=images.PNG)
        except: # not an image
            self.redirect(errorUrl)
            return

        # is feedUrl a valid feed?
        feedUrlData = urlfetch.fetch(req.get("feedUrl"))
        if feedUrlData.status_code != 200:
            self.redirect(errorUrl)
            return

        # save the job to the database
        try:
            feedfile = StringIO(feedUrlData.content)
            feedimages = picasafeed.getthumbnailsfromfile(feedfile)
            assert len(feedimages) > 0
        except:
            self.redirect(errorUrl)
            return

        content_type, width, height = getImageInfo(lead_img)

        job = Job(user=users.get_current_user(),
                  lead_img_url=db.Link(req.get("targetUrl")),
                  lead_img=lead_img,
                  lead_img_size=[width, height],
                  feed_urls=feedimages,
                  uncreated_thumb_indexes=range(len(feedimages)))

        job.put()

        self.redirect('/mosaic/%s/build' % job.key().id())


class Build(webapp.RequestHandler):
    def get(self, jobid):
        jobid = int(jobid)

        job = Job.get_by_id(jobid)
        if not job:
            self.error(404)
            return

        data = {
            'jobid': jobid,
            'orig_img_url': job.lead_img_url,
            'thumbs': ['/mosaic/%s/thumb/%d' % (jobid, x)
                       for x in range(len(job.feed_urls))],
            'thumbcount': len(job.feed_urls),
            'lead_width': job.lead_img_size[0],
            'lead_height': job.lead_img_size[1]
        }

        self.response.out.write(template.render('build.html', data))

class Clean(webapp.RequestHandler):
    def get(self):
        if random.random() < .5:
            self.response.out.write(len(list(Thumbnail.all())))
            return

        while True:
            x=Thumbnail.all().get()
            db.delete(x)

class SetWidths(webapp.RequestHandler):
    def get(self, jobid):
        """Receives a grid width and lead image width, and returns a JSON
        object containing lead image and tile dimensions and grid
        width and height.
        """

        jobid = int(jobid)
        job = Job.get_by_id(jobid)
        if not job:
            self.error(404)
            return

        response = {}

        # let the user have the number of tiles across that they desire.
        tiles_x = int(self.request.get('tiles_x'))

        # try to let them have their desired lead width.
        lead_width = int(self.request.get('lead_width'))

        # but their tiles may not fit exactly into their lead now...
        # how many wide can we fit horizontally, maybe having to trim a 
        # few pixels off the right edge of the lead?
        tile_width = int(float(lead_width) / tiles_x)

        # ok, so now we know how wide the lead can actually be.
        lead_width = tile_width * tiles_x

        # and we're sticking with square tiles, by golly.
        tile_height = tile_width

        # how tall will the lead be based on its aspect ratio and new width?
        lead_ratio = float(job.lead_img_size[1]) / job.lead_img_size[0]
        lead_height = int(lead_ratio * lead_width)

        # how many tiles can we fit on the lead vertically, perhaps
        # leaving a few pixels at the bottom of the lead untended?
        tiles_y = int(float(lead_height) / tile_height)

        response=dict(tiles_x=tiles_x, tiles_y=tiles_y,
                lead_width=lead_width, lead_height=lead_height,
                tile_width=tile_width, tile_height=tile_height)

        self.response.out.write(str(response)) # looks just like JSON

class ColorThumbs(webapp.RequestHandler):
    def get(self, jobid):
        """Record the average color for each thumbnail into job.thumb_colors.
        """
        jobid = int(jobid)
        job = Job.get_by_id(jobid)
        if not job:
            self.error(404)
            return

        job.thumb_colors = repr([ CachedThumb(url).color
                                  for url in job.feed_urls ])
        job.put()

        self.response.out.write("OK")

class Prepare(webapp.RequestHandler):
    def get(self, jobid):
        secs_to_run = 0.5
        start = time.time()

        jobid = int(jobid)
        job = Job.get_by_id(jobid)
        if not job:
            self.error(404)
            return

        key = "unprepared_thumbs_%d" % jobid
        uncached_thumbids = memcache.get(key)

        if uncached_thumbids == "finished":
            self.response.out.write("100")
            return

        if not uncached_thumbids:
            uncached_thumbids = range(len(job.feed_urls))
            memcache.set(key, uncached_thumbids, time=CACHE_TIME)

        while uncached_thumbids and time.time() - start < secs_to_run:
            thumbid = uncached_thumbids.pop()
            CachedThumb(job.feed_urls[thumbid]) # loads url into cache

        if not uncached_thumbids:
            memcache.set(key, "finished", time=CACHE_TIME)
            self.response.out.write("100")
            return

        memcache.set(key, uncached_thumbids, time=CACHE_TIME) # for next guy

        # return the percent we're complete
        thumbs_left = len(uncached_thumbids)
        total_thumbs = len(job.feed_urls)
        import logging
        percent_done = int(float(thumbs_left) / total_thumbs * 100)
        logging.info("%d, %d, %d" % (thumbs_left, total_thumbs, percent_done))
        percent_left = 100 - percent_done

        self.response.out.write(str(percent_left))
