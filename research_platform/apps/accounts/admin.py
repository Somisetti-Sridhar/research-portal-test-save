from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, SearchHistory

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'user_type', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'created_at']
    search_fields = ['username', 'email']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_type',)}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'institution']
    search_fields = ['user__username', 'first_name', 'last_name', 'institution']

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'query', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['user__username', 'query']
