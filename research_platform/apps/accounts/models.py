from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    USER_TYPES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('publisher', 'Publisher'),
        ('reader', 'Reader'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='reader')
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    institution = models.CharField(max_length=200, blank=True)
    research_interests = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'search_history'
        ordering = ['-timestamp']
