from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q
from apps.papers.models import Paper, Category
from apps.accounts.models import SearchHistory

class SearchView(ListView):
    model = Paper
    template_name = 'search/results.html'
    context_object_name = 'papers'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        category = self.request.GET.get('category', '')
        author = self.request.GET.get('author', '')
        year_from = self.request.GET.get('year_from', '')
        year_to = self.request.GET.get('year_to', '')
        
        queryset = Paper.objects.filter(is_approved=True)
        
        if query:
            # Save search history for authenticated users
            if self.request.user.is_authenticated:
                SearchHistory.objects.create(user=self.request.user, query=query)
            
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(abstract__icontains=query) |
                Q(authors__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(categories__id=category)
        
        if author:
            queryset = queryset.filter(authors__icontains=author)
        
        if year_from:
            queryset = queryset.filter(publication_date__year__gte=year_from)
        
        if year_to:
            queryset = queryset.filter(publication_date__year__lte=year_to)
        
        return queryset.distinct().order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['author'] = self.request.GET.get('author', '')
        context['year_from'] = self.request.GET.get('year_from', '')
        context['year_to'] = self.request.GET.get('year_to', '')
        return context

class AdvancedSearchView(TemplateView):
    template_name = 'search/advanced.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class SearchHistoryView(LoginRequiredMixin, ListView):
    model = SearchHistory
    template_name = 'search/history.html'
    context_object_name = 'searches'
    paginate_by = 20
    
    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user).order_by('-timestamp')

def search_suggestions(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'suggestions': []})
    
    # Get title suggestions
    papers = Paper.objects.filter(
        title__icontains=query,
        is_approved=True
    ).values_list('title', flat=True)[:10]
    
    suggestions = list(papers)
    return JsonResponse({'suggestions': suggestions})

class PaperSearchView(SearchView):
    """API version of search view"""
    pass
