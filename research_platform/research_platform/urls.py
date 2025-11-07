from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from apps.papers.models import Paper, Category
from django.db.models import Count

def home_view(request):
    """Custom home view with context data"""
    recent_papers = Paper.objects.filter(is_approved=True).order_by('-created_at')[:6]
    popular_categories = Category.objects.annotate(
        paper_count=Count('paper')
    ).order_by('-paper_count')[:6]
    
    return render(request, 'home.html', {
        'recent_papers': recent_papers,
        'popular_categories': popular_categories,
    })

def info_view(request):
    """Info page with legal and project information"""
    return render(request, 'info.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('info/', info_view, name='info'),
    path('api/', include('apps.api.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('papers/', include('apps.papers.urls')),
    path('groups/', include('apps.groups.urls')),
    path('chat/', include('apps.chat.urls')),
    path('search/', include('apps.search.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
