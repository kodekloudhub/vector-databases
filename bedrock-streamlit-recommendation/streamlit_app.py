"""
Streamlit web application for Bedrock-based recommendation system
"""

import streamlit as st
import time
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional

from config import STREAMLIT_CONFIG, UAE_LOCATIONS, PRODUCT_CATEGORIES
from recommendation_engine import RecommendationEngine
from data_manager import DataManager

# Configure Streamlit page
st.set_page_config(
    page_title=STREAMLIT_CONFIG['page_title'],
    page_icon=STREAMLIT_CONFIG['page_icon'],
    layout=STREAMLIT_CONFIG['layout'],
    initial_sidebar_state=STREAMLIT_CONFIG['initial_sidebar_state']
)

# Initialize session state
if 'recommendation_engine' not in st.session_state:
    st.session_state.recommendation_engine = RecommendationEngine()
    st.session_state.data_manager = DataManager()

def display_header():
    """Display the main header"""
    st.title("🛍️ AI-Powered Recommendation System")
    st.markdown("### Powered by Amazon Bedrock & Streamlit")
    st.markdown("---")

def display_sidebar():
    """Display the sidebar with customer selection"""
    with st.sidebar:
        st.header("👤 Customer Selection")
        
        # Customer type selection
        customer_mode = st.radio(
            "Choose Customer Type:",
            ["Existing Customer", "New Customer"],
            help="Select whether to use an existing customer profile or create a new one"
        )
        
        if customer_mode == "Existing Customer":
            return display_existing_customer_selector()
        else:
            return display_new_customer_form()

