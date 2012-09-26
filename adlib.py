# Python interface to the Adlib API
# http://api.adlibsoft.com/
# This file is a work in progress, implementing only what we need to support
# the needs of the VetRommelingh project to access data from the Amsterdam Historisch Museum
# Feel free to add features if you require items not yet supported.
# Contact: Etienne posthumus <eposthumus@gmail.com>

import urllib
import urllib2
import json
import sys

class OpenEndedSliceNotAllowedException(Exception):
    pass

class Server(object):
    def __init__(self, address):
        self.address = address
        self.data_obj = None

    def _do_action(self):        
        uri = self.address+'?'+urllib.urlencode(self.params)
        sys.stderr.write(uri+'\n')
        data = urllib2.urlopen(uri).read()
        sys.stderr.write(uri+'\n')
        try:
            obj = json.loads(data)
        except ValueError:
            return
        self.data_obj = obj[u'adlibJSON']
        for x in ('first_item', 'limit'):
            tmp = self.data_obj.get('diagnostic', {}).get(x)
            setattr(self, x, int(tmp))

    def __len__(self):
        if not self.data_obj:
            self._do_action()
        tmp = self.data_obj.get('diagnostic', {}).get('hits')
        return int(tmp)

    def __getattr__(self, name):
        if not self.data_obj:
            self._do_action()
        if name in ('first_item', 'limit'):
            tmp = self.data_obj.get('diagnostic', {}).get(name)
            return int(tmp)

    def __getitem__(self, key):
        if not isinstance(key, (int, long, slice)):
            raise TypeError('%s indices must be integers, not %s' % (
                self.__class__.__name__, key.__class__.__name__))

        def get_start_end(val):
            if isinstance(val, slice):
                start = val.start
                if not start:
                    start = 0
                end = val.stop
                if (end < 0) or (end is None):
                    raise OpenEndedSliceNotAllowedException()
                return start, end
            return val, val + 1
        start, end = get_start_end(key)
        if (end - start) < 1:
            return []
        self.params['limit'] = str(end-start)
        self.params['startfrom'] = str(start+1)

        if not self.data_obj:
            self._do_action()
        else:
            if start < (self.first_item-1):
                self._do_action()
            if end > (self.first_item-1+self.limit):
                self._do_action()
        # TODO: What is the limit to number of records returned by 
        # an AdLib server?
        if isinstance(key, slice):
            sstart = self.first_item - start -1
            send = sstart + (end-start)
            return self.data_obj.get('recordList').get('record')[sstart:send]
        else:
            return self.data_obj.get('recordList').get('record')[0]

    def search(self, database, search):
        self.data_obj = None

        self.params = {'output': 'json',
                  'database': database,
                  'search': search,
                  'startfrom': '1',
                  'limit': '100',
                }
        return self
