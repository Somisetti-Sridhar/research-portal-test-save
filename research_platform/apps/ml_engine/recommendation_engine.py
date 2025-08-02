import random
from django.db.models import Count
from .models import UserRecommendation, PaperEmbedding
from apps.papers.models import Paper, Rating, Bookmark
from apps.accounts.models import User

class RecommendationEngine:
    def __init__(self):
        pass
    
    def generate_paper_embeddings(self, paper_id):
        """Generate simple embeddings for a paper"""
        paper = Paper.objects.get(id=paper_id)
        
        # Simple embedding based on title and abstract length
        # In production, use actual ML models
        embedding = [
            len(paper.title),
            len(paper.abstract),
            paper.view_count,
            paper.download_count,
            random.random()  # Random component for diversity
        ]
        
        # Save embedding
        PaperEmbedding.objects.update_or_create(
            paper=paper,
            defaults={
                'embedding': embedding,
                'model_version': 'simple-v1'
            }
        )
        
        return embedding
    
    def collaborative_filtering(self, user_id, top_k=10):
        """Simple collaborative filtering based on user ratings"""
        user = User.objects.get(id=user_id)
        
        # Get papers rated highly by the user
        user_high_rated = Rating.objects.filter(
            user=user, 
            rating__gte=4
        ).values_list('paper_id', flat=True)
        
        if not user_high_rated:
            return []
        
        # Find users who also rated these papers highly
        similar_users = Rating.objects.filter(
            paper_id__in=user_high_rated,
            rating__gte=4
        ).exclude(user=user).values_list('user_id', flat=True).distinct()
        
        # Get papers these similar users rated highly
        recommendations = Rating.objects.filter(
            user_id__in=similar_users,
            rating__gte=4
        ).exclude(
            paper_id__in=user_high_rated
        ).values('paper_id').annotate(
            score=Count('id')
        ).order_by('-score')[:top_k]
        
        return [(rec['paper_id'], rec['score']) for rec in recommendations]
    
    def content_based_filtering(self, user_id, top_k=10):
        """Simple content-based filtering"""
        user = User.objects.get(id=user_id)
        
        # Get user's bookmarked/rated papers
        user_papers = set()
        user_papers.update(Bookmark.objects.filter(user=user).values_list('paper_id', flat=True))
        user_papers.update(Rating.objects.filter(user=user, rating__gte=4).values_list('paper_id', flat=True))
        
        if not user_papers:
            # Return popular papers if no user history
            popular_papers = Paper.objects.filter(
                is_approved=True
            ).order_by('-view_count')[:top_k]
            return [(paper.id, paper.view_count) for paper in popular_papers]
        
        # Get categories of user's papers
        user_categories = Paper.objects.filter(
            id__in=user_papers
        ).values_list('categories__id', flat=True).distinct()
        
        # Recommend papers from same categories
        recommendations = Paper.objects.filter(
            categories__id__in=user_categories,
            is_approved=True
        ).exclude(
            id__in=user_papers
        ).annotate(
            score=Count('categories')
        ).order_by('-score', '-view_count')[:top_k]
        
        return [(paper.id, paper.score) for paper in recommendations]
    
    def hybrid_recommendations(self, user_id, top_k=10):
        """Combine collaborative and content-based filtering"""
        cf_recs = self.collaborative_filtering(user_id, top_k * 2)
        cb_recs = self.content_based_filtering(user_id, top_k * 2)
        
        # Combine scores with weights
        combined_scores = {}
        
        for paper_id, score in cf_recs:
            combined_scores[paper_id] = combined_scores.get(paper_id, 0) + 0.6 * score
        
        for paper_id, score in cb_recs:
            combined_scores[paper_id] = combined_scores.get(paper_id, 0) + 0.4 * score
        
        # Sort and return top recommendations
        recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return recommendations[:top_k]
    
    def save_recommendations(self, user_id, recommendations):
        """Save recommendations to database"""
        user = User.objects.get(id=user_id)
        
        # Clear existing recommendations
        UserRecommendation.objects.filter(user=user).delete()
        
        # Save new recommendations
        for paper_id, score in recommendations:
            try:
                paper = Paper.objects.get(id=paper_id)
                UserRecommendation.objects.create(
                    user=user,
                    paper=paper,
                    score=score,
                    reason="Recommended based on your reading history and preferences"
                )
            except Paper.DoesNotExist:
                continue
