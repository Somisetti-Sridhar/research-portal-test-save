import logging
from .recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

def process_paper_upload(paper_id):
    """Process newly uploaded paper"""
    try:
        engine = RecommendationEngine()
        
        # Generate embeddings
        engine.generate_paper_embeddings(paper_id)
        
        logger.info(f"Successfully processed paper {paper_id}")
        return {"status": "success", "paper_id": paper_id}
        
    except Exception as e:
        logger.error(f"Error processing paper {paper_id}: {str(e)}")
        return {"status": "error", "error": str(e)}

def generate_recommendations(user_id):
    """Generate recommendations for a user"""
    try:
        engine = RecommendationEngine()
        recommendations = engine.hybrid_recommendations(user_id)
        engine.save_recommendations(user_id, recommendations)
        
        logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
        return {"status": "success", "count": len(recommendations)}
        
    except Exception as e:
        logger.error(f"Error generating recommendations for user {user_id}: {str(e)}")
        return {"status": "error", "error": str(e)}
