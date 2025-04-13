import streamlit as st
import requests
import base64

# Configure page
st.set_page_config(
    page_title="Custom 3D Toy Creator",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None
if "prompt_built" not in st.session_state:
    st.session_state.prompt_built = ""
if "image_history" not in st.session_state:
    st.session_state.image_history = []
if "reference_image" not in st.session_state:
    st.session_state.reference_image = None

# Main app introduction
st.title("🎨 Custom 3D Toy Creator")
st.markdown("""
Welcome to the **Custom 3D Toy Creator**! This app lets you design and generate a unique toy image based on your input. 
Simply customize the toy's name, appearance, accessories, and packaging style, and we'll create a stunning visual representation of your idea.
""")
st.markdown("---")

# Sidebar: API key input
st.sidebar.title("🔐 OpenAI API Key")
st.sidebar.markdown("""
To generate images, please enter your OpenAI API key below. Your key will remain private and secure.
""")
st.session_state.api_key = st.sidebar.text_input(
    "Enter your OpenAI API Key", 
    type="password", 
    value=st.session_state.api_key
)

# Sidebar: Theme selection
theme = st.sidebar.radio("🌙 Theme", ["Light Mode", "Dark Mode"], index=0)
if theme == "Dark Mode":
    st.markdown(
        """
        <style>
        body {
            background-color: #2E2E2E;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Sidebar: Toy customization form
st.sidebar.title("🛠 Customize Your Toy")
with st.sidebar.form("toy_creator_form"):
    name = st.text_input("Toy Name (Top Label)", value="CRISTIANO RONALDO")
    role = st.text_input("Role / Occupation", value="FOOTBALLER")
    character_desc = st.text_input("Describe the character/person", value="Cristiano Ronaldo")
    expression = st.text_input("Facial expression or vibe", value="relaxed, friendly smile")
    accessories = st.text_input("Accessories (comma-separated)", value="football, shoes, world cup trophy")
    packaging_style = st.text_input("Packaging design style", value="minimalist, cardboard color, cute toy style sold in stores")
    visual_style = st.text_input("Visual style", value="cartoon, cute but still neat and clean, similar to Mattel toys")
    brand_logo = st.text_input("Brand/logo", value="Mattel logo")

    # Image uploader
    reference_image = st.file_uploader(
        "Upload reference image (optional)", 
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
        help="Upload an image for visual reference (max 200MB)"
    )

    # Image size selection
    image_size = st.selectbox(
        "Image Size",
        options=["512x512", "1024x1024"],
        index=1,
        help="Choose the resolution for your generated image."
    )

    submitted = st.form_submit_button("✨ Generate Toy Image")

# Function to build the prompt for image generation
def build_prompt():
    base_prompt = (
        f"Create a picture of a 3D action figure toy displayed inside transparent plastic blister packaging. "
        f"The toy resembles {character_desc}, styled with a {expression}. "
        f"At the top of the packaging, write in large letters: “{name}”, and below it, add “{role}”. "
        f"Include supporting accessories next to the figure, such as {accessories}. "
        f"The packaging design should be {packaging_style}. "
        f"The visual style is {visual_style}. "
        f"Add the {brand_logo} in the top corner of the packaging."
    )
    
    if reference_image:
        base_prompt += f" Use this uploaded image as visual reference: [USER UPLOADED IMAGE]"
    
    return base_prompt

# Function to generate an image using OpenAI's API
def generate_image(prompt, api_key, size):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": size
    }

    try:
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)

        if response.status_code == 200:
            image_url = response.json()["data"][0]["url"]
            image_response = requests.get(image_url)
            return image_response.content
        else:
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            st.error(f"Image generation failed: {error_message}")
            return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# Handle form submission and trigger image generation
if submitted:
    if not st.session_state.api_key.strip():
        st.error("Please enter your OpenAI API key.")
    else:
        # Save reference image to session state
        st.session_state.reference_image = reference_image
        
        # Build prompt based on user inputs
        st.session_state.prompt_built = build_prompt()
        
        # Generate image with spinner animation
        with st.spinner("🎨 Generating your custom toy..."):
            result = generate_image(st.session_state.prompt_built, st.session_state.api_key, image_size)
            if result:
                # Save generated image to session state for display and history
                st.session_state.image_bytes = result
                st.session_state.generated_image = result
                
                # Add to history
                st.session_state.image_history.append({
                    "image": result,
                    "prompt": st.session_state.prompt_built,
                    "size": image_size
                })

# Display reference image if uploaded
if st.session_state.reference_image and not submitted:
    st.subheader("📸 Uploaded Reference Image")
    st.image(st.session_state.reference_image, use_column_width=True)

# Display generated toy image (if available)
if st.session_state.generated_image:
    st.subheader("🧸 Your Custom 3D Toy")
    
    # Show generated image in app
    st.image(st.session_state.generated_image, use_column_width=True)
    
    # Provide download link for the image
    b64 = base64.b64encode(st.session_state.generated_image).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="custom_toy.png">📥 Download Image</a>'
    st.markdown(href, unsafe_allow_html=True)

# Display history of generated images (if any)
if len(st.session_state.image_history) > 0:
    with st.expander("📜 View Generated Image History"):
        for idx, item in enumerate(st.session_state.image_history):
            with st.container():
                st.markdown(f"### Image #{idx + 1} - Size: {item['size']}")
                b64_hist = base64.b64encode(item['image']).decode()
                href_hist = f'<a href="data:image/png;base64,{b64_hist}" download="custom_toy_{idx + 1}.png">📥 Download Image</a>'
                st.image(item["image"], use_column_width=True)
                if item["prompt"]:
                    with st.expander("🔍 View Prompt"):
                        st.code(item["prompt"])
                # Download link for historical images
                st.markdown(href_hist, unsafe_allow_html=True)

# Option to clear history
if len(st.session_state.image_history) > 0:
    if st.button("🧹 Clear History"):
        del st.session_state.image_history[:]
        st.session_state.generated_image = None
        st.session_state.image_bytes = None
        st.experimental_rerun()
