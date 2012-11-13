import re
import os
import json
import time
from datetime import datetime
import models
import adlib
from django.conf import settings

# The AdLib objects returned in the JSON dicts have fieldnames with periods in them
# This makes accessing them from Django templates tricky, requiring at least a templatetag
def update_pic_url(adlib_dict_obj):
    for x in adlib_dict_obj.get('reproduction', []):
        xx = x.get('reproduction.identifier_URL')
        xxx = xx[0].lower()
        if xxx.endswith('.jpg'):
            # Make this a CONSTANT.
            xxxx = xxx[26:]
            adlib_dict_obj['picref'] = 'http://am.adlibhosting.com/wwwopacximages/wwwopac.ashx?command=getcontent&server=images&value=%s&height=450&width=450' % xxxx
            break

def tag_export():
    # get all antwoorden not exported yet
    # chop into words
    # for each word, make a list of object ids (priref for Adlib)
    tag_map = {}
    # Collect the stopwords
    stopwords = [w.word for w in models.Stopword.objects.all()]
    for a in models.Antwoord.objects.filter(exported=None):
        if a.value:
            for aa in re.split(',| ', a.value):
                if not aa or (aa in stopwords):
                    continue
                tag_map.setdefault(aa, []).append(a.obj)
        a.exported = datetime.now()
        a.save()

    c = adlib.Server('http://am.adlibhosting.com/wwwopacx/wwwopac.ashx')
    c.debug = settings.DEBUG
    for k, v in tag_map.items():
        c.search(database='tagging', search='tag=%s' % k.encode('utf8'))
        if len(c) < 1:
            c.insertrecord('tagging', {'tag': k})
        priref = c[0]['priref']
        # and now for each priref linked to this tag
        for vv in v:
            now = datetime.now()
            c.updaterecord('tagging', 
                           {'priref': priref,
                            'linked.priref': vv,
                            'linked.date': '{:%Y-%m-%d}'.format(now),
                            'linked.time': '{:%H:%M:%S}'.format(now),
                           })

    return tag_map

def write_tags_to_template(tag_map):
    nonce = str(hash(json.dumps(tag_map)))
    output = os.path.join(settings.PROJECT_ROOT, 'templates', 'help', 'tagexport_'+nonce+'.json')
    data = {'data': tag_map, 
            'meta': {'timestamp': time.ctime()}}
    open(output, 'w').write(json.dumps(data))
    return tag_map