def display_existing_customer_selector():
    """Display existing customer selector"""
    customers = st.session_state.data_manager.load_customers()
    
    if not customers:
        st.warning("No customers found. Please generate initial data first.")
        return None, None
    
    # Create customer options with names
    customer_options = {}
    for customer_id, customer_data in customers.items():
        metadata = customer_data.get('customer_metadata', {})
        name = metadata.get('name', customer_id)
        age = metadata.get('age', 'Unknown')
        location = metadata.get('location', 'Unknown')
        customer_options[f"{name} ({customer_id}) - {age}y, {location}"] = customer_id
    
    selected_display = st.selectbox(
        "Select Customer:",
        list(customer_options.keys()),
        help="Choose from existing customer profiles"
    )
    
    if selected_display:
        customer_id = customer_options[selected_display]
        customer_data = customers[customer_id]
        
        # Display customer info
        st.subheader("📋 Customer Profile")
        metadata = customer_data.get('customer_metadata', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Age", metadata.get('age', 'Unknown'))
            st.metric("Gender", metadata.get('gender', 'Unknown'))
        with col2:
            st.metric("Location", metadata.get('location', 'Unknown'))
            st.metric("Lifestyle", metadata.get('lifestyle', 'Unknown'))
        
        preferences = metadata.get('preferences', [])
        if preferences:
            st.write("**Preferences:**", ", ".join(preferences))
        
        price_sensitivity = metadata.get('price_sensitivity', 0.5)
        st.write(f"**Price Sensitivity:** {price_sensitivity:.1f} ({'Budget' if price_sensitivity > 0.7 else 'Premium' if price_sensitivity < 0.3 else 'Balanced'})")
        
        return "existing", customer_id
    
    return None, None

def display_new_customer_form():
    """Display new customer profile form"""
    st.subheader("✨ Create New Customer Profile")
    
    with st.form("new_customer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", placeholder="Enter customer name")
            age = st.slider("Age", 18, 65, 30)
            gender = st.selectbox("Gender", ["M", "F", "Other"])
            location = st.selectbox("Location", UAE_LOCATIONS)
        
        with col2:
            occupation = st.text_input("Occupation", placeholder="e.g., Software Engineer")
            lifestyle = st.selectbox("Lifestyle", [
                "Young Professional", "Family Man", "Student", "Entrepreneur",
                "Senior Executive", "Creative Professional", "Homemaker"
            ])
            price_sensitivity = st.slider(
                "Price Sensitivity", 
                0.0, 1.0, 0.5, 0.1,
                help="0 = Premium focused, 1 = Budget focused"
            )
        
        preferences = st.multiselect(
            "Product Preferences",
            list(PRODUCT_CATEGORIES.keys()),
            help="Select categories you're interested in"
        )
        
        submitted = st.form_submit_button("Get Recommendations")
        
        if submitted:
            if not name or not preferences:
                st.error("Please fill in name and select at least one preference.")
                return None, None
            
            customer_profile = {
                'name': name,
                'age': age,
                'gender': gender,
                'location': location,
                'occupation': occupation,
                'lifestyle': lifestyle,
                'preferences': preferences,
                'price_sensitivity': price_sensitivity
            }
            
            return "new", customer_profile
    
    return None, None

def display_recommendations(recommendations_data: Dict[str, Any]):
    """Display recommendations in the main area"""
    if not recommendations_data or not recommendations_data.get('recommendations'):
        st.warning("No recommendations available.")
        return
    
    recommendations = recommendations_data['recommendations']
    customer_type = recommendations_data.get('customer_type', 'unknown')
    fallback_used = recommendations_data.get('fallback_used', False)
    
    # Header with status
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("🎯 Your Recommendations")
    with col2:
        if fallback_used:
            st.warning("🔄 Fallback Used")
        else:
            st.success("✅ AI Generated")
    with col3:
        st.metric("Items Found", len(recommendations))
    
    # Explanation
    explanation = recommendations_data.get('explanation', '')
    if explanation:
        st.info(f"💡 **Why these products?** {explanation}")
    
    # Display recommendations as cards
    for i, rec in enumerate(recommendations):
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                # Product image placeholder
                st.image(
                    f"https://via.placeholder.com/150x150/4CAF50/white?text={rec.get('category', 'Product')[:3]}",
                    width=120
                )
            
            with col2:
                st.markdown(f"### {rec.get('product_name', 'Unknown Product')}")
                
                # Product details
                col2a, col2b = st.columns(2)
                with col2a:
                    st.write(f"**Category:** {rec.get('category', 'Unknown')}")
                    st.write(f"**Brand:** {rec.get('brand', 'Unknown')}")
                    if rec.get('rating'):
                        st.write(f"**Rating:** {'⭐' * int(rec.get('rating', 0))} ({rec.get('rating', 0)}/5)")
                
                with col2b:
                    st.write(f"**Price:** ${rec.get('price', 0):,.2f}")
                    st.write(f"**Match Score:** {rec.get('similarity_score', 0):.2%}")
                
                # Description
                description = rec.get('description', '')
                if description:
                    st.write(f"*{description}*")
                
                # Features
                features = rec.get('features', [])
                if features:
                    st.write("**Features:** " + " • ".join(features[:3]))
            
            with col3:
                # Action buttons
                if st.button(f"View Details", key=f"details_{i}"):
                    display_product_details(rec)
                
                if st.button(f"Add to Cart", key=f"cart_{i}"):
                    st.success("Added to cart! 🛒")
            
            st.markdown("---")

def display_product_details(product: Dict[str, Any]):
    """Display detailed product information in a modal-like container"""
    with st.expander(f"📦 {product.get('product_name', 'Product Details')}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Product ID:** {product.get('product_id', 'Unknown')}")
            st.write(f"**Category:** {product.get('category', 'Unknown')} > {product.get('subcategory', '')}")
            st.write(f"**Brand:** {product.get('brand', 'Unknown')}")
            st.write(f"**Price:** ${product.get('price', 0):,.2f}")
            st.write(f"**Rating:** {product.get('rating', 0)}/5 ⭐")
        
        with col2:
            st.write(f"**Match Score:** {product.get('similarity_score', 0):.2%}")
            if product.get('reason'):
                st.write(f"**Recommendation Reason:** {product.get('reason')}")
        
        description = product.get('description', '')
        if description:
            st.write(f"**Description:** {description}")
        
        features = product.get('features', [])
        if features:
            st.write("**Features:**")
            for feature in features:
                st.write(f"• {feature}")

def display_analytics_dashboard():
    """Display analytics dashboard"""
    st.header("📊 Analytics Dashboard")
    
    try:
        analytics_data = st.session_state.recommendation_engine.get_analytics_data()
        
        if not analytics_data:
            st.warning("No analytics data available.")
            return
        
        # System health
        col1, col2, col3 = st.columns(3)
        
        with col1:
            bedrock_status = analytics_data.get('system_health', {}).get('bedrock_connection', False)
            st.metric(
                "Bedrock Status", 
                "Connected" if bedrock_status else "Disconnected",
                delta="Healthy" if bedrock_status else "Check Connection"
            )
        
        with col2:
            data_integrity = analytics_data.get('system_health', {}).get('data_integrity', {})
            valid_count = sum(1 for v in data_integrity.values() if v)
            st.metric("Data Integrity", f"{valid_count}/3", delta="Files Valid")
        
        with col3:
            customer_count = analytics_data.get('customers', {}).get('total_customers', 0)
            st.metric("Total Customers", customer_count)
        
        # Customer analytics
        st.subheader("👥 Customer Analytics")
        customer_data = analytics_data.get('customers', {})
        
        if customer_data:
            col1, col2 = st.columns(2)
            
            with col1:
                # Age distribution
                age_dist = customer_data.get('age_distribution', {})
                if age_dist:
                    st.write("**Age Distribution**")
                    st.write(f"Average: {age_dist.get('mean', 0):.1f} years")
                    st.write(f"Range: {age_dist.get('min', 0):.0f} - {age_dist.get('max', 0):.0f}")
                
                # Gender distribution
                gender_dist = customer_data.get('gender_distribution', {})
                if gender_dist:
                    st.write("**Gender Distribution**")
                    for gender, count in gender_dist.items():
                        st.write(f"{gender}: {count}")
            
            with col2:
                # Location distribution
                location_dist = customer_data.get('location_distribution', {})
                if location_dist:
                    fig = px.pie(
                        values=list(location_dist.values()),
                        names=list(location_dist.keys()),
                        title="Customer Locations"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Product analytics
        st.subheader("🛍️ Product Analytics")
        product_data = analytics_data.get('products', {})
        
        if product_data:
            col1, col2 = st.columns(2)
            
            with col1:
                # Category distribution
                category_dist = product_data.get('category_distribution', {})
                if category_dist:
                    fig = px.bar(
                        x=list(category_dist.keys()),
                        y=list(category_dist.values()),
                        title="Products by Category"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Price distribution
                price_dist = product_data.get('price_distribution', {})
                if price_dist:
                    st.write("**Price Statistics**")
                    st.write(f"Average: ${price_dist.get('mean', 0):,.2f}")
                    st.write(f"Range: ${price_dist.get('min', 0):,.2f} - ${price_dist.get('max', 0):,.2f}")
                    st.write(f"Median: ${price_dist.get('50%', 0):,.2f}")
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

def display_system_status():
    """Display system status and controls"""
    with st.expander("⚙️ System Status & Controls"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Data"):
                st.session_state.recommendation_engine.refresh_cache()
                st.success("Data refreshed!")
        
        with col2:
            if st.button("📊 View Analytics"):
                st.session_state.show_analytics = True
        
        with col3:
            if st.button("💾 Backup Data"):
                try:
                    st.session_state.data_manager.backup_data()
                    st.success("Data backed up!")
                except Exception as e:
                    st.error(f"Backup failed: {str(e)}")
        
        # Data summary
        summary = st.session_state.data_manager.get_data_summary()
        st.json(summary)

def main():
    """Main application function"""
    display_header()
    
    # Sidebar for customer selection
    customer_type, customer_data = display_sidebar()
    
    # Main content area
    if customer_type and customer_data:
        # Get recommendations
        with st.spinner("🧠 Generating AI recommendations..."):
            start_time = time.time()
            
            if customer_type == "existing":
                recommendations_data = st.session_state.recommendation_engine.get_recommendations_for_existing_customer(customer_data)
            else:  # new customer
                recommendations_data = st.session_state.recommendation_engine.get_recommendations_for_new_customer(customer_data)
            
            processing_time = (time.time() - start_time) * 1000
            recommendations_data['processing_time_ms'] = processing_time
        
        # Display processing time
        st.success(f"✨ Recommendations generated in {processing_time:.0f}ms")
        
        # Display recommendations
        display_recommendations(recommendations_data)
        
        # Option to add new customer to system
        if customer_type == "new" and not recommendations_data.get('fallback_used', False):
            if st.button("💾 Save Customer Profile"):
                try:
                    customer_id = st.session_state.recommendation_engine.add_new_customer_to_system(customer_data)
                    st.success(f"Customer saved as {customer_id}!")
                except Exception as e:
                    st.error(f"Failed to save customer: {str(e)}")
    
    else:
        # Welcome screen
        st.markdown("""
        ## Welcome to the AI-Powered Recommendation System! 🎉
        
        This system uses **Amazon Bedrock** to provide personalized product recommendations:
        
        ### 🚀 Features:
        - **Existing Customers**: Get instant recommendations based on stored preferences
        - **New Customers**: Real-time AI analysis of your profile for personalized suggestions
        - **Smart Fallbacks**: Popular recommendations when similarity is low
        - **Detailed Explanations**: Understand why products were recommended
        
        ### 📋 How to Use:
        1. **Select Customer Type** in the sidebar
        2. **Choose an existing customer** or **create a new profile**
        3. **View your personalized recommendations** with explanations
        4. **Explore product details** and add items to cart
        
        ### 🛠️ Powered By:
        - **Amazon Bedrock Titan Embeddings** for understanding preferences
        - **Claude 3 Haiku** for generating explanations
        - **Streamlit** for the interactive interface
        
        👈 **Get started by selecting a customer type in the sidebar!**
        """)
    
    # Analytics dashboard (optional)
    if st.session_state.get('show_analytics', False):
        st.markdown("---")
        display_analytics_dashboard()
    
    # System status
    display_system_status()
    
    # Footer
    st.markdown("---")
    st.markdown("*Built with ❤️ using Amazon Bedrock, Streamlit, and AI*")

if __name__ == "__main__":
    main()