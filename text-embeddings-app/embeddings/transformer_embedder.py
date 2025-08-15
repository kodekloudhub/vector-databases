"""
Sentence Transformers Text Embedding Module
Provides transformer-based embeddings with dimensionality reduction.
"""

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any, Optional
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class TransformerEmbedder:
    """
    Sentence Transformer based text embedder with 2D dimensionality reduction.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the Transformer embedder.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.pca = None
        self.scaler = None
        self.is_fitted = False
        self.original_dim = None
        
    def load_model(self) -> None:
        """
        Load the sentence transformer model.
        """
        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"✅ Loaded model: {self.model_name}")
        except Exception as e:
            print(f"❌ Error loading model {self.model_name}: {str(e)}")
            # Fallback to a smaller model
            self.model_name = 'all-MiniLM-L6-v2'
            self.model = SentenceTransformer(self.model_name)
            print(f"✅ Loaded fallback model: {self.model_name}")
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """
        Fit the model and transform texts to 2D embeddings.
        
        Args:
            texts: List of text strings
            
        Returns:
            2D numpy array of embeddings
        """
        # Load model if not already loaded
        if self.model is None:
            self.load_model()
        
        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True)
        self.original_dim = embeddings.shape[1]
        
        # Standardize embeddings
        self.scaler = StandardScaler()
        embeddings_scaled = self.scaler.fit_transform(embeddings)
        
        # Apply PCA for 2D reduction
        self.pca = PCA(n_components=2, random_state=42)
        embeddings_2d = self.pca.fit_transform(embeddings_scaled)
        
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
        
        if self.model is None:
            self.load_model()
        
        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=False)
        
        # Scale and reduce dimensions
        embeddings_scaled = self.scaler.transform(embeddings)
        embeddings_2d = self.pca.transform(embeddings_scaled)
        
        return embeddings_2d
    
    def get_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score
        """
        if self.model is None:
            self.load_model()
        
        embeddings = self.model.encode([text1, text2])
        
        # Calculate cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        
        return float(similarity)
    
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
            "method": "Sentence Transformers + PCA",
            "model_name": self.model_name,
            "original_dimensions": self.original_dim,
            "reduced_dimensions": 2,
            "explained_variance_ratio": self.pca.explained_variance_ratio_.tolist(),
            "total_explained_variance": float(np.sum(self.pca.explained_variance_ratio_))
        }
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available sentence transformer models.
        
        Returns:
            List of model names
        """
        return [
            'all-MiniLM-L6-v2',  # Fast and good quality
            'all-mpnet-base-v2',  # Best quality
            'all-distilroberta-v1',  # Good balance
            'paraphrase-MiniLM-L6-v2',  # Paraphrase detection
            'multi-qa-MiniLM-L6-cos-v1'  # Question answering
        ]