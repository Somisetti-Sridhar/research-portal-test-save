from django.db import models
from django.utils import timezone
from apps.accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name

class Paper(models.Model):
    title = models.CharField(max_length=500)
    abstract = models.TextField()
    authors = models.TextField()  # JSON field for multiple authors
    publication_date = models.DateField()
    doi = models.CharField(max_length=100, blank=True, unique=True)
    pdf_path = models.FileField(upload_to='papers/pdfs/', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_papers')
    categories = models.ManyToManyField(Category, through='PaperCategory')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'papers'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0
    
    @property
    def citation_count(self):
        return self.cited_by.count()

class PaperCategory(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'paper_categories'
        unique_together = ['paper', 'category']

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(default=timezone.now)
    folder = models.CharField(max_length=100, default='default')
    
    class Meta:
        db_table = 'bookmarks'
        unique_together = ['user', 'paper']

class Citation(models.Model):
    citing_paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='citations')
    cited_paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='cited_by')
    
    class Meta:
        db_table = 'citations'
        unique_together = ['citing_paper', 'cited_paper']

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'ratings'
        unique_together = ['user', 'paper']

class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    progress_percentage = models.FloatField(default=0.0)
    last_page = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reading_progress'
        unique_together = ['user', 'paper']
