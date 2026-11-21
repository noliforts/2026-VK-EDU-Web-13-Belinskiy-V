from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rank', 'avatar')
    search_fields = ('user__username', 'user__email', 'rank')
    list_filter = ('rank',)
    raw_id_fields = ('user',)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
