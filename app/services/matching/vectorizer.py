from typing import List, Counter
import math

class SimpleVectorizer:
    """
    Lightweight TF-IDF / Cosine Similarity Vectorizer using pure Python.
    Avoids heavy dependencies like sklearn/torch for this specific microservice scope,
    while remaining production-safe and fast.
    """
    
    def compute_cosine_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
            
        vec1 = self._text_to_vector(text1)
        vec2 = self._text_to_vector(text2)
        
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        
        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        
        if not denominator:
            return 0.0
        
        return numerator / denominator

    def _text_to_vector(self, text: str) -> Counter:
        words = text.lower().replace(r'[^\w\s]', '').split()
        return Counter(words)
