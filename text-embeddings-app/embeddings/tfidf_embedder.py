"""
TF-IDF Text Embedding Module
Provides TF-IDF vectorization with dimensionality reduction.
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import re
import string
from typing import Tuple, List, Dict, Any


class TFIDFEmbedder:
    """
    TF-IDF based text embedder with 2D dimensionality reduction.
    """
    
    def __init__(self, max_features: int = 1000, ngram_range: Tuple[int, int] = (1, 2)):
        """
        Initialize the TF-IDF embedder.
        
        Args:
            max_features: Maximum number of features to extract
            ngram_range: Range of n-grams to consider (default: unigrams and bigrams)
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vectorizer = None
        self.pca = None
        self.scaler = None
        self.is_fitted = False
        
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for TF-IDF vectorization.
        
        Args:
            text: Input text string
            
        Returns:
            Cleaned and preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """
        Fit the TF-IDF model and transform texts to 2D embeddings.
        
        Args:
            texts: List of text strings
            
        Returns:
            2D numpy array of embeddings
        """
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Initialize and fit TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            stop_words='english',
            lowercase=True,
            strip_accents='ascii'
        )
        
        # Transform texts to TF-IDF vectors
        tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
        
        # Convert to dense array for PCA
        tfidf_dense = tfidf_matrix.toarray()
        
        # Standardize features
        self.scaler = StandardScaler()
        tfidf_scaled = self.scaler.fit_transform(tfidf_dense)
        
        # Apply PCA for 2D reduction
        self.pca = PCA(n_components=2, random_state=42)
        embeddings_2d = self.pca.fit_transform(tfidf_scaled)
        
        self.is_fitted = True
        return embeddings_2d
    
    def transform(self, texts: List[str]) -> np.ndarray:
        """
        Transform new texts to 2D embeddings using fitted model.
        
        Args:
            texts: List of text strings
            
        Returns:
            2D numpy array of embeddings
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before transforming new texts")
        
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Transform to TF-IDF
        tfidf_matrix = self.vectorizer.transform(processed_texts)
        tfidf_dense = tfidf_matrix.toarray()
        
        # Scale and reduce dimensions
        tfidf_scaled = self.scaler.transform(tfidf_dense)
        embeddings_2d = self.pca.transform(tfidf_scaled)
        
        return embeddings_2d
    
    def get_feature_names(self) -> List[str]:
        """
        Get the feature names (terms) used by the TF-IDF vectorizer.
        
        Returns:
            List of feature names
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        return self.vectorizer.get_feature_names_out().tolist()
    
    def get_top_features(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Get top TF-IDF features for a given text.
        
        Args:
            text: Input text
            top_k: Number of top features to return
            
        Returns:
            List of (feature, score) tuples
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        processed_text = self.preprocess_text(text)
        tfidf_vector = self.vectorizer.transform([processed_text])
        
        feature_names = self.get_feature_names()
        scores = tfidf_vector.toarray()[0]
        
        # Get top features
        top_indices = np.argsort(scores)[::-1][:top_k]
        top_features = [(feature_names[i], scores[i]) for i in top_indices if scores[i] > 0]
        
        return top_features
    
    def get_embedding_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model.
        
        Returns:
            Dictionary with model information
        """
        if not self.is_fitted:
            return {"status": "not_fitted"}
        
        return {
            "status": "fitted",
            "method": "TF-IDF + PCA",
            "max_features": self.max_features,
            "ngram_range": self.ngram_range,
            "vocabulary_size": len(self.vectorizer.vocabulary_),
            "explained_variance_ratio": self.pca.explained_variance_ratio_.tolist(),
            "total_explained_variance": float(np.sum(self.pca.explained_variance_ratio_))
        }