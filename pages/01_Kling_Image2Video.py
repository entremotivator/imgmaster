import streamlit as st
import sys
import os

# Add the root directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.common import get_api_key, get_image_input, make_segmind_api_request, show_result

st.set_page_config(page_title="Kling Image2Video | Segmind Toolkit", page_icon="🎬", layout="wide")

st.title("🎬 Kling 1.6: Image to Video")
st.markdown("Transform static images into dynamic, cinematic videos with Kling 1.6")

# Page layout
col1, col2 = st.columns([2, 1])

with col1:
    # Image Input
    st.subheader("Input Image")
    image_base64, image_preview = get_image_input("Select an image to animate")

with col2:
    # Parameters
    st.subheader("Animation Parameters")
    
    prompt = st.text_area(
        "Prompt", 
        "Breathtaking cinematic scene, dramatic lighting, highly detailed",
        help="Describe how you want the video to look and move"
    )
    
    negative_prompt = st.text_area(
        "Negative Prompt", 
        "Blurry, distorted, low quality, glitch, shaking, text, watermark, signature",
        help="Specify what you want to avoid in the animation"
    )
    
    advanced_options = st.expander("Advanced Options")
    
    with advanced_options:
        cfg_scale = st.slider(
            "CFG Scale", 
            0.0, 1.0, 0.5, 
            step=0.05,
            help="Controls how closely the result follows the prompt (higher = more faithful to prompt)"
        )
        
        mode = st.selectbox(
            "Quality Mode", 
            ["pro", "standard", "fast"],
            help="Pro: highest quality but slowest, Fast: lower quality but quickest"
        )
        
        fps = st.selectbox(
            "Frames Per Second",
            [24, 30, 60],
            index=0,
            help="Higher FPS results in smoother video but may reduce quality"
        )
        
        duration = st.slider(
            "Duration (seconds)", 
            1, 10, 4,
            help="Length of the generated video"
        )

# Generation section
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    generate_button = st.button("🎬 Generate Video", use_container_width=True)

if generate_button:
    if not image_base64:
        st.error("Please provide an image first.")
    else:
        # Prepare API payload
        payload = {
            "image": image_base64,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "mode": mode,
            "fps": fps,
            "duration": duration
        }
        
        # Make API request
        result, error = make_segmind_api_request("kling-1.6-image2video", payload)
        
        # Show result
        show_result(result, error, "mp4")

# Example Gallery
st.markdown("---")
st.subheader("📸 Example Animations")

# Display examples in a grid
example_col1, example_col2, example_col3 = st.columns(3)

with example_col1:
    st.markdown("**Nature Landscape**")
    st.image("https://placehold.co/600x400/png?text=Example+1")
    st.markdown("*Prompt: Serene mountain landscape, gentle wind, cinematic*")

with example_col2:
    st.markdown("**Portrait Animation**")
    st.image("https://placehold.co/600x400/png?text=Example+2")
    st.markdown("*Prompt: Professional portrait, subtle expressions, studio lighting*")

with example_col3:
    st.markdown("**Urban Scene**")
    st.image("https://placehold.co/600x400/png?text=Example+3")
    st.markdown("*Prompt: Busy city street, people walking, cars moving, rain*")

# Tips section
st.markdown("---")
st.subheader("💡 Tips for Best Results")
st.markdown("""
- Use high-quality, well-lit images with clear subjects
- Be specific in your prompt about the type of movement you want
- Avoid requesting extreme camera movements or zooms
- For portraits, subtle movements work best
- Longer durations may dilute the quality of the animation
""")
