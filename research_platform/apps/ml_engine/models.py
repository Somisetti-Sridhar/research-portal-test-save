from django.db import models
from apps.accounts.models import User
from apps.papers.models import Paper

class UserRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    reason = models.TextField(default="Recommended based on your activity")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_recommendations'
        unique_together = ['user', 'paper']
        ordering = ['-score']

    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.paper.title}"

class RecommendationModel(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    model_path = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recommendation_models'

class PaperEmbedding(models.Model):
    paper = models.OneToOneField(Paper, on_delete=models.CASCADE)
    embedding = models.JSONField(default=list)  # Store as JSON array
    model_version = models.CharField(max_length=50, default='simple')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'paper_embeddings'
