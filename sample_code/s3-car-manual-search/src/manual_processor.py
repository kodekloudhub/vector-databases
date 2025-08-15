import json
import logging
from typing import List, Dict, Any
from config import LOCAL_MANUAL_FILE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ManualProcessor:
    """
    Processes car manual sections for embedding generation and search.
    """
    
    def __init__(self):
        self.sections = []
        
    def load_manual_data(self, file_path: str = LOCAL_MANUAL_FILE) -> List[Dict[str, Any]]:
        """
        Load car manual sections from JSON file.
        
        Args:
            file_path: Path to the manual data JSON file
            
        Returns:
            List of manual sections
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.sections = data.get('sections', [])
                logger.info(f"Loaded {len(self.sections)} manual sections")
                return self.sections
        except FileNotFoundError:
            logger.error(f"Manual data file not found: {file_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file: {e}")
            return []
    
    def get_sections_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all sections for a specific category.
        
        Args:
            category: Category name (e.g., 'Engine', 'Brakes')
            
        Returns:
            List of sections in the specified category
        """
        return [section for section in self.sections if section.get('category') == category]
    
    def get_section_by_id(self, section_id: str) -> Dict[str, Any]:
        """
        Get a specific section by its ID.
        
        Args:
            section_id: Unique section identifier
            
        Returns:
            Section data or empty dict if not found
        """
        for section in self.sections:
            if section.get('id') == section_id:
                return section
        return {}
    
    def prepare_text_for_embedding(self, section: Dict[str, Any]) -> str:
        """
        Prepare section text for embedding generation.
        Combines title, content, and keywords into a single text.
        
        Args:
            section: Manual section data
            
        Returns:
            Combined text for embedding
        """
        title = section.get('title', '')
        content = section.get('content', '')
        keywords = ' '.join(section.get('keywords', []))
        category = section.get('category', '')
        
        # Combine all text elements
        combined_text = f"{category}: {title}. {content} Keywords: {keywords}"
        return combined_text.strip()
    
    def get_all_texts_for_embedding(self) -> List[str]:
        """
        Get all section texts prepared for embedding generation.
        
        Returns:
            List of texts ready for embedding
        """
        if not self.sections:
            self.load_manual_data()
        
        texts = []
        for section in self.sections:
            text = self.prepare_text_for_embedding(section)
            texts.append(text)
        
        logger.info(f"Prepared {len(texts)} texts for embedding")
        return texts
    
    def get_section_metadata(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all sections (without content for storage efficiency).
        
        Returns:
            List of section metadata
        """
        metadata = []
        for section in self.sections:
            meta = {
                'id': section.get('id'),
                'category': section.get('category'),
                'title': section.get('title'),
                'keywords': section.get('keywords', [])
            }
            metadata.append(meta)
        
        return metadata
    
    def search_sections_by_keywords(self, query: str) -> List[Dict[str, Any]]:
        """
        Simple keyword-based search for fallback when embeddings are not available.
        
        Args:
            query: Search query
            
        Returns:
            List of matching sections
        """
        query_lower = query.lower()
        matching_sections = []
        
        for section in self.sections:
            # Check title, content, and keywords
            title = section.get('title', '').lower()
            content = section.get('content', '').lower()
            keywords = ' '.join(section.get('keywords', [])).lower()
            
            if (query_lower in title or 
                query_lower in content or 
                query_lower in keywords):
                matching_sections.append(section)
        
        return matching_sections
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories from the manual sections.
        
        Returns:
            List of category names
        """
        categories = set()
        for section in self.sections:
            category = section.get('category')
            if category:
                categories.add(category)
        
        return sorted(list(categories))
    
    def get_section_count_by_category(self) -> Dict[str, int]:
        """
        Get count of sections per category.
        
        Returns:
            Dictionary with category names and counts
        """
        category_counts = {}
        for section in self.sections:
            category = section.get('category', 'Unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return category_counts
    
    def validate_sections(self) -> Dict[str, Any]:
        """
        Validate the loaded manual sections for completeness.
        
        Returns:
            Validation report
        """
        if not self.sections:
            return {'valid': False, 'error': 'No sections loaded'}
        
        required_fields = ['id', 'category', 'title', 'content', 'keywords']
        validation_report = {
            'valid': True,
            'total_sections': len(self.sections),
            'missing_fields': [],
            'categories': self.get_categories(),
            'category_counts': self.get_section_count_by_category()
        }
        
        for i, section in enumerate(self.sections):
            for field in required_fields:
                if field not in section or not section[field]:
                    validation_report['missing_fields'].append(f"Section {i}: missing {field}")
                    validation_report['valid'] = False
        
        return validation_report

if __name__ == "__main__":
    # Test the manual processor
    processor = ManualProcessor()
    sections = processor.load_manual_data()
    
    print(f"Loaded {len(sections)} sections")
    print(f"Categories: {processor.get_categories()}")
    print(f"Category counts: {processor.get_section_count_by_category()}")
    
    # Test validation
    validation = processor.validate_sections()
    print(f"Validation: {validation}")
    
    # Test search
    results = processor.search_sections_by_keywords("oil change")
    print(f"Found {len(results)} sections for 'oil change'")