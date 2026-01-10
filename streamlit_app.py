import streamlit as st
import requests
import json
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
import base64
import os

# Configuration
API_BASE_URL = "http://localhost:8000"  # Update this to your FastAPI server address

# Page configuration
st.set_page_config(
    page_title="Car Manual RAG System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}
if 'selected_manual_id' not in st.session_state:
    st.session_state.selected_manual_id = None
if 'query_type' not in st.session_state:
    st.session_state.query_type = "simple"

# Helper functions
def make_request(endpoint: str, method: str = "GET", data: Optional[dict] = None, files: Optional[dict] = None):
    """Make HTTP requests to the FastAPI backend."""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files)
            else:
                response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to the API server at {API_BASE_URL}. Make sure the FastAPI server is running.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e}")
        try:
            error_detail = response.json().get('detail', str(e))
            st.error(f"Details: {error_detail}")
        except:
            pass
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def list_manuals():
    """Get list of uploaded manuals."""
    return make_request("/api/manuals")

def upload_manual(file):
    """Upload a manual PDF."""
    files = {"file": (file.name, file, file.type)}
    return make_request("/api/manuals/upload", method="POST", files=files)

def delete_manual(manual_id: str):
    """Delete a manual."""
    return make_request(f"/api/manuals/{manual_id}", method="DELETE")

def process_manual(manual_id: str, start_page: int = 0, end_page: Optional[int] = None, process_images: bool = False):
    """Start manual processing."""
    data = {
        "start_page": start_page,
        "end_page": end_page,
        "process_images": process_images
    }
    return make_request(f"/api/manuals/{manual_id}/process", method="POST", data=data)

def get_processing_status(manual_id: str):
    """Get processing status."""
    return make_request(f"/api/manuals/{manual_id}/process/status")

def query_manual(question: str, manual_id: Optional[str] = None, top_k: int = 5, similarity_threshold: float = 0.7):
    """Query a manual."""
    data = {
        "question": question,
        "manual_id": manual_id,
        "top_k": top_k,
        "similarity_threshold": similarity_threshold,
        "include_sources": True
    }
    return make_request("/api/query", method="POST", data=data)

def filtered_query(question: str, manual_id: str, page_number: Optional[int] = None, section_header: Optional[str] = None, top_k: int = 5):
    """Query with filters."""
    data = {
        "question": question,
        "manual_id": manual_id,
        "page_number": page_number,
        "section_header": section_header,
        "top_k": top_k
    }
    return make_request("/api/query/filtered", method="POST", data=data)

def chat_with_manual(messages: List[Dict], manual_id: str, top_k: int = 5):
    """Chat with manual."""
    data = {
        "manual_id": manual_id,
        "messages": messages,
        "top_k": top_k
    }
    return make_request("/api/chat", method="POST", data=data)

# Sidebar for navigation
st.sidebar.title("🚗 Car Manual RAG System")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["📤 Upload Manual", "📚 Manage Manuals", "❓ Query Manual", "💬 Chat with Manual", "⚙️ Settings"]
)

# Main content based on page selection
if page == "📤 Upload Manual":
    st.title("Upload Car Manual PDF")
    st.markdown("---")
    
    with st.form("upload_form"):
        uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
        
        col1, col2 = st.columns(2)
        with col1:
            start_page = st.number_input("Start Page (optional)", min_value=0, value=0, step=1)
        with col2:
            end_page = st.number_input("End Page (optional)", min_value=0, value=None, step=1)
        
        process_images = st.checkbox("Extract and process images", value=False)
        
        submit_button = st.form_submit_button("Upload & Process")
        
        if submit_button and uploaded_file is not None:
            with st.spinner("Uploading manual..."):
                result = upload_manual(uploaded_file)
                
                if result:
                    manual_id = result.get('manual_id')
                    st.success(f"✅ Manual uploaded successfully! ID: {manual_id}")
                    
                    # Start processing
                    with st.spinner("Processing manual..."):
                        process_result = process_manual(
                            manual_id=manual_id,
                            start_page=start_page if start_page > 0 else None,
                            end_page=end_page if end_page else None,
                            process_images=process_images
                        )
                        
                        if process_result:
                            st.success("✅ Processing started in background!")
                            
                            # Show processing status
                            status = get_processing_status(manual_id)
                            if status:
                                st.info(f"Status: {status.get('status', 'Unknown')}")
                                st.info(f"Message: {status.get('message', '')}")

