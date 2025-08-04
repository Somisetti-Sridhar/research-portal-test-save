from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import User, UserProfile
from .forms import UserRegistrationForm, UserProfileForm, LoginForm
from apps.papers.models import Paper, Bookmark, Rating
from apps.groups.models import Group, GroupMember

class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('accounts:dashboard')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=email, password=password)
        if user:
            login(self.request, user)
            messages.success(self.request, 'Successfully logged in!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid credentials')
            return self.form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().get(request, *args, **kwargs)

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        user = form.save()
        UserProfile.objects.create(
            user=user,
            first_name=form.cleaned_data.get('first_name', ''),
            last_name=form.cleaned_data.get('last_name', ''),
            institution=form.cleaned_data.get('institution', ''),
            research_interests=form.cleaned_data.get('research_interests', ''),
        )
        messages.success(self.request, 'Account created successfully! Please login.')
        return super().form_valid(form)

class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'Successfully logged out!')
        return redirect('home')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        context.update({
            'profile': profile,
            'uploaded_papers': Paper.objects.filter(uploaded_by=user).count(),
            'bookmarks_count': Bookmark.objects.filter(user=user).count(),
            'ratings_count': Rating.objects.filter(user=user).count(),
            'groups_count': GroupMember.objects.filter(user=user).count(),
        })
        return context

class ProfileEditView(LoginRequiredMixin, FormView):
    template_name = 'accounts/profile_edit.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('accounts:profile')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        kwargs['instance'] = profile
        return kwargs
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's recent activity
        recent_papers = Paper.objects.filter(uploaded_by=user).order_by('-created_at')[:5]
        recent_bookmarks = Bookmark.objects.filter(user=user).select_related('paper').order_by('-created_at')[:5]
        recent_ratings = Rating.objects.filter(user=user).select_related('paper').order_by('-created_at')[:5]
        
        # Get recommendations
        try:
            from apps.ml_engine.models import UserRecommendation
            recommendations = UserRecommendation.objects.filter(user=user).select_related('paper')[:10]
        except ImportError:
            recommendations = []
        
        context.update({
            'recent_papers': recent_papers,
            'recent_bookmarks': recent_bookmarks,
            'recent_ratings': recent_ratings,
            'recommendations': recommendations,
            'user_type': user.user_type,
        })
        return context
    
from django.views.generic.edit import UpdateView


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/admin_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type not in ['admin']:
            messages.error(request, 'Access denied. Admin/Moderator privileges required.')
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get pending papers
        pending_papers = Paper.objects.filter(is_approved=False).order_by('-created_at')
        
        # Get recent activity
        recent_papers = Paper.objects.all().order_by('-created_at')[:10]
        total_users = User.objects.count()
        total_papers = Paper.objects.count()
        approved_papers = Paper.objects.filter(is_approved=True).count()
        
        context.update({
            'pending_papers': pending_papers,
            'recent_papers': recent_papers,
            'total_users': total_users,
            'total_papers': total_papers,
            'approved_papers': approved_papers,
            'pending_count': pending_papers.count(),
        })
        return context
