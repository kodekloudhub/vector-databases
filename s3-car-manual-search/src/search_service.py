import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from .manual_processor import ManualProcessor
from .embedding_service import EmbeddingService
from .s3_vector_service import S3VectorService
from config import MAX_SEARCH_RESULTS, SIMILARITY_THRESHOLD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchService:
    """
    Main search service that combines manual processing, embeddings, and S3 storage
    to provide vector-based search functionality for car manual sections.
    """
    
    def __init__(self):
        """Initialize the search service with all required components."""
        self.manual_processor = ManualProcessor()
        self.embedding_service = EmbeddingService()
        self.s3_service = S3VectorService()
        
        # Cache for loaded data
        self._embeddings_cache = None
        self._metadata_cache = None
        self._sections_cache = None
        
        logger.info("Search service initialized")
    
    def initialize_data(self) -> bool:
        """
        Initialize the search service by loading manual data and generating embeddings.
        This should be called once during setup.
        
        Returns:
            True if initialization successful
        """
        try:
            logger.info("Initializing search service data...")
            
            # Load manual sections
            sections = self.manual_processor.load_manual_data()
            if not sections:
                logger.error("No manual sections loaded")
                return False
            
            # Generate embeddings for all sections
            texts = self.manual_processor.get_all_texts_for_embedding()
            embeddings = self.embedding_service.generate_embeddings_batch(texts)
            
            # Get metadata
            metadata = self.manual_processor.get_section_metadata()
            
            # Upload to S3
            success = self._upload_all_data(sections, embeddings, metadata)
            if success:
                logger.info("Search service initialized successfully")
                return True
            else:
                logger.error("Failed to upload data to S3")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing search service: {e}")
            return False
    
    def _upload_all_data(self, sections: List[Dict[str, Any]], 
                        embeddings: np.ndarray, 
                        metadata: List[Dict[str, Any]]) -> bool:
        """
        Upload all data to S3.
        
        Args:
            sections: Manual sections
            embeddings: Generated embeddings
            metadata: Section metadata
            
        Returns:
            True if all uploads successful
        """
        try:
            # Create bucket if needed
            if not self.s3_service.create_bucket_if_not_exists():
                return False
            
            # Upload manual data
            if not self.s3_service.upload_manual_data(sections):
                return False
            
            # Upload embeddings
            if not self.s3_service.upload_embeddings(embeddings):
                return False
            
            # Upload metadata
            if not self.s3_service.upload_metadata(metadata):
                return False
            
            logger.info("All data uploaded to S3 successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading data to S3: {e}")
            return False
    
    def _load_data_from_s3(self) -> bool:
        """
        Load embeddings, metadata, and sections from S3 into cache.
        
        Returns:
            True if data loaded successfully
        """
        try:
            # Load embeddings
            if self._embeddings_cache is None:
                self._embeddings_cache = self.s3_service.download_embeddings()
                if self._embeddings_cache is None:
                    logger.error("Failed to load embeddings from S3")
                    return False
            
            # Load metadata
            if self._metadata_cache is None:
                self._metadata_cache = self.s3_service.download_metadata()
                if self._metadata_cache is None:
                    logger.error("Failed to load metadata from S3")
                    return False
            
            # Load sections
            if self._sections_cache is None:
                self._sections_cache = self.s3_service.download_manual_data()
                if self._sections_cache is None:
                    logger.error("Failed to load manual data from S3")
                    return False
            
            logger.info("Data loaded from S3 successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data from S3: {e}")
            return False
    
    def search(self, query: str, top_k: int = MAX_SEARCH_RESULTS) -> List[Dict[str, Any]]:
        """
        Search for relevant manual sections based on a query.
        
        Args:
            query: Search query from the user
            top_k: Number of top results to return
            
        Returns:
            List of search results with sections and similarity scores
        """
        try:
            logger.info(f"Searching for: '{query}'")
            
            # Load data from S3 if not cached
            if not self._load_data_from_s3():
                # Fallback to local keyword search
                logger.warning("Using fallback keyword search")
                return self._fallback_search(query, top_k)
            
            # Generate embedding for the query
            query_embedding = self.embedding_service.generate_embedding(query)
            
            # Find most similar sections
            similar_results = self.embedding_service.find_most_similar(
                query_embedding, 
                self._embeddings_cache, 
                top_k
            )
            
            # Prepare results with section data
            search_results = []
            for idx, similarity_score in similar_results:
                if similarity_score >= SIMILARITY_THRESHOLD:
                    section = self._sections_cache[idx]
                    metadata = self._metadata_cache[idx]
                    
                    result = {
                        'section': section,
                        'metadata': metadata,
                        'similarity_score': similarity_score,
                        'rank': len(search_results) + 1
                    }
                    search_results.append(result)
            
            # If no results above threshold, use fallback
            if not search_results:
                logger.warning(f"No results above similarity threshold {SIMILARITY_THRESHOLD}")
                return self._fallback_search(query, top_k)
            
            logger.info(f"Found {len(search_results)} relevant results")
            return search_results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            # Fallback to keyword search
            return self._fallback_search(query, top_k)
    
    def _fallback_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Fallback keyword-based search when vector search is not available.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            logger.info("Using fallback keyword search")
            
            # Use local manual processor for keyword search
            if not self.manual_processor.sections:
                self.manual_processor.load_manual_data()
            
            matching_sections = self.manual_processor.search_sections_by_keywords(query)
            
            # Limit results and format
            results = []
            for i, section in enumerate(matching_sections[:top_k]):
                result = {
                    'section': section,
                    'metadata': {
                        'id': section.get('id'),
                        'category': section.get('category'),
                        'title': section.get('title'),
                        'keywords': section.get('keywords', [])
                    },
                    'similarity_score': 0.5,  # Default score for keyword matches
                    'rank': i + 1,
                    'search_type': 'keyword_fallback'
                }
                results.append(result)
            
            logger.info(f"Fallback search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in fallback search: {e}")
            return []
    
    def search_by_category(self, category: str, top_k: int = MAX_SEARCH_RESULTS) -> List[Dict[str, Any]]:
        """
        Search for sections within a specific category.
        
        Args:
            category: Category name (e.g., 'Engine', 'Brakes')
            top_k: Number of results to return
            
        Returns:
            List of sections in the specified category
        """
        try:
            # Load sections if not cached
            if self._sections_cache is None:
                if not self._load_data_from_s3():
                    # Use local data
                    if not self.manual_processor.sections:
                        self.manual_processor.load_manual_data()
                    sections = self.manual_processor.get_sections_by_category(category)
                else:
                    sections = [s for s in self._sections_cache if s.get('category') == category]
            else:
                sections = [s for s in self._sections_cache if s.get('category') == category]
            
            # Format results
            results = []
            for i, section in enumerate(sections[:top_k]):
                result = {
                    'section': section,
                    'metadata': {
                        'id': section.get('id'),
                        'category': section.get('category'),
                        'title': section.get('title'),
                        'keywords': section.get('keywords', [])
                    },
                    'similarity_score': 1.0,  # Perfect match for category
                    'rank': i + 1,
                    'search_type': 'category'
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} sections in category '{category}'")
            return results
            
        except Exception as e:
            logger.error(f"Error searching by category: {e}")
            return []
    
    def get_section_by_id(self, section_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific section by its ID.
        
        Args:
            section_id: Section identifier
            
        Returns:
            Section data or None if not found
        """
        try:
            # Load sections if not cached
            if self._sections_cache is None:
                if not self._load_data_from_s3():
                    if not self.manual_processor.sections:
                        self.manual_processor.load_manual_data()
                    return self.manual_processor.get_section_by_id(section_id)
            
            # Search in cached sections
            for section in self._sections_cache:
                if section.get('id') == section_id:
                    return section
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting section by ID: {e}")
            return None
    
    def get_available_categories(self) -> List[str]:
        """
        Get list of available categories.
        
        Returns:
            List of category names
        """
        try:
            if self._sections_cache is None:
                if not self._load_data_from_s3():
                    if not self.manual_processor.sections:
                        self.manual_processor.load_manual_data()
                    return self.manual_processor.get_categories()
            
            categories = set()
            for section in self._sections_cache:
                category = section.get('category')
                if category:
                    categories.add(category)
            
            return sorted(list(categories))
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get status of the search system components.
        
        Returns:
            Dictionary with system status information
        """
        status = {
            'search_service': 'operational',
            's3_connection': 'unknown',
            'embeddings_loaded': self._embeddings_cache is not None,
            'metadata_loaded': self._metadata_cache is not None,
            'sections_loaded': self._sections_cache is not None,
            'embedding_model': 'unknown',
            'total_sections': 0,
            'categories': []
        }
        
        try:
            # Check S3 connection
            s3_status = self.s3_service.check_connection()
            status['s3_connection'] = 'connected' if s3_status['connected'] else 'disconnected'
            status['s3_details'] = s3_status
            
            # Get embedding model info
            model_info = self.embedding_service.get_model_info()
            status['embedding_model'] = model_info.get('model_name', 'unknown')
            status['embedding_dimension'] = model_info.get('embedding_dimension', 0)
            
            # Get section count and categories
            if self._sections_cache:
                status['total_sections'] = len(self._sections_cache)
                status['categories'] = self.get_available_categories()
            elif self.manual_processor.sections:
                status['total_sections'] = len(self.manual_processor.sections)
                status['categories'] = self.manual_processor.get_categories()
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            status['error'] = str(e)
        
        return status
    
    def clear_cache(self):
        """Clear all cached data to force reload from S3."""
        self._embeddings_cache = None
        self._metadata_cache = None
        self._sections_cache = None
        logger.info("Cache cleared")

if __name__ == "__main__":
    # Test the search service
    search_service = SearchService()
    
    # Get system status
    status = search_service.get_system_status()
    print(f"System status: {status}")
    
    # Test search
    results = search_service.search("oil change", top_k=3)
    print(f"Search results for 'oil change': {len(results)} found")
    
    for result in results:
        print(f"- {result['metadata']['title']} (Score: {result['similarity_score']:.3f})")