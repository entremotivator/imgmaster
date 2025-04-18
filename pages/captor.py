import streamlit as st
from PIL import Image
import openai
import io

# Replace with your OpenAI API Key
openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-api-key-here")

# Placeholder for Kling image generation function
def generate_kling_image(prompt, image):
    # Simulated image generation
    img = Image.new("RGB", (512, 512), color="lightblue")
    return img

# Actual DALL·E generation function
def generate_dalle_image(prompt):
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response["data"][0]["url"]
        return image_url
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None

# App UI
st.set_page_config(page_title="Capsule Pic Generator", layout="centered")
st.title("📸 Chibi Capsule Pic Generator")

st.sidebar.header("🧠 Generation Settings")
model_choice = st.sidebar.radio("Choose AI Model", ["OpenAI DALL·E 3", "Kling (Simulated)"])

# Image Upload
uploaded_image = st.file_uploader("📷 Upload a photo of yourself", type=["png", "jpg", "jpeg"])

# Form for customization
with st.form("capsule_form"):
    st.subheader("🎨 Customize Your Capsule")
    hoodie_desc = st.text_input("Hoodie Description", "LB hoodie")
    jeans_desc = st.text_input("Jeans Description", "blue Levi Jeans")
    hat_desc = st.text_input("Hat Description", 'beige hat with the “LB” logo')
    accessory = st.text_input("Accessory", "holding an iPhone")
    submitted = st.form_submit_button("Generate Capsule Pic")

# Process generation
if submitted and uploaded_image:
    with st.spinner("🌀 Generating your capsule..."):
        image = Image.open(uploaded_image)

        # Construct prompt
        prompt = f"""
        Generate a portrait image of a detailed, all-glass gashapon capsule,
        held between two fingers. Inside the capsule is a miniature version
        of the person in the uploaded photo, chibi-style, life-size.
        The chibi is wearing: {hoodie_desc}, {jeans_desc}, {hat_desc}, and {accessory}.
        """

        if model_choice == "Kling (Simulated)":
            result_image = generate_kling_image(prompt, image)
            st.image(result_image, caption="🎉 Your Chibi Capsule Pic", use_column_width=True)

        elif model_choice == "OpenAI DALL·E 3":
            dalle_url = generate_dalle_image(prompt)
            if dalle_url:
                st.image(dalle_url, caption="🎉 Your Chibi Capsule Pic (DALL·E 3)", use_column_width=True)

elif submitted and not uploaded_image:
    st.warning("Please upload a photo to continue.")

st.markdown("---")
st.markdown("Created with 💙 using Streamlit, OpenAI DALL·E, and Kling.")

