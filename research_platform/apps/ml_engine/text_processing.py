import re
from apps.papers.models import Paper

class TextProcessor:
    def __init__(self):
        pass
    
    def extract_paper_text(self, paper_id):
        """Extract and process text from paper"""
        try:
            paper = Paper.objects.get(id=paper_id)
            
            # Simple text processing
            text = f"{paper.title} {paper.abstract}"
            
            # Basic cleaning
            text = re.sub(r'[^\w\s]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            text = text.lower().strip()
            
            return text
            
        except Paper.DoesNotExist:
            return ""
    
    def extract_keywords(self, text):
        """Extract keywords from text"""
        # Simple keyword extraction
        words = text.split()
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Return top keywords by frequency
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(10)]
