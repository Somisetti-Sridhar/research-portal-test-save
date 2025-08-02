from django.contrib import admin
from .models import Paper, Category, Bookmark, Rating, Citation, ReadingProgress

@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_by', 'is_approved', 'view_count', 'download_count', 'created_at']
    list_filter = ['is_approved', 'created_at', 'categories']
    search_fields = ['title', 'authors', 'abstract']
    actions = ['approve_papers', 'reject_papers']
    
    def approve_papers(self, request, queryset):
        queryset.update(is_approved=True)
    approve_papers.short_description = "Approve selected papers"
    
    def reject_papers(self, request, queryset):
        queryset.update(is_approved=False)
    reject_papers.short_description = "Reject selected papers"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'paper', 'folder', 'created_at']
    list_filter = ['folder', 'created_at']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'paper', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']

@admin.register(Citation)
class CitationAdmin(admin.ModelAdmin):
    list_display = ['citing_paper', 'cited_paper']
    search_fields = ['citing_paper__title', 'cited_paper__title']