elif page == "📚 Manage Manuals":
    st.title("Manage Uploaded Manuals")
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Manuals"):
        st.rerun()
    
    # List manuals
    with st.spinner("Loading manuals..."):
        manuals = list_manuals()
    
    if manuals:
        # Create a DataFrame for better display
        manual_data = []
        for manual in manuals:
            manual_data.append({
                "ID": manual.get('manual_id', 'N/A'),
                "Filename": manual.get('filename', 'N/A'),
                "Uploaded": manual.get('uploaded_at', 'N/A'),
                "Processed": "✅" if manual.get('processed', False) else "❌",
                "Pages": manual.get('total_pages', 0),
                "Size": f"{manual.get('file_size_mb', 0):.2f} MB"
            })
        
        df = pd.DataFrame(manual_data)
        st.dataframe(df, use_container_width=True)
        
        # Manual selection and actions
        st.subheader("Manual Actions")
        col1, col2, col3 = st.columns(3)
        
        manual_ids = [m['ID'] for m in manual_data]
        selected_id = col1.selectbox("Select a manual:", manual_ids)
        
        with col2:
            if st.button("🗑️ Delete Manual", type="secondary"):
                if st.warning(f"Are you sure you want to delete manual {selected_id}? This action cannot be undone."):
                    with st.spinner("Deleting..."):
                        result = delete_manual(selected_id)
                        if result:
                            st.success(f"✅ Manual {selected_id} deleted!")
                            st.rerun()
        
        with col3:
            # Check if manual is processed
            selected_manual = next((m for m in manuals if m.get('manual_id') == selected_id), None)
            if selected_manual and not selected_manual.get('processed', False):
                if st.button("⚙️ Process Now"):
                    with st.spinner("Starting processing..."):
                        result = process_manual(selected_id)
                        if result:
                            st.success("✅ Processing started!")
                            st.rerun()
        
        # Show detailed info
        if selected_manual:
            st.subheader(f"Details: {selected_manual.get('filename')}")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Status", "Processed" if selected_manual.get('processed') else "Not Processed")
                st.metric("Pages", selected_manual.get('total_pages', 0))
            with col2:
                st.metric("File Size", f"{selected_manual.get('file_size_mb', 0):.2f} MB")
                st.metric("Upload Date", selected_manual.get('uploaded_at', 'N/A'))
            
            # Processing stats if available
            if selected_manual.get('processed') and selected_manual.get('processing_stats'):
                stats = selected_manual['processing_stats']
                st.subheader("Processing Statistics")
                cols = st.columns(4)
                cols[0].metric("Chunks", stats.get('chunks_created', 0))
                cols[1].metric("Embeddings", stats.get('embeddings_generated', 0))
                cols[2].metric("Total Pages", stats.get('total_pages', 0))
                cols[3].metric("Status", stats.get('status', 'completed'))
    else:
        st.info("No manuals uploaded yet. Go to the Upload page to add your first manual.")

