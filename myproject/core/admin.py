from django.contrib import admin
from .models import UserData, UserProfile

# 在admin界面展示、修改用户的UserData模型值
@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'value')
    search_fields = ('user__username', 'key')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_joined')
    search_fields = ('user__username', 'key')