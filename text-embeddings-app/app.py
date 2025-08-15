"""
Text to Vector Converter - Simple App
A Streamlit application for converting text to numerical vectors.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from typing import List

# Import our embedding modules
from embeddings import TFIDFEmbedder, TransformerEmbedder

# Page configuration
st.set_page_config(
    page_title="Text to Vector Converter",
    page_icon="🔢",
    layout="wide"
)

# Cache functions for performance
@st.cache_data
def get_sample_texts():
    """Get sample texts for demonstration."""
    return [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is a subset of artificial intelligence.",
        "Natural language processing helps computers understand human language.",
        "Deep learning uses neural networks with multiple layers.",
        "Python is a popular programming language for data science.",
        "Streamlit makes it easy to create web applications.",
        "Text embeddings convert words into numerical vectors.",
        "Semantic similarity measures how related two texts are."
    ]

@st.cache_resource
def load_tfidf_model():
    """Load and cache TF-IDF model."""
    return TFIDFEmbedder()

@st.cache_resource
def load_transformer_model(model_name):
    """Load and cache Transformer model."""
    return TransformerEmbedder(model_name)

def create_visualization(embeddings_2d, texts, method_name):
    """Create interactive 2D visualization of embeddings."""
    df = pd.DataFrame({
        'x': embeddings_2d[:, 0],
        'y': embeddings_2d[:, 1],
        'text': texts,
        'index': range(len(texts))
    })
    
    fig = px.scatter(
        df, x='x', y='y',
        hover_data=['text'],
        title=f'2D Text Embeddings - {method_name}',
        labels={'x': 'First Principal Component', 'y': 'Second Principal Component'},
        color='index',
        color_continuous_scale='viridis'
    )
    
    fig.update_traces(
        marker=dict(size=12, line=dict(width=2, color='white')),
        hovertemplate='<b>Text:</b> %{customdata[0]}<br>' +
                      '<b>X:</b> %{x:.3f}<br>' +
                      '<b>Y:</b> %{y:.3f}<extra></extra>'
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def display_vector_table(embeddings_2d, texts):
    """Display embeddings in a formatted table."""
    df = pd.DataFrame({
        'Text': [text[:50] + '...' if len(text) > 50 else text for text in texts],
        'X Coordinate': embeddings_2d[:, 0].round(4),
        'Y Coordinate': embeddings_2d[:, 1].round(4),
        'Vector Magnitude': np.linalg.norm(embeddings_2d, axis=1).round(4)
    })
    
    return df

def main():
    """Main application function."""
    st.title("🔢 Text to Vector Converter")
    st.write("Convert text to numerical vectors using different embedding methods.")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Settings")
        
        # Method selection
        embedding_method = st.selectbox(
            "Choose Method",
            ["TF-IDF", "Sentence Transformers"]
        )
        
        # Model selection for transformers
        if embedding_method == "Sentence Transformers":
            selected_model = st.selectbox(
                "Choose AI Model",
                ['all-MiniLM-L6-v2']
            )
        
        # Sample text options
        st.subheader("Example Texts")
        use_samples = st.checkbox("Use example texts", value=True)
        
        if use_samples:
            sample_texts = get_sample_texts()
            selected_samples = st.multiselect(
                "Pick some texts to try",
                sample_texts,
                default=sample_texts[:4]
            )
    
    # Main content area with two columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Input Text")
        
        # Text input area
        if use_samples and selected_samples:
            input_texts = selected_samples
            st.success(f"Using {len(selected_samples)} example texts")
            for i, text in enumerate(selected_samples, 1):
                st.write(f"**{i}.** {text}")
        else:
            text_input = st.text_area(
                "Type your sentences here (one per line)",
                height=200,
                placeholder="Type some sentences like:\n\nI love pizza\nPizza is delicious\nI enjoy reading books\nBooks are educational"
            )
            
            if text_input.strip():
                input_texts = [line.strip() for line in text_input.split('\n') if line.strip()]
            else:
                input_texts = []
        
        # Convert button
        convert_button = st.button("Convert Text to Numbers!", type="primary", use_container_width=True)
    
    with col2:
        st.header("Vector Output")
        
        if convert_button and input_texts:
            if len(input_texts) < 2:
                st.warning("Please add at least 2 sentences!")
            else:
                with st.spinner(f"Converting your text to numbers..."):
                    try:
                        # Generate embeddings
                        if embedding_method == "TF-IDF":
                            embedder = load_tfidf_model()
                            embeddings_2d = embedder.fit_transform(input_texts)
                        else:
                            embedder = load_transformer_model(selected_model)
                            embeddings_2d = embedder.fit_transform(input_texts)
                        
                        # Success message
                        st.success("Success! Your text is now numbers!")
                        
                        # Visualization
                        st.subheader("2D Visualization")
                        fig = create_visualization(embeddings_2d, input_texts, embedding_method)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Vector table
                        st.subheader("Vector Values")
                        vector_df = display_vector_table(embeddings_2d, input_texts)
                        st.dataframe(vector_df, use_container_width=True)
                        
                        # Download
                        csv_data = vector_df.to_csv(index=False)
                        st.download_button(
                            "Download Results as CSV",
                            csv_data,
                            "text_vectors.csv",
                            "text/csv",
                            use_container_width=True
                        )
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        elif not input_texts and convert_button:
            st.warning("Please add some text first!")
        
        else:
            st.info("Ready to convert text to vectors!")

if __name__ == "__main__":
    main()