# Export tags to a Adlib Database

from django.core.management.base import BaseCommand
from AHMTG import util
    
class Command(BaseCommand):
    help = "Write all un-exported answers to the AdLib database"
    
    def handle(self, *args, **options):
        tag_map = util.tag_export()
        if tag_map:
            print 'Wrote %s tags' % len(tag_map)
