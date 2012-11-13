from django.views.generic.simple import direct_to_template
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.conf import settings
import random, json
import adlib
import models
import util
import os

def help(request, pagename='about'):
    return render(request, 'help/%s.html'%pagename, {'pagename': pagename})    

def tagexports(request):
    tpath = os.path.join(settings.PROJECT_ROOT, 'templates', 'help')
    exports = [x for x in os.listdir(tpath) if x.startswith('tagexport_')]
    filename = request.GET.get('filename')
    if filename:
        tag_map = json.loads(open(os.path.join(tpath, filename)).read())
    else:
        tag_map = None
    return render(request, 'help/tagexport.html', {'exports': exports, 'tag_map': tag_map})

def home(request):
    if request.user.is_anonymous():
        return render(request, 'index.html', 
                              {'pagename': 'home'
                              })

    return render(request, 'home.html', 
                              {'pagename': 'home',
                               'series': models.Serie.objects.all()
                              })

def registerloginmethod_helper(request, template, username=u'', password=u'', msg=None):
    return direct_to_template(request, template, 
                {'schools': models.School.objects.all(),
                 'msg': msg,
                 'username': username,
                 'password': password,
                })

def registermethod(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')        

        # Create the user, and set the school in it's profile
        kusername = [x for x in username.lower() if x in 'abcdefghijklmnopqrstuvwxyz']
        kusername = ''.join(kusername)[:30]
        try:
            u = models.User.objects.get(username=kusername)
            return direct_to_template(request, 'register.html', 
                {'schools': models.School.objects.all(),
                 'msg': u'De gebruiker met email: %s bestaat reeds' % username,
                })
        except models.User.DoesNotExist:
            u, created = models.User.objects.get_or_create(username=kusername, 
                                                      email=username)
            u.set_password(password)
            u.save()
        school = request.POST.get('school')
        if school:
            school = models.School.objects.get(pk=school)        
            u_profile = u.get_profile()
            u_profile.school = school
            u_profile.save()

        user = authenticate(username=kusername, password=password)
        login(request, user)
        return HttpResponseRedirect('/')
    return direct_to_template(request, 'register.html', 
                {'schools': models.School.objects.all()})

def loginmethod(request):
    username = password = msg = None
    if request.method == 'POST':
        # do the actual login
        username = request.POST.get('username')
        password = request.POST.get('password')
        next = request.POST.get('next', '/')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(next)
            else:
                # Return a 'disabled account' error message
                msg = u'Deze user is op non-actief gezet en kan dus niet inloggen'
        else:
            # Return an 'invalid login' error message.
            msg = u'De gebruikersnaam of wachtwoord klopt niet'

    return registerloginmethod_helper(request, 'login.html', username, password, msg)

def logoutmethod(request):
    logout(request)
    return HttpResponseRedirect('/')

def adlibpreview(request):
    search = request.GET.get('search', 'all')
    c = adlib.Server('http://amdata.adlibsoft.com/wwwopac.ashx')
    result = []
    for obj in c.search(database='AMcollect', search=search)[:99]:
        util.update_pic_url(obj)
        if 'picref' in obj:
            result.append(obj)

    return direct_to_template(request, 'adlibsearch.html',
                              {'result': result[:20],
                               'pagename': 'makeseries',
                               'search': search,
                               'count': len(result)
                              })

@login_required
def doseries(request, serie_pk):
    serie = models.Serie.objects.get(pk=serie_pk)
    vraag = random.choice(serie.vragen.all())
    obj = random.choice(serie.items.all()).obj
    util.update_pic_url(obj)
    antwoorden = request.user.antwoorden.filter(serievraag__serie=serie)
    aantal_deelnemers = models.User.objects.count()
    aantal_antwoorden = models.Antwoord.objects.count()
    gem_antwoorden = aantal_antwoorden / aantal_deelnemers

    return direct_to_template(request, 'doseries.html',
                              {'serie': serie,
                               'serievraag': vraag,
                               'vraag': vraag.vraag,
                               'antwoorden': antwoorden,
                               'pagename': 'home',
                               'obj': obj,
                               'aantal_deelnemers': aantal_deelnemers,
                               'aantal_antwoorden': aantal_antwoorden,
                               'gem_antwoorden': gem_antwoorden,
                              })

@require_POST
@login_required
def save_answer(request):
    serievraag_pk = request.POST.get('serievraag_pk')
    obj_id = request.POST.get('obj_id')
    data = request.POST.get('data', u'')
    a = models.Antwoord.objects.create(serievraag_id=int(serievraag_pk),
                                   user=request.user,
                                   obj=obj_id,
                                   value=data                                   
                                   )
    return HttpResponse('OK %s'%a.pk, mimetype='text/plain') 

@login_required
def makeseries(request):
    if request.method == 'POST':
        naam = request.POST.get('naam')
        adlibsearch = request.POST.get('adlibsearch')
        s = models.Serie.objects.create(naam=naam, adlibsearch=adlibsearch)
        for v in request.POST.getlist('vraag'):
            vraag = models.Vraag.objects.get(pk=int(v))
            models.SerieVraag.objects.create(serie=s, vraag=vraag)
        c = adlib.Server('http://amdata.adlibsoft.com/wwwopac.ashx')
        objs = c.search(database='AMcollect', search=adlibsearch)
        for obj in objs[:200]:
            util.update_pic_url(obj)
            if 'picref' in obj:
                obj_id = obj.get('priref', [None])[0]
                if obj_id:
                    models.SerieItem.objects.create(serie=s, objdata=json.dumps(obj), objid=obj_id)

        return HttpResponse('OK %s'%s.pk, mimetype='text/plain')

    return direct_to_template(request, 'makeseries.html', 
                              {'vragen': models.Vraag.objects.all(),
                               'pagename': 'makeseries'
                              })

@login_required
def makepybossa(request):
    # Create a new application if it does not exist

    # Make a new template, and update application

    # Create a new task for each priref object
    return HttpResponse('OK', mimetype='text/plain')