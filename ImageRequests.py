from google.appengine.ext import webapp

from NotFound import NotFound
from Models import *

import logging

class Thumb(webapp.RequestHandler):
    def get(self, jobid, thumbindex):
        jobid = int(jobid)
        thumbindex = int(thumbindex)

        job = Job.get_by_id(jobid)
        if not job or thumbindex not in range(len(job.feed_urls)):
            self.error(404)
            return

        self.response.headers['Content-type'] = 'image/png'
        thumb = CachedThumb(job.feed_urls[thumbindex])
        if not thumb.data:
            self.error(404)
            return

        self.response.out.write(thumb.data)

class Tile(webapp.RequestHandler):
    def get(self, jobid):
        """Return the tile data for slot (i,j) on the lead image, when
        sized lead_width by lead_height and divided into tiles_x by
        tiles_y tiles of tile_width by tile_height."""
        jobid=int(jobid)

        job = Job.get_by_id(jobid);
        if not job:
            self.error(404)
            return

        tiles_x = int(self.request.get("tiles_x"))
        tiles_y = int(self.request.get("tiles_y"))
        lead_width = int(self.request.get("lead_width"))
        lead_height = int(self.request.get("lead_height"))
        tile_width = int(self.request.get("tile_width"))
        tile_height = int(self.request.get("tile_height"))
        i = int(self.request.get("i"))
        j = int(self.request.get("j"))

        tile = CachedTile(job, tiles_x, tiles_y,
                tile_width, tile_height,
                lead_width, lead_height,
                i, j).data

        self.response.headers['Content-type'] = 'image/png'
        self.response.out.write(tile)

class Complete(webapp.RequestHandler):
    def get(self, mosaicid):
        self.response.out.write("Complete")

class Save(webapp.RequestHandler):
    def get(self, mosaicid):
        self.response.out.write("Save")
