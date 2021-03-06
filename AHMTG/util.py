import traceback
from datetime import datetime
from django.utils.timezone import utc
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
    for a in models.Antwoord.objects.filter(exported=None):
        if a.value:
            for aa in a.tags():
                tag_map.setdefault(aa, []).append(a)

    c = adlib.Server('http://am.adlibhosting.com/wwwopacx/wwwopac.ashx')
    c.debug = settings.DEBUG
    for k, v in tag_map.items():
        c.search(database='tagging', search='tag=%s' % k.encode('utf8'))
        if len(c) < 1:
            new_item = c.insertrecord('tagging', {'tag': k})
            priref = new_item['priref']
        else:
            priref = c[0]['priref'][0]
        # and now for each priref linked to this tag
        for vv in v:
            try:
                now = datetime.utcnow().replace(tzinfo=utc)
                c.updaterecord('tagging', 
                               {'priref': priref,
                                'linked.database': 'ChoiceCollect',
                                'linked.priref': vv.obj,
                                'linked.date': '{:%Y-%m-%d}'.format(now),
                                'linked.time': '{:%H:%M:%S}'.format(now),
                               })
            except:
                traceback.print_exc()
            finally:
                vv.exported = now
                vv.save()

    return tag_map
