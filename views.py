from wsgiref.handlers import CGIHandler
from google.appengine.ext import webapp

import Index
import NotFound
import ImageRequests
import Mosaic

def real_main():
  application = webapp.WSGIApplication([
      ('/', Index.Index),
      ('/index.html', Index.Index),

      ('/mosaic', Mosaic.Mosaic),
      ('/mosaic/(\d+)/build', Mosaic.Build),
      ('/mosaic/(\d+)/prepare', Mosaic.Prepare),
      ('/mosaic/(\d+)/colorthumbs', Mosaic.ColorThumbs),
      ('/mosaic/(\d+)/setwidths', Mosaic.SetWidths),
      ('/mosaic/diediedie', Mosaic.Clean),

      ('/mosaic/(\d+)/thumb/(\d+)', ImageRequests.Thumb),
      ('/mosaic/(\d+)/tile', ImageRequests.Tile),
      ('/mosaic/(\d+)/complete', ImageRequests.Complete),
      ('/mosaic/(\d+)/save', ImageRequests.Save),

      ('/.*', NotFound.NotFound)
      ],

      debug=True)

  CGIHandler().run(application)

def profile_main():
    # This is the main function for profiling 
    # We've renamed our original main() above to real_main()
    import cProfile, pstats
    prof = cProfile.Profile()
    prof = prof.runctx("real_main()", globals(), locals())
    print "<pre>"
    stats = pstats.Stats(prof)
    stats.sort_stats("cumulative")  # Or 'time'
    stats.print_stats(80)  # 80 = how many to print
    # The rest is optional.
    # stats.print_callees()
    # stats.print_callers()
    print "</pre>"

import logging
def profile2_main():
 # This is the main function for profiling 
 # We've renamed our original main() above to real_main()
 import cProfile, pstats, StringIO
 prof = cProfile.Profile()
 prof = prof.runctx("real_main()", globals(), locals())
 stream = StringIO.StringIO()
 stats = pstats.Stats(prof, stream=stream)
 stats.sort_stats("time")  # Or cumulative
 stats.print_stats(80)  # 80 = how many to print
 # The rest is optional.
 # stats.print_callees()
 # stats.print_callers()
 logging.info("Profile data:\n%s", stream.getvalue())

main = real_main

if __name__ == "__main__":
    main()
