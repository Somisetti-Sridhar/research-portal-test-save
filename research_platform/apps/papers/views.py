from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from .models import Paper, Category, Bookmark, Rating, Citation
from .forms import PaperUploadForm, PaperEditForm, RatingForm
from apps.accounts.permissions import IsPublisherOrAbove, IsModeratorOrAdmin
from django.views.generic import CreateView

class PaperListView(ListView):
    model = Paper
    template_name = 'papers/list.html'
    context_object_name = 'papers'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Paper.objects.filter(is_approved=True).select_related('uploaded_by').prefetch_related('categories')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(abstract__icontains=search_query) |
                Q(authors__icontains=search_query)
            )
        
        # Category filter
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by == 'popular':
            queryset = queryset.order_by('-view_count')
        elif sort_by == 'rating':
            queryset = queryset.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')
        elif sort_by == 'citations':
            queryset = queryset.annotate(citation_count=Count('cited_by')).order_by('-citation_count')
        else:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['sort_by'] = self.request.GET.get('sort', '-created_at')
        return context

class PaperDetailView(DetailView):
    model = Paper
    template_name = 'papers/detail.html'
    context_object_name = 'paper'
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.user_type in ['moderator', 'admin']:
                return Paper.objects.all()
            elif self.request.user.user_type == 'publisher':
                return Paper.objects.filter(
                    Q(uploaded_by=self.request.user) | Q(is_approved=True)
                )
        return Paper.objects.filter(is_approved=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paper = self.object
        
        # Increment view count
        Paper.objects.filter(id=paper.id).update(view_count=paper.view_count + 1)
        
        # Get related data
        context['ratings'] = Rating.objects.filter(paper=paper).select_related('user')
        context['citations'] = Citation.objects.filter(cited_paper=paper).select_related('citing_paper')
        context['cited_papers'] = Citation.objects.filter(citing_paper=paper).select_related('cited_paper')
        
        if self.request.user.is_authenticated:
            context['user_bookmark'] = Bookmark.objects.filter(user=self.request.user, paper=paper).first()
            context['user_rating'] = Rating.objects.filter(user=self.request.user, paper=paper).first()
            context['rating_form'] = RatingForm()
        
        return context

class PaperUploadView(LoginRequiredMixin, CreateView):
    model = Paper
    form_class = PaperUploadForm
    template_name = 'papers/upload.html'
    success_url = reverse_lazy('papers:my_papers')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type not in ['publisher', 'moderator', 'admin']:
            messages.error(request, 'You do not have permission to upload papers.')
            return redirect('papers:list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        if self.request.user.user_type in ['moderator', 'admin']:
            form.instance.is_approved = True
        messages.success(self.request, 'Paper uploaded successfully!')
        return super().form_valid(form)

class PaperEditView(LoginRequiredMixin, UpdateView):
    model = Paper
    form_class = PaperEditForm
    template_name = 'papers/edit.html'
    
    def get_queryset(self):
        if self.request.user.user_type in ['moderator', 'admin']:
            return Paper.objects.all()
        return Paper.objects.filter(uploaded_by=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('papers:detail', kwargs={'pk': self.object.pk})

class PaperDeleteView(LoginRequiredMixin, DeleteView):
    model = Paper
    template_name = 'papers/delete.html'
    success_url = reverse_lazy('papers:my_papers')
    
    def get_queryset(self):
        if self.request.user.user_type in ['moderator', 'admin']:
            return Paper.objects.all()
        return Paper.objects.filter(uploaded_by=self.request.user)

class MyPapersView(LoginRequiredMixin, ListView):
    model = Paper
    template_name = 'papers/my_papers.html'
    context_object_name = 'papers'
    paginate_by = 10
    
    def get_queryset(self):
        return Paper.objects.filter(uploaded_by=self.request.user).order_by('-created_at')

class BookmarkListView(LoginRequiredMixin, ListView):
    model = Bookmark
    template_name = 'papers/bookmarks.html'
    context_object_name = 'bookmarks'
    paginate_by = 12
    
    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('paper').order_by('-created_at')

class CategoryListView(ListView):
    model = Category
    template_name = 'papers/categories.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'papers/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['papers'] = Paper.objects.filter(categories=self.object, is_approved=True).order_by('-created_at')
        return context

class PendingApprovalView(LoginRequiredMixin, ListView):
    model = Paper
    template_name = 'papers/pending_approval.html'
    context_object_name = 'papers'
    paginate_by = 10
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type not in ['moderator', 'admin']:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('papers:list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Paper.objects.filter(is_approved=False).order_by('-created_at')

@login_required
def bookmark_paper(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, paper=paper)
    
    if created:
        messages.success(request, 'Paper bookmarked successfully!')
    else:
        bookmark.delete()
        messages.success(request, 'Bookmark removed!')
    
    return redirect('papers:detail', pk=pk)

@login_required
def rate_paper(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating, created = Rating.objects.get_or_create(
                user=request.user,
                paper=paper,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'review_text': form.cleaned_data['review_text']
                }
            )
            if not created:
                rating.rating = form.cleaned_data['rating']
                rating.review_text = form.cleaned_data['review_text']
                rating.save()
            
            messages.success(request, 'Rating submitted successfully!')
    
    return redirect('papers:detail', pk=pk)

@login_required
def download_paper(request, pk):
    paper = get_object_or_404(Paper, pk=pk, is_approved=True)
    
    # Increment download count
    Paper.objects.filter(id=paper.id).update(download_count=paper.download_count + 1)
    
    # Serve file
    if paper.pdf_path:
        response = HttpResponse(paper.pdf_path.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{paper.title}.pdf"'
        return response
    
    raise Http404("File not found")

@login_required
def approve_paper(request, pk):
    if request.user.user_type not in ['moderator', 'admin']:
        messages.error(request, 'You do not have permission to approve papers.')
        return redirect('papers:list')
    
    paper = get_object_or_404(Paper, pk=pk)
    paper.is_approved = True
    paper.save()
    messages.success(request, f'Paper "{paper.title}" approved successfully!')
    return redirect('papers:pending_approval')

@login_required
def reject_paper(request, pk):
    if request.user.user_type not in ['moderator', 'admin']:
        messages.error(request, 'You do not have permission to reject papers.')
        return redirect('papers:list')
    
    paper = get_object_or_404(Paper, pk=pk)
    paper.delete()
    messages.success(request, 'Paper rejected and deleted successfully!')
    return redirect('papers:pending_approval')

@login_required
def get_recommendations(request):
    """Get recommendations for the current user"""
    try:
        from apps.ml_engine.models import UserRecommendation
        recommendations = UserRecommendation.objects.filter(
            user=request.user
        ).select_related('paper')[:10]
    except ImportError:
        recommendations = []
    
    if request.content_type == 'application/json':
        data = []
        for rec in recommendations:
            data.append({
                'paper_id': rec.paper.id,
                'title': rec.paper.title,
                'score': rec.score,
                'reason': rec.reason
            })
        return JsonResponse({'recommendations': data})
    
    return render(request, 'papers/recommendations.html', {
        'recommendations': recommendations
    })

# Add these imports at the top of your papers/views.py file
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.http import JsonResponse

# Add these views at the end of your papers/views.py file

class PaperListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating papers"""
    serializer_class = None  # Will be defined when serializers are ready
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Paper.objects.filter(is_approved=True)
    
    def list(self, request, *args, **kwargs):
        papers = self.get_queryset()
        data = []
        for paper in papers:
            data.append({
                'id': paper.id,
                'title': paper.title,
                'abstract': paper.abstract,
                'authors': paper.authors,
                'publication_date': paper.publication_date,
                'uploaded_by': paper.uploaded_by.username,
                'view_count': paper.view_count,
                'download_count': paper.download_count,
            })
        return Response(data)
    
    def create(self, request, *args, **kwargs):
        return Response({'message': 'Paper creation via API not implemented yet'}, 
                       status=status.HTTP_501_NOT_IMPLEMENTED)

class BookmarkListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating bookmarks"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        bookmarks = self.get_queryset()
        data = []
        for bookmark in bookmarks:
            data.append({
                'id': bookmark.id,
                'paper_title': bookmark.paper.title,
                'paper_id': bookmark.paper.id,
                'created_at': bookmark.created_at,
                'folder': bookmark.folder,
            })
        return Response(data)
    
    def create(self, request, *args, **kwargs):
        return Response({'message': 'Bookmark creation via API not implemented yet'}, 
                       status=status.HTTP_501_NOT_IMPLEMENTED)

class RatingListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating ratings"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        ratings = self.get_queryset()
        data = []
        for rating in ratings:
            data.append({
                'id': rating.id,
                'paper_title': rating.paper.title,
                'paper_id': rating.paper.id,
                'rating': rating.rating,
                'review_text': rating.review_text,
                'created_at': rating.created_at,
            })
        return Response(data)
    
    def create(self, request, *args, **kwargs):
        return Response({'message': 'Rating creation via API not implemented yet'}, 
                       status=status.HTTP_501_NOT_IMPLEMENTED)

@login_required
def download_paper(request, pk):
    # Only allow downloading approved papers
    paper = get_object_or_404(Paper, pk=pk, is_approved=True)
    
    # Increment download count
    Paper.objects.filter(id=paper.id).update(download_count=paper.download_count + 1)
    
    # Check if PDF file exists
    if paper.pdf_path and paper.pdf_path.name:
        try:
            response = HttpResponse(paper.pdf_path.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{paper.title}.pdf"'
            return response
        except FileNotFoundError:
            messages.error(request, 'PDF file not found.')
            return redirect('papers:detail', pk=pk)
    else:
        messages.error(request, 'No PDF file available for this paper.')
        return redirect('papers:detail', pk=pk)




class PaperUploadView(LoginRequiredMixin, CreateView):
    model = Paper
    form_class = PaperUploadForm
    template_name = "papers/upload.html"
    success_url = reverse_lazy("papers:my_papers")

    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type not in ["publisher", "moderator", "admin"]:
            messages.error(request, "You do not have permission to upload papers.")
            return redirect("papers:list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        paper = form.save(commit=False)
        paper.uploaded_by = self.request.user

        # approve only if uploader is moderator or admin
        paper.is_approved = self.request.user.user_type in ["moderator", "admin"]

        paper.save()         # first and only save
        form.save_m2m()      # add M2M categories after instance exists

        messages.success(
            self.request,
            "Paper uploaded successfully!"
            + ("" if paper.is_approved else "  It will be visible after moderator approval.")
        )
        return super().form_valid(form)
