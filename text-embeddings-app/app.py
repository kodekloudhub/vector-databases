"""
Text to Vector Converter - Educational App v1
A simple Streamlit application for demonstrating how text becomes numerical vectors.
Perfect for teaching students about text embeddings.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from typing import List, Dict, Any
import json

# Import our embedding modules
from embeddings import TFIDFEmbedder, TransformerEmbedder

# Page configuration
st.set_page_config(
    page_title="Text to Vector Converter",
    page_icon="🔢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimalist design
def load_css():
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #2E86AB;
        --secondary-color: #A23B72;
        --accent-color: #F18F01;
        --background-color: #F8F9FA;
        --text-color: #2C3E50;
        --light-gray: #ECF0F1;
        --success-color: #27AE60;
        --warning-color: #F39C12;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom styling */
    .main-header {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .method-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid var(--primary-color);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: var(--light-gray);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .info-box {
        background: #E8F4FD;
        border: 1px solid var(--primary-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #D5F4E6;
        border: 1px solid var(--success-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #FEF9E7;
        border: 1px solid var(--warning-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--background-color);
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid var(--light-gray);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(46, 134, 171, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

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
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        title_font_size=16,
        title_x=0.5
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
    load_css()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔢 Text to Vector Converter</h1>
        <p>Learn how computers convert text into numbers that they can understand</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Method selection
        embedding_method = st.selectbox(
            "Choose Method",
            ["TF-IDF", "Sentence Transformers"],
            help="How should we convert text to numbers?"
        )
        
        # Model selection for transformers
        if embedding_method == "Sentence Transformers":
            selected_model = st.selectbox(
                "Choose AI Model",
                ['all-MiniLM-L6-v2'],  # Simplified to just one model for v1
                help="We'll use a fast, efficient AI model"
            )
        
        # Sample text options
        st.subheader("📝 Example Texts")
        use_samples = st.checkbox("Use example texts", value=True)
        
        if use_samples:
            sample_texts = get_sample_texts()
            selected_samples = st.multiselect(
                "Pick some texts to try",
                sample_texts,
                default=sample_texts[:4]
            )
        
        # Educational info
        st.markdown("---")
        st.subheader("🎓 What's happening?")
        st.write("1. You enter text")
        st.write("2. Computer converts to numbers")
        st.write("3. We show you the result!")
        st.write("4. Similar texts get similar numbers")
    
    # Main content area with two columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📝 Your Text")
        
        # Text input area
        if use_samples and selected_samples:
            input_texts = selected_samples
            st.success(f"✅ Using {len(selected_samples)} example texts")
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
        convert_button = st.button("🔢 Convert Text to Numbers!", type="primary", use_container_width=True)
        
        # Simple explanation
        if embedding_method == "TF-IDF":
            st.info("**TF-IDF** counts important words and makes them into numbers")
        else:
            st.info("**AI Model** understands meaning and converts to numbers")
    
    with col2:
        st.header("🔢 Your Numbers")
        
        if convert_button and input_texts:
            if len(input_texts) < 2:
                st.warning("⚠️ Please add at least 2 sentences to see the magic!")
            else:
                with st.spinner(f"🤖 Converting your text to numbers..."):
                    try:
                        # Generate embeddings
                        if embedding_method == "TF-IDF":
                            embedder = load_tfidf_model()
                            embeddings_2d = embedder.fit_transform(input_texts)
                        else:
                            embedder = load_transformer_model(selected_model)
                            embeddings_2d = embedder.fit_transform(input_texts)
                        
                        # Success message
                        st.success("🎉 **Success!** Your text is now numbers!")
                        
                        # Visualization
                        st.subheader("📍 See Your Text as Points")
                        fig = create_visualization(embeddings_2d, input_texts, embedding_method)
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption("💡 **Tip:** Similar texts appear close together!")
                        
                        # Vector table
                        st.subheader("🔢 The Actual Numbers")
                        vector_df = display_vector_table(embeddings_2d, input_texts)
                        st.dataframe(vector_df, use_container_width=True)
                        st.caption("Each sentence becomes 2 numbers (X and Y coordinates)")
                        
                        # Simple download
                        csv_data = vector_df.to_csv(index=False)
                        st.download_button(
                            "💾 Save Results as File",
                            csv_data,
                            "my_text_vectors.csv",
                            "text/csv",
                            use_container_width=True
                        )
                        
                        # Fun facts
                        st.subheader("🎯 Cool Facts")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Sentences Converted", len(input_texts))
                        with col_b:
                            st.metric("Method Used", embedding_method)
                    
                    except Exception as e:
                        st.error(f"❌ Oops! Something went wrong: {str(e)}")
                        st.info("💡 Try using simpler text or fewer sentences.")
        
        elif not input_texts and convert_button:
            st.warning("⚠️ Please add some text first!")
        
        else:
            # Show placeholder content
            st.info("""
            **👈 Ready to see the magic?**
            
            1. Choose some example texts or type your own
            2. Click the convert button
            3. Watch your text become numbers!
            
            **What you'll see:**
            - 📍 Your text as points on a map
            - 🔢 The exact numbers for each sentence
            - 💾 Option to save your results
            """)
    
    # Footer with simple educational content
    st.markdown("---")
    
    with st.expander("🎓 Learn More - How Does This Work?", expanded=False):
        st.markdown("""
        ### Why Turn Text Into Numbers?
        
        **Computers only understand numbers!**
        To work with text, we need to convert words into numbers that computers can process.
        
        **Two Methods We Use:**
        
        **🔤 TF-IDF Method:**
        - Counts how often words appear
        - Gives higher scores to rare, important words
        - Like highlighting the most important words in a sentence
        
        **🤖 AI Method (Sentence Transformers):**
        - Uses artificial intelligence to understand meaning
        - Knows that "happy" and "joyful" are similar
        - Much smarter but needs more computer power
        
        **Why Do Similar Texts Get Similar Numbers?**
        Because that's how we teach the computer! If two sentences mean similar things,
        they should get similar numbers. This helps computers understand that:
        - "I love cats" and "I adore cats" are very similar
        - "I love cats" and "I hate vegetables" are very different
        
        **Real-World Uses:**
        - Google Search (finding relevant websites)
        - Netflix recommendations (suggesting movies you might like)
        - Language translation (Google Translate)
        - Chatbots (understanding what you're asking)
        """)

if __name__ == "__main__":
    main()