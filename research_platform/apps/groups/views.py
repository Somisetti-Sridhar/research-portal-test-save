from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Group, GroupMember, GroupPaper
from .forms import GroupCreateForm, GroupEditForm
from apps.papers.models import Paper

class GroupListView(ListView):
    model = Group
    template_name = 'groups/list.html'
    context_object_name = 'groups'
    paginate_by = 12
    
    def get_queryset(self):
        return Group.objects.filter(is_private=False).order_by('-created_at')

class GroupDetailView(DetailView):
    model = Group
    template_name = 'groups/detail.html'
    context_object_name = 'group'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object
        
        context['members'] = GroupMember.objects.filter(group=group).select_related('user')
        context['papers'] = GroupPaper.objects.filter(group=group).select_related('paper')
        
        if self.request.user.is_authenticated:
            context['is_member'] = GroupMember.objects.filter(group=group, user=self.request.user).exists()
            context['user_papers'] = Paper.objects.filter(uploaded_by=self.request.user, is_approved=True)
        
        return context

class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupCreateForm
    template_name = 'groups/create.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        group = form.save()
        
        # Add creator as admin
        GroupMember.objects.create(
            group=group,
            user=self.request.user,
            role='admin'
        )
        
        messages.success(self.request, 'Group created successfully!')
        return redirect('groups:detail', pk=group.pk)

class GroupEditView(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupEditForm
    template_name = 'groups/edit.html'
    
    def get_queryset(self):
        return Group.objects.filter(created_by=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('groups:detail', kwargs={'pk': self.object.pk})

class MyGroupsView(LoginRequiredMixin, ListView):
    model = GroupMember
    template_name = 'groups/my_groups.html'
    context_object_name = 'memberships'
    paginate_by = 12
    
    def get_queryset(self):
        return GroupMember.objects.filter(user=self.request.user).select_related('group')

@login_required
def join_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    
    if group.is_private:
        messages.error(request, 'This is a private group.')
        return redirect('groups:detail', pk=pk)
    
    member, created = GroupMember.objects.get_or_create(
        group=group,
        user=request.user,
        defaults={'role': 'member'}
    )
    
    if created:
        messages.success(request, f'You have joined "{group.name}"!')
    else:
        messages.info(request, 'You are already a member of this group.')
    
    return redirect('groups:detail', pk=pk)

@login_required
def leave_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    
    try:
        member = GroupMember.objects.get(group=group, user=request.user)
        member.delete()
        messages.success(request, f'You have left "{group.name}".')
    except GroupMember.DoesNotExist:
        messages.error(request, 'You are not a member of this group.')
    
    return redirect('groups:detail', pk=pk)

@login_required
def add_paper_to_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    
    # Check if user is a member
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        messages.error(request, 'You must be a member to add papers to this group.')
        return redirect('groups:detail', pk=pk)
    
    if request.method == 'POST':
        paper_id = request.POST.get('paper_id')
        paper = get_object_or_404(Paper, pk=paper_id, is_approved=True)
        
        group_paper, created = GroupPaper.objects.get_or_create(
            group=group,
            paper=paper,
            defaults={'added_by': request.user}
        )
        
        if created:
            messages.success(request, f'Paper "{paper.title}" added to group!')
        else:
            messages.info(request, 'Paper is already in this group.')
    
    return redirect('groups:detail', pk=pk)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from .models import Group, GroupMember, GroupPaper
from .forms import GroupCreateForm, GroupEditForm, GroupInviteForm
from apps.papers.models import Paper
from apps.accounts.models import User

# Add these new views to your existing views.py file:

@login_required
def invite_member(request, pk):
    group = get_object_or_404(Group, pk=pk)
    
    # Check if user has permission to invite (admin or moderator)
    user_membership = GroupMember.objects.filter(group=group, user=request.user).first()
    if not user_membership or user_membership.role not in ['admin', 'moderator']:
        messages.error(request, 'You do not have permission to invite members to this group.')
        return redirect('groups:detail', pk=pk)
    
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        role = request.POST.get('role', 'member')
        
        # Find user by username or email
        try:
            user = User.objects.get(
                Q(username=username_or_email) | Q(email=username_or_email)
            )
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('groups:detail', pk=pk)
        
        # Check if user is already a member
        if GroupMember.objects.filter(group=group, user=user).exists():
            messages.error(request, 'User is already a member of this group.')
            return redirect('groups:detail', pk=pk)
        
        # Add user to group
        GroupMember.objects.create(
            group=group,
            user=user,
            role=role
        )
        
        messages.success(request, f'Successfully added {user.username} to the group.')
        return redirect('groups:detail', pk=pk)
    
    return redirect('groups:detail', pk=pk)

@login_required
def remove_member(request, pk, user_id):
    group = get_object_or_404(Group, pk=pk)
    member_to_remove = get_object_or_404(User, pk=user_id)
    
    # Check if user has permission to remove members
    user_membership = GroupMember.objects.filter(group=group, user=request.user).first()
    if not user_membership or user_membership.role not in ['admin', 'moderator']:
        messages.error(request, 'You do not have permission to remove members.')
        return redirect('groups:detail', pk=pk)
    
    # Don't allow removing the group creator unless user is admin
    if member_to_remove == group.created_by and request.user != group.created_by:
        messages.error(request, 'Cannot remove the group creator.')
        return redirect('groups:detail', pk=pk)
    
    # Remove member
    try:
        membership = GroupMember.objects.get(group=group, user=member_to_remove)
        membership.delete()
        messages.success(request, f'Successfully removed {member_to_remove.username} from the group.')
    except GroupMember.DoesNotExist:
        messages.error(request, 'User is not a member of this group.')
    
    return redirect('groups:detail', pk=pk)

@login_required
def update_member_role(request, pk, user_id):
    group = get_object_or_404(Group, pk=pk)
    member = get_object_or_404(User, pk=user_id)
    
    # Check if user has permission to update roles
    user_membership = GroupMember.objects.filter(group=group, user=request.user).first()
    if not user_membership or user_membership.role != 'admin':
        messages.error(request, 'Only group admins can update member roles.')
        return redirect('groups:detail', pk=pk)
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['admin', 'moderator', 'member']:
            try:
                membership = GroupMember.objects.get(group=group, user=member)
                membership.role = new_role
                membership.save()
                messages.success(request, f'Updated {member.username} role to {new_role}.')
            except GroupMember.DoesNotExist:
                messages.error(request, 'User is not a member of this group.')
    
    return redirect('groups:detail', pk=pk)

class GroupMembersView(LoginRequiredMixin, DetailView):
    model = Group
    template_name = 'groups/members.html'
    context_object_name = 'group'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object
        
        # Check if user is a member
        user_membership = GroupMember.objects.filter(group=group, user=self.request.user).first()
        context['user_membership'] = user_membership
        context['is_member'] = user_membership is not None
        context['can_manage'] = user_membership and user_membership.role in ['admin', 'moderator'] if user_membership else False
        
        # Get all members
        context['members'] = GroupMember.objects.filter(group=group).select_related('user').order_by('role', 'joined_at')
        
        return context
