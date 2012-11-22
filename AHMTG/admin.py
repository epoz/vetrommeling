from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from models import *

class KeuzeInline(admin.TabularInline):
    model = Keuze
#class KeuzeAdmin(admin.ModelAdmin):
#    pass
#admin.site.register(Keuze, KeuzeAdmin)

class VraagAdmin(admin.ModelAdmin):
    inlines = [KeuzeInline]
admin.site.register(Vraag, VraagAdmin)

def reset_export_timestamp(modeladmin, request, queryset):
    for x in queryset:
        x.exported = None
        x.save()
reset_export_timestamp.short_description = u"Reset Export"

class AntwoordAdmin(admin.ModelAdmin):
    list_display = ('user', 'link_to_adlib_tagdb', 'link_to_obj', 'created', 'exported')
    date_hierarchy = 'created'
    search_fields = ('value', 'obj')
    actions = [reset_export_timestamp]
admin.site.register(Antwoord, AntwoordAdmin)

class SerieVraagInline(admin.TabularInline):
    model = SerieVraag
# class SerieVraagAdmin(admin.ModelAdmin):
#     pass
# admin.site.register(SerieVraag, SerieVraagAdmin)
class SerieItemInline(admin.TabularInline):
    model = SerieItem

class SerieAdmin(admin.ModelAdmin):
    inlines = [SerieVraagInline]
admin.site.register(Serie, SerieAdmin)

class UserProfileSchoolInline(admin.TabularInline):
    model = UserProfile

class SchoolAdmin(admin.ModelAdmin):
    inlines = [UserProfileSchoolInline]
admin.site.register(School, SchoolAdmin)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False

class ExtendedUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ('email', 'date_joined', 'last_login', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)

admin.site.register(Stopword)