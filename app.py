import streamlit as st
import os
import importlib.util

st.set_page_config(page_title="Mega Content Suite", layout="wide")

st.title("🎬 Mega Content Suite")
st.markdown("### The Ultimate Creator's Toolkit — Powered by AI ⚡")

# Discover available tools in /page
page_dir = "page"
tools = {
    filename[:-3]: os.path.join(page_dir, filename)
    for filename in sorted(os.listdir(page_dir))
    if filename.endswith(".py")
}

# Sidebar for tool selection
st.sidebar.title("🧰 Tools Menu")
selected_tool = st.sidebar.selectbox("Choose a tool to launch:", list(tools.keys()))

# Load selected tool dynamically
if selected_tool:
    module_path = tools[selected_tool]
    spec = importlib.util.spec_from_file_location(selected_tool, module_path)
    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
        if hasattr(module, "render"):
            st.subheader(f"🔧 {selected_tool.replace('_', ' ').title()}")
            module.render()
        else:
            st.warning(f"⚠️ `{selected_tool}.py` does not define a `render()` function.")
    except Exception as e:
        st.error(f"❌ Failed to load `{selected_tool}.py`: {e}")
