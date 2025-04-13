import streamlit as st
import os
import json

# Set up page configuration
st.set_page_config(
    page_title="Segmind AI Toolkit",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        color: #FF4B4B;
        margin-bottom: 24px;
    }
    .feature-header {
        font-size: 24px;
        font-weight: bold;
        color: #0068C9;
        margin-top: 20px;
    }
    .feature-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .api-key-section {
        background-color: #ffffd0;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization for API key
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""
    
    # Try to load API key from config file
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                st.session_state['api_key'] = config.get('api_key', "")
        except:
            pass

# Main Header
st.markdown('<p class="main-header">👋 Welcome to Segmind AI Toolkit</p>', unsafe_allow_html=True)

# Introduction
st.markdown("""
This comprehensive application provides an intuitive interface to leverage 
**Segmind's powerful AI APIs** for creative and professional work.
""")

# API Key Section
st.markdown('<div class="api-key-section">', unsafe_allow_html=True)
st.subheader("🔑 API Configuration")

col1, col2 = st.columns([3, 1])

with col1:
    api_key = st.text_input(
        "Enter your Segmind API Key",
        value=st.session_state['api_key'],
        type="password",
        help="Your API key will be stored in session state and used across all tools"
    )
    
    if api_key != st.session_state['api_key']:
        st.session_state['api_key'] = api_key

with col2:
    if st.button("Save API Key"):
        # Save to config file
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_file, 'w') as f:
                json.dump({'api_key': st.session_state['api_key']}, f)
            st.success("API key saved!")
        except:
            st.error("Could not save API key permanently")

st.markdown("</div>", unsafe_allow_html=True)

# Features Overview
st.subheader("🛠️ Available Tools")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown('<p class="feature-header">🎬 Image & Video Generation</p>', unsafe_allow_html=True)
    st.markdown("""
    - **Kling 1.6 Image-to-Video**: Transform static images into dynamic videos
    - **SDXL Text-to-Image**: Generate high-quality images from text descriptions
    - **SD3 Text-to-Image**: Latest Stable Diffusion model for text-to-image
    - **Kandinsky Text-to-Image**: Alternative image generation model
    - **Image Variation Generator**: Create variations of existing images
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown('<p class="feature-header">🏠 Real Estate & Interior Design</p>', unsafe_allow_html=True)
    st.markdown("""
    - **DW Virtual Staging**: Stage empty rooms with virtual furniture
    - **Depth2Img Transformation**: Convert depth maps into realistic scenes
    - **RealESRGAN Upscaling**: Enhance low-resolution property images
    """)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown('<p class="feature-header">✏️ Image Editing & Manipulation</p>', unsafe_allow_html=True)
    st.markdown("""
    - **ControlNet Image Editing**: Edit images with advanced control
    - **Stable Inpainting**: Replace specific areas within images
    - **Mask Generator**: Create masks for selective editing
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown('<p class="feature-header">📊 Utilities & Monitoring</p>', unsafe_allow_html=True)
    st.markdown("""
    - **API Usage Monitor**: Track your API consumption and costs
    - **Batch Processing**: Process multiple images at once *(Coming Soon)*
    - **Custom Workflows**: Chain multiple API calls *(Coming Soon)*
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Getting Started
st.subheader("🚀 Getting Started")
st.markdown("""
1. Enter your Segmind API key in the box above
2. Navigate to your desired tool using the sidebar
3. Upload images or enter URLs and configure parameters
4. Generate amazing AI-powered content!

Need an API key? [Sign up on Segmind's website](https://segmind.com)
""")

# Useful resources
st.subheader("📚 Resources")
st.markdown("""
- [Segmind API Documentation](https://segmind.com/docs)
- [GitHub Repository](https://github.com/yourusername/segmind-toolkit)
- [Report Issues](https://github.com/yourusername/segmind-toolkit/issues)
""")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by [Your Name] | © 2025 | Version 2.0")
