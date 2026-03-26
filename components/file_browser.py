"""Workspace file browser component for sandbox file management."""

import streamlit as st
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
import os
import mimetypes

@dataclass
class FileInfo:
    name: str
    path: str
    size: int
    modified: float
    is_dir: bool
    mime_type: str = ""

# File type icons
FILE_ICONS = {
    'directory': '📁',
    'image': '🖼️',
    'code': '📄',
    'text': '📝',
    'data': '📊',
    'config': '⚙️',
    'executable': '⚡',
    'archive': '📦',
    'default': '📄'
}

CODE_EXTENSIONS = {'.py', '.js', '.ts', '.html', '.css', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.rb', '.php'}
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.ico', '.webp'}
DATA_EXTENSIONS = {'.json', '.csv', '.xml', '.yaml', '.yml', '.parquet', '.db', '.sqlite'}
CONFIG_EXTENSIONS = {'.conf', '.cfg', '.ini', '.env', '.toml'}
ARCHIVE_EXTENSIONS = {'.zip', '.tar', '.gz', '.bz2', '.7z', '.rar'}

def get_file_icon(filename: str, is_dir: bool) -> str:
    """Get appropriate icon for file type."""
    if is_dir:
        return FILE_ICONS['directory']
    
    ext = Path(filename).suffix.lower()
    
    if ext in CODE_EXTENSIONS:
        return FILE_ICONS['code']
    elif ext in IMAGE_EXTENSIONS:
        return FILE_ICONS['image']
    elif ext in DATA_EXTENSIONS:
        return FILE_ICONS['data']
    elif ext in CONFIG_EXTENSIONS:
        return FILE_ICONS['config']
    elif ext in ARCHIVE_EXTENSIONS:
        return FILE_ICONS['archive']
    elif ext in {'.sh', '.bat', '.exe'}:
        return FILE_ICONS['executable']
    else:
        return FILE_ICONS['default']

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def format_timestamp(timestamp: float) -> str:
    """Format timestamp in human-readable format."""
    from datetime import datetime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M")

def list_directory_contents(path: str) -> List[FileInfo]:
    """List directory contents with metadata."""
    try:
        target_path = Path(path).expanduser()
        
        if not target_path.exists():
            return []
        
        if not target_path.is_dir():
            return []
        
        contents = []
        
        # Add parent directory entry (except at root)
        if target_path.parent != target_path:
            contents.append(FileInfo(
                name="..",
                path=str(target_path.parent),
                size=0,
                modified=0,
                is_dir=True,
                mime_type=""
            ))
        
        # List directory contents
        for item in sorted(target_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            try:
                stat = item.stat()
                mime_type, _ = mimetypes.guess_type(str(item)) if not item.is_dir() else ("", None)
                
                contents.append(FileInfo(
                    name=item.name,
                    path=str(item),
                    size=stat.st_size,
                    modified=stat.st_mtime,
                    is_dir=item.is_dir(),
                    mime_type=mime_type or ""
                ))
            except (PermissionError, OSError):
                # Skip files we can't access
                continue
        
        return contents
        
    except Exception as e:
        st.error(f"Error reading directory: {e}")
        return []

def render_file_browser(
    base_path: str,
    on_file_select: Optional[Callable[[str], None]] = None,
    on_directory_change: Optional[Callable[[str], None]] = None,
    allow_upload: bool = True,
    allow_download: bool = True,
    show_hidden: bool = False
):
    """Render an interactive file browser component."""
    
    # Initialize session state for current path
    browser_key = f"file_browser_{base_path}"
    if browser_key not in st.session_state:
        st.session_state[browser_key] = {
            'current_path': base_path,
            'selected_files': []
        }
    
    current_path = st.session_state[browser_key]['current_path']
    
    # Header with current path
    st.subheader("📂 File Browser")
    
    # Breadcrumb navigation
    path_parts = Path(current_path).parts
    breadcrumb_cols = st.columns(len(path_parts) + 1)
    
    with breadcrumb_cols[0]:
        if st.button("🏠 Root", key=f"{browser_key}_root"):
            st.session_state[browser_key]['current_path'] = base_path
            if on_directory_change:
                on_directory_change(base_path)
            st.rerun()
    
    cumulative_path = ""
    for i, part in enumerate(path_parts):
        cumulative_path = os.path.join(cumulative_path, part) if cumulative_path else part
        with breadcrumb_cols[i + 1]:
            if st.button(part, key=f"{browser_key}_crumb_{i}"):
                st.session_state[browser_key]['current_path'] = cumulative_path
                if on_directory_change:
                    on_directory_change(cumulative_path)
                st.rerun()
    
    # Toolbar
    st.divider()
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        # Show current path
        st.code(current_path, language=None)
    
    with col2:
        if st.button("🔄 Refresh", key=f"{browser_key}_refresh"):
            st.rerun()
    
    with col3:
        show_hidden = st.checkbox("Show Hidden", value=show_hidden, key=f"{browser_key}_hidden")
    
    with col4:
        if allow_upload:
            with st.expander("⬆️ Upload", expanded=False):
                uploaded_file = st.file_uploader(
                    "Upload file",
                    key=f"{browser_key}_upload"
                )
                if uploaded_file:
                    save_path = Path(current_path) / uploaded_file.name
                    try:
                        with open(save_path, 'wb') as f:
                            f.write(uploaded_file.getvalue())
                        st.success(f"Uploaded {uploaded_file.name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Upload failed: {e}")
    
    # File listing
    st.divider()
    
    contents = list_directory_contents(current_path)
    
    if not contents:
        st.info("Directory is empty or inaccessible.")
    else:
        # Filter hidden files if needed
        if not show_hidden:
            contents = [f for f in contents if not f.name.startswith('.')]
        
        # Table header
        header_cols = st.columns([0.5, 3, 1, 1.5, 1.5])
        with header_cols[0]:
            st.write("**Icon**")
        with header_cols[1]:
            st.write("**Name**")
        with header_cols[2]:
            st.write("**Size**")
        with header_cols[3]:
            st.write("**Modified**")
        with header_cols[4]:
            st.write("**Actions**")
        
        st.divider()
        
        # File rows
        for file_info in contents:
            row_cols = st.columns([0.5, 3, 1, 1.5, 1.5])
            
            with row_cols[0]:
                st.write(get_file_icon(file_info.name, file_info.is_dir))
            
            with row_cols[1]:
                if file_info.is_dir:
                    # Directory - clickable to navigate
                    if st.button(
                        f"📁 {file_info.name}",
                        key=f"{browser_key}_dir_{file_info.name}",
                        use_container_width=True
                    ):
                        new_path = os.path.join(current_path, file_info.name) if file_info.name != ".." else file_info.path
                        st.session_state[browser_key]['current_path'] = new_path
                        if on_directory_change:
                            on_directory_change(new_path)
                        st.rerun()
                else:
                    # File - clickable to select
                    file_label = f"{get_file_icon(file_info.name, False)} {file_info.name}"
                    if st.button(
                        file_label,
                        key=f"{browser_key}_file_{file_info.name}",
                        use_container_width=True
                    ):
                        if on_file_select:
                            on_file_select(file_info.path)
            
            with row_cols[2]:
                if file_info.is_dir:
                    st.write("-")
                else:
                    st.write(format_file_size(file_info.size))
            
            with row_cols[3]:
                if file_info.modified:
                    st.write(format_timestamp(file_info.modified))
                else:
                    st.write("-")
            
            with row_cols[4]:
                if not file_info.is_dir and allow_download:
                    try:
                        with open(file_info.path, 'rb') as f:
                            file_data = f.read()
                        st.download_button(
                            "⬇️",
                            data=file_data,
                            file_name=file_info.name,
                            mime=file_info.mime_type or "application/octet-stream",
                            key=f"{browser_key}_dl_{file_info.name}",
                            use_container_width=True
                        )
                    except Exception:
                        st.write("-")
                else:
                    st.write("-")
        
        st.divider()
        
        # Summary
        dirs = sum(1 for f in contents if f.is_dir and f.name != "..")
        files = sum(1 for f in contents if not f.is_dir)
        st.caption(f"📁 {dirs} directories | 📄 {files} files")

def render_workspace_browser_card(sandbox_id: str, workspace_path: str):
    """Render a file browser card for a specific sandbox workspace."""
    with st.expander(f"📂 Workspace Browser: {sandbox_id}", expanded=False):
        if not workspace_path:
            st.warning("No workspace path configured for this sandbox.")
            return
        
        render_file_browser(
            base_path=workspace_path,
            allow_upload=True,
            allow_download=True,
            show_hidden=False
        )
