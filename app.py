import streamlit as st
import os
import importlib

st.set_page_config(page_title="Mega Content Suite", layout="wide")

st.title("🎬 Mega Content Suite")
st.markdown("### The Ultimate Creator's Toolkit — Powered by AI ⚡")

# Get all .py files in /page, ignoring __init__.py
page_dir = "page"
tool_modules = [
    f[:-3] for f in os.listdir(page_dir)
    if f.endswith(".py") and f != "__init__.py"
]

# Sidebar: tool selection
st.sidebar.title("🧰 Tools Menu")
selected_tool = st.sidebar.selectbox("Choose a tool to launch:", tool_modules)

# Dynamically import selected module
if selected_tool:
    try:
        module = importlib.import_module(f"page.{selected_tool}")
        if hasattr(module, "render"):
            st.subheader(f"🔧 {selected_tool.replace('_', ' ').title()}")
            module.render()
        else:
            st.warning(f"⚠️ `{selected_tool}.py` does not define a `render()` function.")
    except Exception as e:
        st.error(f"❌ Failed to load `{selected_tool}.py`: {e}")
