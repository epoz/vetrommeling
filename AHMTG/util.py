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