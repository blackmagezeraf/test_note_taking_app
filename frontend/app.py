import streamlit as st
import requests

API_URL = "http://backend:8000"   # Docker service name

st.set_page_config(page_title="Notes App", layout="wide")
st.title("📝 Notes with Markdown")

# Sidebar: list notes
with st.sidebar:
    st.header("Notes")
    try:
        response = requests.get(f"{API_URL}/notes")
        if response.status_code == 200:
            notes = response.text.splitlines()
            selected = st.selectbox("Select a note", notes, index=0 if notes else None)
        else:
            st.error("Could not load notes")
            notes = []
            selected = None
    except Exception as e:
        st.error(f"Backend not reachable: {e}")
        notes = []
        selected = None

    # Delete button
    if selected and st.button("Delete Note"):
        resp = requests.delete(f"{API_URL}/notes/{selected}")
        if resp.status_code == 200:
            st.success("Deleted")
            st.rerun()
        else:
            st.error("Delete failed")

# Main area
col1, col2 = st.columns(2)

with col1:
    st.subheader("Create / Edit")
    title = st.text_input("Title", key="title")
    content = st.text_area("Content (Markdown)", height=300, key="content")
    if st.button("Create Note"):
        if title:
            resp = requests.post(f"{API_URL}/notes/{title}", json={"title": title, "content": content})
            if resp.status_code == 201:
                st.success("Note created")
                st.rerun()
            elif resp.status_code == 409:
                st.error("Note already exists")
            else:
                st.error("Create failed")
    if selected and st.button("Update Note"):
        resp = requests.put(f"{API_URL}/notes/{selected}", json={"content": content})
        if resp.status_code == 200:
            st.success("Updated")
            st.rerun()
        else:
            st.error("Update failed")

with col2:
    st.subheader("Preview")
    if selected:
        try:
            resp = requests.get(f"{API_URL}/notes/{selected}")
            if resp.status_code == 200:
                st.markdown(resp.text)
            else:
                st.warning("Note not found")
        except Exception as e:
            st.error(f"Could not load note: {e}")
    else:
        st.info("Select a note from the sidebar")