elif page == "❓ Query Manual":
    st.title("Query Car Manual")
    st.markdown("---")
    
    # Get manuals list
    manuals = list_manuals()
    processed_manuals = [m for m in manuals if m.get('processed', False)] if manuals else []
    
    if not processed_manuals:
        st.warning("⚠️ No processed manuals found. Please upload and process a manual first.")
        st.info("Go to 'Manage Manuals' to process uploaded manuals.")
    else:
        # Manual selection
        manual_options = {m['filename']: m['manual_id'] for m in processed_manuals}
        selected_filename = st.selectbox("Select a manual:", list(manual_options.keys()))
        selected_manual_id = manual_options[selected_filename]
        
        # Store in session state
        st.session_state.selected_manual_id = selected_manual_id
        
        # Query type selection
        query_type = st.radio(
            "Query Type:",
            ["Simple Query", "Filtered Query"],
            horizontal=True
        )
        
        st.session_state.query_type = query_type
        
        # Query input
        question = st.text_area(
            "Enter your question:",
            placeholder="e.g., How do I change the oil? What's the tire pressure?",
            height=100
        )
        
        # Query parameters
        with st.expander("Advanced Settings", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                top_k = st.slider("Number of results (top_k)", 1, 20, 5)
                similarity_threshold = st.slider("Similarity threshold", 0.0, 1.0, 0.7, 0.05)
            with col2:
                if query_type == "Filtered Query":
                    page_number = st.number_input("Page number (optional)", min_value=0, value=None, step=1)
                    section_header = st.text_input("Section header (optional)", placeholder="e.g., Maintenance, Troubleshooting")
                else:
                    page_number = None
                    section_header = None
        
        # Query button
        if st.button("🔍 Query Manual", type="primary", disabled=not question.strip()):
            with st.spinner("Searching manual..."):
                if query_type == "Simple Query":
                    result = query_manual(
                        question=question,
                        manual_id=selected_manual_id,
                        top_k=top_k,
                        similarity_threshold=similarity_threshold
                    )
                else:  # Filtered Query
                    result = filtered_query(
                        question=question,
                        manual_id=selected_manual_id,
                        page_number=page_number if page_number else None,
                        section_header=section_header if section_header else None,
                        top_k=top_k
                    )
                
                if result:
                    # Display answer
                    st.subheader("Answer:")
                    st.markdown(f"**{result.get('answer', 'No answer found.')}**")
                    
                    # Display sources if available
                    if result.get('sources'):
                        st.subheader("📚 Sources:")
                        sources = result['sources']
                        
                        for i, source in enumerate(sources, 1):
                            with st.expander(f"Source {i} (Score: {source.get('similarity_score', 0):.3f})", expanded=i==1):
                                st.markdown(f"**Content:**")
                                st.write(source.get('content', 'No content'))
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Page:** {source.get('page_number', 'N/A')}")
                                with col2:
                                    st.write(f"**Section:** {source.get('section_header', 'N/A')}")
                                
                                if source.get('metadata'):
                                    st.write("**Metadata:**")
                                    st.json(source.get('metadata', {}))

elif page == "💬 Chat with Manual":
    st.title("Chat with Car Manual")
    st.markdown("---")
    
    # Get manuals list
    manuals = list_manuals()
    processed_manuals = [m for m in manuals if m.get('processed', False)] if manuals else []
    
    if not processed_manuals:
        st.warning("⚠️ No processed manuals found. Please upload and process a manual first.")
    else:
        # Manual selection
        manual_options = {m['filename']: m['manual_id'] for m in processed_manuals}
        selected_filename = st.selectbox("Select a manual:", list(manual_options.keys()), key="chat_manual_select")
        selected_manual_id = manual_options[selected_filename]
        
        # Initialize chat history for this manual
        if selected_manual_id not in st.session_state.chat_history:
            st.session_state.chat_history[selected_manual_id] = []
        
        # Display chat history
        st.subheader("Conversation")
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_history[selected_manual_id]:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    
                    # Show sources for assistant messages
                    if message["role"] == "assistant" and "sources" in message:
                        with st.expander("View Sources"):
                            for i, source in enumerate(message["sources"], 1):
                                st.write(f"**Source {i}:**")
                                st.write(source.get('content', '')[:200] + "...")
                                st.caption(f"Page: {source.get('page_number', 'N/A')}")
        
        # Chat input
        user_input = st.chat_input("Ask a question about the manual...")
        
        if user_input:
            # Add user message to chat
            st.session_state.chat_history[selected_manual_id].append({
                "role": "user",
                "content": user_input
            })
            
            # Display user message
            with st.chat_message("user"):
                st.write(user_input)
            
            # Prepare messages for API
            messages = st.session_state.chat_history[selected_manual_id]
            
            # Get response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = chat_with_manual(
                        messages=messages,
                        manual_id=selected_manual_id,
                        top_k=5
                    )
                    
                    if response:
                        answer = response.get('answer', '')
                        sources = response.get('sources', [])
                        
                        # Display answer
                        st.write(answer)
                        
                        # Add assistant message to chat history
                        st.session_state.chat_history[selected_manual_id].append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })
                        
                        # Show sources
                        if sources:
                            with st.expander("Sources"):
                                for i, source in enumerate(sources, 1):
                                    st.write(f"**Source {i}** (Score: {source.get('similarity_score', 0):.3f}):")
                                    st.write(source.get('content', '')[:300] + "...")
                                    st.caption(f"Page: {source.get('page_number', 'N/A')}")
                    else:
                        st.error("Failed to get response from the manual.")

        # Clear chat button
        if st.session_state.chat_history[selected_manual_id]:
            if st.button("🗑️ Clear Chat History", type="secondary"):
                st.session_state.chat_history[selected_manual_id] = []
                st.rerun()

elif page == "⚙️ Settings":
    st.title("Settings")
    st.markdown("---")
    
    st.subheader("API Configuration")
    
    # API URL configuration
    current_api_url = st.text_input(
        "API Base URL",
        value=API_BASE_URL,
        help="URL of your FastAPI server"
    )
    
    # Test connection
    if st.button("Test API Connection"):
        with st.spinner("Testing connection..."):
            try:
                response = requests.get(f"{current_api_url}/docs", timeout=5)
                if response.status_code == 200:
                    st.success("✅ API connection successful!")
                else:
                    st.error(f"❌ API returned status code: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
    
    st.markdown("---")
    st.subheader("About")
    
    st.markdown("""
    ### Car Manual RAG System
    
    This application allows you to:
    
    1. **Upload** car manual PDFs
    2. **Process** them to extract text and generate embeddings
    3. **Query** the manuals using natural language
    4. **Chat** with manuals in a conversational manner
    
    **Features:**
    - RAG (Retrieval-Augmented Generation) powered Q&A
    - Source citation and page references
    - Multi-turn conversations
    - Filtered queries by page/section
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")
st.sidebar.markdown("🟢 API: Connected" if manuals is not None else "🔴 API: Disconnected")

if manuals:
    total_manuals = len(manuals)
    processed_count = sum(1 for m in manuals if m.get('processed', False))
    st.sidebar.markdown(f"📚 Manuals: {total_manuals} ({processed_count} processed)")