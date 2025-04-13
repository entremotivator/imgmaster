import streamlit as st
import requests
import base64

# --- Page Configuration ---
st.set_page_config(
    page_title="Custom 3D Toy Creator",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Initialize Session State ---
for key, default in {
    "api_key": "",
    "generated_image": None,
    "image_bytes": None,
    "prompt_built": "",
    "image_history": [],
    "reference_image": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- App Title & Description ---
st.title("🎨 Custom 3D Toy Creator")
st.markdown("""
Welcome to the **Custom 3D Toy Creator**!  
Design and generate a custom toy based on your ideas and an optional reference image.  
We'll create a visually rich, 3D-style toy mockup with custom packaging just for you!
""")
st.markdown("---")

# --- Sidebar Inputs ---
st.sidebar.title("🔐 OpenAI API Key")
st.sidebar.markdown("Your API key stays secure and private.")
st.session_state.api_key = st.sidebar.text_input(
    "Enter your OpenAI API Key", 
    type="password", 
    value=st.session_state.api_key
)

st.sidebar.title("🛠 Customize Your Toy")
with st.sidebar.form("toy_creator_form"):
    name = st.text_input("Toy Name (Top Label)", value="CRISTIANO RONALDO")
    role = st.text_input("Role / Occupation", value="FOOTBALLER")
    character_desc = st.text_input("Describe the character/person", value="Cristiano Ronaldo")
    expression = st.text_input("Facial expression or vibe", value="relaxed, friendly smile")
    accessories = st.text_input("Accessories (comma-separated)", value="football, shoes, world cup trophy")
    packaging_style = st.text_input("Packaging design style", value="minimalist, cardboard color, cute toy style")
    visual_style = st.text_input("Visual style", value="cartoon, cute but clean, similar to Mattel toys")
    brand_logo = st.text_input("Brand/logo", value="Mattel logo")
    reference_image = st.file_uploader("Upload reference image (optional)", type=["jpg", "jpeg", "png"])

    image_size = st.selectbox(
        "Image Size",
        options=["512x512", "1024x1024"],
        index=1
    )

    submitted = st.form_submit_button("✨ Generate Toy Image")

# --- Prompt Builder ---
def build_prompt():
    prompt = (
        f"Generate a 3D action figure toy inside clear blister packaging. "
        f"The toy should resemble {character_desc}, with a {expression}. "
        f"The packaging top label should say: “{name}”, and below that: “{role}”. "
        f"Add these accessories: {accessories}. "
        f"The packaging should follow a {packaging_style} style. "
        f"The visual tone is {visual_style}, and include the {brand_logo} in a top corner."
    )
    if st.session_state.reference_image:
        prompt += " Base the character’s appearance closely on the uploaded image."
    return prompt

# --- Image Generation Function ---
def generate_image(prompt, api_key, size):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
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
            error = response.json().get("error", {}).get("message", "Unknown error")
            st.error(f"Image generation failed: {error}")
            return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Form Submission Logic ---
if submitted:
    if not st.session_state.api_key.strip():
        st.error("🔑 Please enter your OpenAI API key to generate the image.")
    else:
        st.session_state.reference_image = reference_image
        prompt = build_prompt()
        st.session_state.prompt_built = prompt

        with st.spinner("🧠 Creating your toy image..."):
            image_data = generate_image(prompt, st.session_state.api_key, image_size)
            if image_data:
                st.session_state.image_bytes = image_data
                st.session_state.generated_image = image_data
                st.session_state.image_history.append({
                    "image": image_data,
                    "prompt": prompt,
                    "size": image_size
                })

# --- Display Uploaded Image ---
if st.session_state.reference_image and not submitted:
    st.subheader("📸 Uploaded Reference Image")
    st.image(st.session_state.reference_image, use_column_width=True)

# --- Display Generated Image ---
if st.session_state.generated_image:
    st.subheader("🧸 Your Custom 3D Toy")
    st.image(st.session_state.generated_image, use_column_width=True)

    b64 = base64.b64encode(st.session_state.generated_image).decode()
    st.markdown(f'<a href="data:image/png;base64,{b64}" download="custom_toy.png">📥 Download Image</a>', unsafe_allow_html=True)

# --- Display Image History ---
if st.session_state.image_history:
    with st.expander("📜 View Generated Image History"):
        for idx, item in enumerate(st.session_state.image_history):
            st.markdown(f"### Image #{idx + 1} - Size: {item['size']}")
            st.image(item["image"], use_column_width=True)
            with st.expander("🔍 View Prompt"):
                st.code(item["prompt"])
            b64_hist = base64.b64encode(item["image"]).decode()
            st.markdown(f'<a href="data:image/png;base64,{b64_hist}" download="custom_toy_{idx + 1}.png">📥 Download Image</a>', unsafe_allow_html=True)

# --- Clear History Option ---
if st.session_state.image_history:
    if st.button("🧹 Clear History"):
        st.session_state.image_history.clear()
        st.session_state.generated_image = None
        st.session_state.image_bytes = None
        st.experimental_rerun()
