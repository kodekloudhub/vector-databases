import numpy as np
import logging
from typing import List, Union
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config import EMBEDDING_MODEL, EMBEDDING_DIMENSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for generating and managing embeddings using sentence-transformers.
    """
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence-transformers model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Numpy array containing the embedding vector
        """
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once
            
        Returns:
            Numpy array containing all embeddings
        """
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            # Generate embeddings in batches for memory efficiency
            embeddings = self.model.encode(
                texts, 
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            
            logger.info(f"Generated embeddings shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def calculate_similarity(self, query_embedding: np.ndarray, 
                           document_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between query and document embeddings.
        
        Args:
            query_embedding: Single query embedding vector
            document_embeddings: Array of document embeddings
            
        Returns:
            Array of similarity scores
        """
        try:
            # Ensure query embedding is 2D for sklearn
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_embedding, document_embeddings)
            return similarities.flatten()
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            raise
    
    def find_most_similar(self, query_embedding: np.ndarray, 
                         document_embeddings: np.ndarray, 
                         top_k: int = 5) -> List[tuple]:
        """
        Find the most similar documents to a query.
        
        Args:
            query_embedding: Query embedding vector
            document_embeddings: Array of document embeddings
            top_k: Number of top results to return
            
        Returns:
            List of tuples (index, similarity_score) sorted by similarity
        """
        try:
            # Calculate similarities
            similarities = self.calculate_similarity(query_embedding, document_embeddings)
            
            # Get top-k indices and scores
            top_indices = np.argsort(similarities)[::-1][:top_k]
            top_scores = similarities[top_indices]
            
            # Return as list of tuples
            results = [(int(idx), float(score)) for idx, score in zip(top_indices, top_scores)]
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar documents: {e}")
            raise
    
    def save_embeddings(self, embeddings: np.ndarray, file_path: str):
        """
        Save embeddings to a numpy file.
        
        Args:
            embeddings: Numpy array of embeddings
            file_path: Path to save the embeddings
        """
        try:
            np.save(file_path, embeddings)
            logger.info(f"Saved embeddings to {file_path}")
        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")
            raise
    
    def load_embeddings(self, file_path: str) -> np.ndarray:
        """
        Load embeddings from a numpy file.
        
        Args:
            file_path: Path to the embeddings file
            
        Returns:
            Numpy array of embeddings
        """
        try:
            embeddings = np.load(file_path)
            logger.info(f"Loaded embeddings from {file_path}, shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            raise
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        if not self.model:
            return {"error": "Model not loaded"}
        
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "max_sequence_length": getattr(self.model, 'max_seq_length', 'Unknown'),
            "device": str(self.model.device)
        }
    
    def validate_embeddings(self, embeddings: np.ndarray) -> dict:
        """
        Validate embeddings array.
        
        Args:
            embeddings: Numpy array of embeddings
            
        Returns:
            Validation report
        """
        validation_report = {
            "valid": True,
            "shape": embeddings.shape,
            "dtype": str(embeddings.dtype),
            "has_nan": bool(np.isnan(embeddings).any()),
            "has_inf": bool(np.isinf(embeddings).any()),
            "min_value": float(np.min(embeddings)),
            "max_value": float(np.max(embeddings)),
            "mean_value": float(np.mean(embeddings))
        }
        
        # Check for issues
        if validation_report["has_nan"] or validation_report["has_inf"]:
            validation_report["valid"] = False
            validation_report["error"] = "Embeddings contain NaN or Inf values"
        
        if len(embeddings.shape) != 2:
            validation_report["valid"] = False
            validation_report["error"] = "Embeddings should be 2D array"
        
        expected_dim = EMBEDDING_DIMENSION
        if embeddings.shape[1] != expected_dim:
            validation_report["valid"] = False
            validation_report["error"] = f"Expected dimension {expected_dim}, got {embeddings.shape[1]}"
        
        return validation_report

if __name__ == "__main__":
    # Test the embedding service
    embedding_service = EmbeddingService()
    
    # Test single embedding
    test_text = "How to change engine oil in a car"
    embedding = embedding_service.generate_embedding(test_text)
    print(f"Generated embedding shape: {embedding.shape}")
    
    # Test batch embeddings
    test_texts = [
        "Engine oil change procedure",
        "Brake pad replacement",
        "Battery testing and replacement"
    ]
    
    batch_embeddings = embedding_service.generate_embeddings_batch(test_texts)
    print(f"Batch embeddings shape: {batch_embeddings.shape}")
    
    # Test similarity calculation
    query_embedding = embedding_service.generate_embedding("oil change")
    similarities = embedding_service.calculate_similarity(query_embedding, batch_embeddings)
    print(f"Similarities: {similarities}")
    
    # Test finding most similar
    most_similar = embedding_service.find_most_similar(query_embedding, batch_embeddings, top_k=2)
    print(f"Most similar: {most_similar}")
    
    # Test model info
    model_info = embedding_service.get_model_info()
    print(f"Model info: {model_info}")