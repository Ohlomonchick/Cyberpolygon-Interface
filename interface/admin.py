from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from django.contrib.auth.admin import UserAdmin

from .models import *


class SomeModelAdmin(SummernoteModelAdmin):  # instead of ModelAdmin
    summernote_fields = '__all__'


admin.site.register(Lab, SomeModelAdmin)
admin.site.register(User, UserAdmin)
