from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from django.contrib.auth.admin import UserAdmin
from django_json_widget.widgets import JSONEditorWidget
from .models import *
from .forms import CustomUserCreationForm, CompetitionForm
from django.db.models import JSONField
from django_apscheduler.admin import DjangoJob, DjangoJobExecution


class CustomJSONEditorWidget(JSONEditorWidget):
    class Media:
        css = {
            'all': ('admin/css/json_admin.css',)
        }


class LabLevelInline(admin.TabularInline):
    model = LabLevel
    extra = 1  # Display one empty level form by default
    fields = ["level_number", "description"]


class LabTaskInline(admin.TabularInline):
    model = LabTask
    extra = 1  # Shows one empty form by default


class LabModelAdmin(SummernoteModelAdmin):  # instead of ModelAdmin
    summernote_fields = 'description'
    formfield_overrides = {
        JSONField: {
            'widget': CustomJSONEditorWidget(width="50%", height="30vh")
        },
    }
    inlines = [LabLevelInline, LabTaskInline]


class MyUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    list_display = ("username", "is_staff", "platoon")
    model = User
    fieldsets = UserAdmin.fieldsets
    fieldsets = ((None, {'fields': ('username', 'password', 'platoon')}),) + fieldsets[1:]
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "first_name", "last_name", "password1", "password2", "platoon"
            )}
         ),
    )
    list_filter = ("is_staff", "platoon")
    search_fields = ("first_name", "last_name")
    exclude = ('pnet_login', )


class Competition2UserInline(admin.TabularInline):
    model = Competition2User
    extra = 0
    fields = ('user', 'level')
    readonly_fields = ('user',)
    can_delete = False


def set_all_users_to_competition_level(modeladmin, request, queryset):
    for competition in queryset:
        comp_users = competition.competition_users.all()
        comp_users.update(level=competition.level)


class CompetitionAdmin(admin.ModelAdmin):
    form = CompetitionForm
    add_form = CompetitionForm
    list_display = ("start", "lab", 'all_platoons', 'all_non_platoon_users')
    search_fields = ['lab__name']
    exclude = ('participants', 'deleted', 'slug', 'issued_labs')
    inlines = [Competition2UserInline]
    actions = [set_all_users_to_competition_level]

    class Media:
        js = ('admin/js/load_levels.js', 'admin/js/jquery-3.7.1.min.js')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        all_users = User.objects.filter(platoon__in=obj.platoons.all())
        existing_user_ids = obj.competition_users.values_list('user_id', flat=True)

        for user in all_users:
            if user.id not in existing_user_ids:
                Competition2User.objects.create(
                    competition=obj,
                    user=user,
                    level=obj.level
                )

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj and obj.lab:
            formset.form.base_fields['level'].queryset = LabLevel.objects.filter(lab=obj.lab)

        return formset

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()

    def all_platoons(self, obj):
        return ", ".join(str(tag.number) for tag in obj.platoons.all())

    def all_non_platoon_users(self, obj):
        return ", ".join(user.last_name for user in obj.non_platoon_users.all())

    all_platoons.short_description = 'Взвода'
    all_non_platoon_users.short_description = 'Отдельные пользователи'


admin.site.register(Lab, LabModelAdmin)
admin.site.register(Platoon, admin.ModelAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(User, MyUserAdmin)
admin.site.register(Answers, admin.ModelAdmin)
admin.site.unregister(DjangoJob)
admin.site.unregister(DjangoJobExecution)
