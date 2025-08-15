import streamlit as st
import sys
import os
from pathlib import Path
import logging
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent))

from src.search_service import SearchService
from config import APP_TITLE, APP_DESCRIPTION, SAMPLE_QUERIES, MANUAL_CATEGORIES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Car Manual Search",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'search_service' not in st.session_state:
    st.session_state.search_service = None
if 'system_status' not in st.session_state:
    st.session_state.system_status = None

@st.cache_resource
def initialize_search_service():
    """Initialize the search service (cached to avoid reloading)."""
    try:
        search_service = SearchService()
        return search_service
    except Exception as e:
        st.error(f"Error initializing search service: {e}")
        return None

def display_search_result(result: Dict[str, Any], rank: int):
    """Display a single search result."""
    section = result['section']
    metadata = result['metadata']
    similarity_score = result.get('similarity_score', 0)
    search_type = result.get('search_type', 'vector')
    
    # Create expandable section for each result
    with st.expander(f"#{rank} - {metadata['title']} ({metadata['category']}) - Score: {similarity_score:.3f}"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**Category:** {metadata['category']}")
            st.markdown(f"**Section ID:** {metadata['id']}")
            
            # Display content
            st.markdown("**Procedure:**")
            st.write(section['content'])
            
            # Display keywords
            if metadata.get('keywords'):
                st.markdown("**Keywords:**")
                keywords_str = ", ".join(metadata['keywords'])
                st.markdown(f"`{keywords_str}`")
        
        with col2:
            # Display metadata
            st.markdown("**Details:**")
            st.markdown(f"Similarity: {similarity_score:.3f}")
            st.markdown(f"Search Type: {search_type}")
            
            # Color-code by category
            category_colors = {
                'Engine': '🔴',
                'Brakes': '🟠', 
                'Electrical': '🟡',
                'Transmission': '🟢',
                'Suspension': '🔵',
                'AC/Heating': '🟣',
                'Fuel System': '🟤',
                'Exhaust': '⚫',
                'Cooling System': '🔵',
                'Steering': '🟢'
            }
            
            category_icon = category_colors.get(metadata['category'], '⚪')
            st.markdown(f"{category_icon} {metadata['category']}")

def display_system_status():
    """Display system status in the sidebar."""
    if st.session_state.search_service:
        status = st.session_state.search_service.get_system_status()
        st.session_state.system_status = status
        
        st.sidebar.markdown("### System Status")
        
        # Connection status
        s3_connected = status.get('s3_connection') == 'connected'
        s3_icon = "✅" if s3_connected else "❌"
        st.sidebar.markdown(f"{s3_icon} S3 Connection")
        
        # Data status
        embeddings_loaded = status.get('embeddings_loaded', False)
        embeddings_icon = "✅" if embeddings_loaded else "❌"
        st.sidebar.markdown(f"{embeddings_icon} Embeddings Loaded")
        
        sections_loaded = status.get('sections_loaded', False)
        sections_icon = "✅" if sections_loaded else "❌"
        st.sidebar.markdown(f"{sections_icon} Manual Data Loaded")
        
        # Statistics
        total_sections = status.get('total_sections', 0)
        st.sidebar.markdown(f"📚 Total Sections: {total_sections}")
        
        categories = status.get('categories', [])
        st.sidebar.markdown(f"📂 Categories: {len(categories)}")
        
        # Model info
        model_name = status.get('embedding_model', 'Unknown')
        if model_name != 'Unknown':
            st.sidebar.markdown(f"🤖 Model: {model_name.split('/')[-1]}")

def main():
    """Main Streamlit application."""
    
    # Header
    st.title(APP_TITLE)
    st.markdown(APP_DESCRIPTION)
    
    # Initialize search service
    if st.session_state.search_service is None:
        with st.spinner("Initializing search service..."):
            st.session_state.search_service = initialize_search_service()
    
    if st.session_state.search_service is None:
        st.error("Failed to initialize search service. Please check your configuration.")
        st.stop()
    
    # Sidebar
    st.sidebar.title("🔧 Search Options")
    
    # Display system status
    display_system_status()
    
    # Search mode selection
    st.sidebar.markdown("### Search Mode")
    search_mode = st.sidebar.radio(
        "Choose search mode:",
        ["🔍 Text Search", "📂 Browse by Category", "📋 View All Sections"]
    )
    
    # Main content area
    if search_mode == "🔍 Text Search":
        st.header("Search Car Manual")
        
        # Search input
        col1, col2 = st.columns([4, 1])
        
        with col1:
            query = st.text_input(
                "Enter your search query:",
                placeholder="e.g., 'oil change', 'brake noise', 'engine won't start'",
                help="Describe the problem or procedure you're looking for"
            )
        
        with col2:
            search_button = st.button("🔍 Search", type="primary")
        
        # Sample queries
        st.markdown("**Quick searches:**")
        sample_cols = st.columns(len(SAMPLE_QUERIES[:5]))
        
        for i, sample_query in enumerate(SAMPLE_QUERIES[:5]):
            with sample_cols[i]:
                if st.button(sample_query, key=f"sample_{i}"):
                    query = sample_query
                    search_button = True
        
        # Perform search
        if (search_button and query) or (query and len(query) > 2):
            with st.spinner(f"Searching for '{query}'..."):
                results = st.session_state.search_service.search(query, top_k=5)
            
            if results:
                st.success(f"Found {len(results)} relevant results:")
                
                # Display results
                for i, result in enumerate(results, 1):
                    display_search_result(result, i)
                
                # Search tips
                with st.expander("💡 Search Tips"):
                    st.markdown("""
                    - Use specific terms like "oil change" or "brake noise"
                    - Describe symptoms: "engine won't start", "grinding noise"
                    - Include system names: "transmission", "electrical", "cooling"
                    - Try different phrasings if you don't find what you need
                    """)
            else:
                st.warning("No results found. Try different keywords or browse by category.")
    
    elif search_mode == "📂 Browse by Category":
        st.header("Browse by Category")
        
        # Get available categories
        categories = st.session_state.search_service.get_available_categories()
        
        if categories:
            # Category selection
            selected_category = st.selectbox(
                "Select a category:",
                categories,
                help="Choose a system category to view all related procedures"
            )
            
            if selected_category:
                with st.spinner(f"Loading {selected_category} procedures..."):
                    results = st.session_state.search_service.search_by_category(
                        selected_category, top_k=10
                    )
                
                if results:
                    st.success(f"Found {len(results)} procedures in {selected_category}:")
                    
                    # Display results
                    for i, result in enumerate(results, 1):
                        display_search_result(result, i)
                else:
                    st.warning(f"No procedures found in {selected_category}")
        else:
            st.error("No categories available. Please check the system status.")
    
    elif search_mode == "📋 View All Sections":
        st.header("All Manual Sections")
        
        # Get system status for section count
        status = st.session_state.system_status or st.session_state.search_service.get_system_status()
        total_sections = status.get('total_sections', 0)
        categories = status.get('categories', [])
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sections", total_sections)
        with col2:
            st.metric("Categories", len(categories))
        with col3:
            embedding_model = status.get('embedding_model', 'Unknown')
            st.metric("Embedding Model", embedding_model.split('/')[-1] if embedding_model != 'Unknown' else 'Unknown')
        
        # Category breakdown
        if categories:
            st.markdown("### Categories Overview")
            
            # Create columns for categories
            cols = st.columns(min(3, len(categories)))
            
            for i, category in enumerate(categories):
                with cols[i % 3]:
                    if st.button(f"📂 {category}", key=f"cat_overview_{i}"):
                        # Switch to category browse mode
                        st.session_state.browse_category = category
                        st.rerun()
        
        # System details
        with st.expander("🔧 System Details"):
            st.json(status)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🔧 **Car Manual Search System** - Powered by AWS S3 Vector Storage and sentence-transformers"
    )
    
    # Refresh button in sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Refresh System Status"):
        st.session_state.search_service.clear_cache()
        st.rerun()

if __name__ == "__main__":
    main()