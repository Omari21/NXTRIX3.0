"""
Advanced Document Management System for NXTRIX CRM
Handles property photos, documents, and file organization
"""

import streamlit as st
import os
import shutil
import mimetypes
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import sqlite3
from PIL import Image
import io
import base64

@dataclass
class DocumentInfo:
    """Document information structure"""
    id: str
    deal_id: str
    filename: str
    file_type: str
    file_size: int
    category: str
    tags: List[str]
    uploaded_by: str
    uploaded_at: datetime
    file_path: str
    thumbnail_path: Optional[str] = None
    description: str = ""
    is_public: bool = True

class DocumentManager:
    """Advanced document management system"""
    
    def __init__(self, db_path: str = "crm_data.db", storage_path: str = "deal_documents"):
        self.db_path = db_path
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.init_database()
        
    def init_database(self):
        """Initialize document database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    deal_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT,
                    uploaded_by TEXT NOT NULL,
                    uploaded_at TIMESTAMP NOT NULL,
                    file_path TEXT NOT NULL,
                    thumbnail_path TEXT,
                    description TEXT,
                    is_public BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_categories (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    icon TEXT,
                    color TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default categories
            default_categories = [
                ('photos', 'Property Photos', 'Photos of the property', '📸', '#4CAF50'),
                ('contracts', 'Contracts & Legal', 'Purchase agreements, contracts', '📋', '#2196F3'),
                ('inspections', 'Inspections & Reports', 'Inspection reports, appraisals', '🔍', '#FF9800'),
                ('financial', 'Financial Documents', 'Bank statements, pre-approval', '💰', '#9C27B0'),
                ('permits', 'Permits & Licenses', 'Building permits, licenses', '📜', '#607D8B'),
                ('marketing', 'Marketing Materials', 'Flyers, listing photos', '📊', '#E91E63'),
                ('misc', 'Miscellaneous', 'Other documents', '📁', '#757575')
            ]
            
            for cat_id, name, desc, icon, color in default_categories:
                cursor.execute('''
                    INSERT OR IGNORE INTO document_categories 
                    (id, name, description, icon, color) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (cat_id, name, desc, icon, color))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error initializing document database: {e}")
    
    def upload_document(self, uploaded_file, deal_id: str, category: str, 
                       tags: List[str] = None, description: str = "",
                       uploaded_by: str = "current_user") -> Optional[DocumentInfo]:
        """Upload and process a document"""
        try:
            if uploaded_file is None:
                return None
            
            # Generate unique ID and paths
            doc_id = hashlib.md5(f"{deal_id}_{uploaded_file.name}_{datetime.now()}".encode()).hexdigest()
            file_extension = Path(uploaded_file.name).suffix.lower()
            safe_filename = f"{doc_id}_{uploaded_file.name}"
            
            # Create deal-specific directory
            deal_dir = self.storage_path / deal_id
            deal_dir.mkdir(exist_ok=True)
            
            # Save file
            file_path = deal_dir / safe_filename
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            
            # Create thumbnail for images
            thumbnail_path = None
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                thumbnail_path = self._create_thumbnail(file_path, deal_dir)
            
            # Create document info
            doc_info = DocumentInfo(
                id=doc_id,
                deal_id=deal_id,
                filename=uploaded_file.name,
                file_type=file_extension,
                file_size=uploaded_file.size,
                category=category,
                tags=tags or [],
                uploaded_by=uploaded_by,
                uploaded_at=datetime.now(),
                file_path=str(file_path),
                thumbnail_path=thumbnail_path,
                description=description
            )
            
            # Save to database
            self._save_document_to_db(doc_info)
            
            return doc_info
            
        except Exception as e:
            st.error(f"Error uploading document: {e}")
            return None
    
    def _create_thumbnail(self, image_path: Path, output_dir: Path) -> Optional[str]:
        """Create thumbnail for image files"""
        try:
            thumbnail_path = output_dir / f"thumb_{image_path.name}"
            
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(thumbnail_path, 'JPEG', quality=85)
                
            return str(thumbnail_path)
            
        except Exception as e:
            st.warning(f"Could not create thumbnail: {e}")
            return None
    
    def _save_document_to_db(self, doc_info: DocumentInfo):
        """Save document information to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO documents 
                (id, deal_id, filename, file_type, file_size, category, tags, 
                 uploaded_by, uploaded_at, file_path, thumbnail_path, description, is_public)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_info.id,
                doc_info.deal_id,
                doc_info.filename,
                doc_info.file_type,
                doc_info.file_size,
                doc_info.category,
                json.dumps(doc_info.tags),
                doc_info.uploaded_by,
                doc_info.uploaded_at,
                doc_info.file_path,
                doc_info.thumbnail_path,
                doc_info.description,
                doc_info.is_public
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error saving document to database: {e}")
    
    def get_documents(self, deal_id: str = None, category: str = None) -> List[DocumentInfo]:
        """Retrieve documents with optional filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM documents WHERE 1=1"
            params = []
            
            if deal_id:
                query += " AND deal_id = ?"
                params.append(deal_id)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY uploaded_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            documents = []
            for row in rows:
                doc = DocumentInfo(
                    id=row[0],
                    deal_id=row[1],
                    filename=row[2],
                    file_type=row[3],
                    file_size=row[4],
                    category=row[5],
                    tags=json.loads(row[6]) if row[6] else [],
                    uploaded_by=row[7],
                    uploaded_at=datetime.fromisoformat(row[8]),
                    file_path=row[9],
                    thumbnail_path=row[10],
                    description=row[11] or "",
                    is_public=bool(row[12])
                )
                documents.append(doc)
            
            conn.close()
            return documents
            
        except Exception as e:
            st.error(f"Error retrieving documents: {e}")
            return []
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all document categories"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM document_categories ORDER BY name")
            rows = cursor.fetchall()
            
            categories = []
            for row in rows:
                categories.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'icon': row[3],
                    'color': row[4]
                })
            
            conn.close()
            return categories
            
        except Exception as e:
            st.error(f"Error retrieving categories: {e}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get document info first
            cursor.execute("SELECT file_path, thumbnail_path FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            
            if row:
                # Delete files
                if os.path.exists(row[0]):
                    os.remove(row[0])
                if row[1] and os.path.exists(row[1]):
                    os.remove(row[1])
                
                # Delete from database
                cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
                conn.commit()
            
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error deleting document: {e}")
            return False
    
    def get_document_stats(self, deal_id: str = None) -> Dict[str, Any]:
        """Get document statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT category, COUNT(*), SUM(file_size) FROM documents"
            params = []
            
            if deal_id:
                query += " WHERE deal_id = ?"
                params.append(deal_id)
            
            query += " GROUP BY category"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            stats = {
                'total_documents': 0,
                'total_size': 0,
                'by_category': {}
            }
            
            for row in rows:
                category, count, size = row
                stats['total_documents'] += count
                stats['total_size'] += size or 0
                stats['by_category'][category] = {
                    'count': count,
                    'size': size or 0
                }
            
            conn.close()
            return stats
            
        except Exception as e:
            st.error(f"Error getting document stats: {e}")
            return {'total_documents': 0, 'total_size': 0, 'by_category': {}}

def show_document_management(deal_id: str = None):
    """Show document management interface"""
    st.subheader("📁 Document & Photo Management")
    
    doc_manager = DocumentManager()
    
    # Document management tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Upload Files", 
        "📋 Document Library", 
        "📊 Statistics",
        "⚙️ Settings"
    ])
    
    with tab1:
        show_upload_interface(doc_manager, deal_id)
    
    with tab2:
        show_document_library(doc_manager, deal_id)
    
    with tab3:
        show_document_statistics(doc_manager, deal_id)
    
    with tab4:
        show_document_settings(doc_manager)

def show_upload_interface(doc_manager: DocumentManager, deal_id: str = None):
    """Show file upload interface"""
    st.markdown("### 📤 Upload Documents & Photos")
    
    # Get categories
    categories = doc_manager.get_categories()
    category_options = {cat['name']: cat['id'] for cat in categories}
    
    # Upload form
    with st.form("document_upload", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_files = st.file_uploader(
                "Choose files",
                accept_multiple_files=True,
                type=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt'],
                help="Upload property photos, contracts, reports, and other documents"
            )
        
        with col2:
            category_name = st.selectbox("Category", list(category_options.keys()))
            category_id = category_options[category_name]
        
        description = st.text_area("Description (optional)", placeholder="Brief description of the documents...")
        tags = st.text_input("Tags (optional)", placeholder="renovation, before, after, inspection")
        
        # Deal selection if not provided
        if not deal_id:
            deal_id = st.text_input("Deal ID", placeholder="Enter deal ID to associate documents")
        
        submitted = st.form_submit_button("📤 Upload Files", type="primary")
        
        if submitted and uploaded_files and deal_id:
            tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
            
            upload_progress = st.progress(0)
            status_container = st.empty()
            
            uploaded_count = 0
            total_files = len(uploaded_files)
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_container.info(f"Uploading {uploaded_file.name}...")
                
                doc_info = doc_manager.upload_document(
                    uploaded_file=uploaded_file,
                    deal_id=deal_id,
                    category=category_id,
                    tags=tag_list,
                    description=description
                )
                
                if doc_info:
                    uploaded_count += 1
                
                upload_progress.progress((i + 1) / total_files)
            
            status_container.success(f"✅ Successfully uploaded {uploaded_count}/{total_files} files!")
            
            if uploaded_count > 0:
                st.rerun()

def show_document_library(doc_manager: DocumentManager, deal_id: str = None):
    """Show document library with filtering and search"""
    st.markdown("### 📋 Document Library")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = doc_manager.get_categories()
        category_filter = st.selectbox("Filter by Category", 
            ['All'] + [cat['name'] for cat in categories])
    
    with col2:
        search_term = st.text_input("Search documents", placeholder="Search by filename or description")
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Upload Date", "File Name", "File Size", "Category"])
    
    # Get documents
    category_id = None
    if category_filter != 'All':
        category_id = next((cat['id'] for cat in categories if cat['name'] == category_filter), None)
    
    documents = doc_manager.get_documents(deal_id=deal_id, category=category_id)
    
    # Apply search filter
    if search_term:
        documents = [doc for doc in documents if 
                    search_term.lower() in doc.filename.lower() or 
                    search_term.lower() in doc.description.lower()]
    
    # Display documents
    if documents:
        st.markdown(f"**Found {len(documents)} documents**")
        
        # Display as grid for images, list for others
        image_docs = [doc for doc in documents if doc.file_type in ['.jpg', '.jpeg', '.png', '.gif']]
        other_docs = [doc for doc in documents if doc.file_type not in ['.jpg', '.jpeg', '.png', '.gif']]
        
        # Image gallery
        if image_docs:
            st.markdown("#### 📸 Photos")
            cols = st.columns(4)
            
            for i, doc in enumerate(image_docs):
                with cols[i % 4]:
                    try:
                        if doc.thumbnail_path and os.path.exists(doc.thumbnail_path):
                            with open(doc.thumbnail_path, "rb") as f:
                                thumbnail_data = f.read()
                            st.image(thumbnail_data, caption=doc.filename, use_column_width=True)
                        else:
                            st.image("https://via.placeholder.com/300x200?text=Image", 
                                   caption=doc.filename, use_column_width=True)
                        
                        # Download button for images
                        if os.path.exists(doc.file_path):
                            with open(doc.file_path, "rb") as f:
                                file_data = f.read()
                            st.download_button(
                                "⬇️", 
                                data=file_data,
                                file_name=doc.filename,
                                mime=mimetypes.guess_type(doc.filename)[0],
                                key=f"download_img_{doc.id}",
                                help="Download image"
                            )
                        
                        if st.button("🗑️", key=f"del_img_{doc.id}", help="Delete"):
                            if doc_manager.delete_document(doc.id):
                                st.success("Document deleted!")
                                st.rerun()
                    except Exception as e:
                        st.error(f"Error displaying image: {e}")
        
        # Other documents
        if other_docs:
            st.markdown("#### 📄 Documents")
            
            for doc in other_docs:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        file_icon = get_file_icon(doc.file_type)
                        st.markdown(f"{file_icon} **{doc.filename}**")
                        if doc.description:
                            st.caption(doc.description)
                    
                    with col2:
                        st.caption(f"{format_file_size(doc.file_size)}")
                        st.caption(doc.uploaded_at.strftime("%m/%d/%Y"))
                    
                    with col3:
                        category = next((cat for cat in categories if cat['id'] == doc.category), None)
                        if category:
                            st.markdown(f"{category['icon']} {category['name']}")
                    
                    with col4:
                        # Download button
                        if os.path.exists(doc.file_path):
                            with open(doc.file_path, "rb") as f:
                                file_data = f.read()
                            st.download_button(
                                "⬇️", 
                                data=file_data,
                                file_name=doc.filename,
                                mime=mimetypes.guess_type(doc.filename)[0],
                                key=f"download_{doc.id}",
                                help="Download file"
                            )
                        
                        if st.button("🗑️", key=f"del_doc_{doc.id}", help="Delete"):
                            if doc_manager.delete_document(doc.id):
                                st.success("Document deleted!")
                                st.rerun()
                    
                    st.markdown("---")
    else:
        st.info("📭 No documents found. Upload some files to get started!")

def show_document_statistics(doc_manager: DocumentManager, deal_id: str = None):
    """Show document statistics and analytics"""
    st.markdown("### 📊 Document Statistics")
    
    stats = doc_manager.get_document_stats(deal_id)
    
    # Overview metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Documents", stats['total_documents'])
    
    with col2:
        st.metric("Total Storage", format_file_size(stats['total_size']))
    
    with col3:
        avg_size = stats['total_size'] / stats['total_documents'] if stats['total_documents'] > 0 else 0
        st.metric("Average File Size", format_file_size(avg_size))
    
    # Category breakdown
    if stats['by_category']:
        st.markdown("#### 📂 Documents by Category")
        
        categories = doc_manager.get_categories()
        category_map = {cat['id']: cat for cat in categories}
        
        for category_id, category_stats in stats['by_category'].items():
            category = category_map.get(category_id, {'name': category_id, 'icon': '📁'})
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"{category['icon']} **{category['name']}**")
            
            with col2:
                st.markdown(f"{category_stats['count']} files")
            
            with col3:
                st.markdown(f"{format_file_size(category_stats['size'])}")

def show_document_settings(doc_manager: DocumentManager):
    """Show document management settings"""
    st.markdown("### ⚙️ Document Settings")
    
    st.info("🚧 Document settings and bulk operations coming soon!")
    
    # Placeholder for future settings
    with st.expander("📁 Storage Settings"):
        st.markdown("- Maximum file size: 50MB")
        st.markdown("- Supported formats: Images, PDFs, Office documents")
        st.markdown("- Auto-thumbnail generation: Enabled")
    
    with st.expander("🔒 Privacy Settings"):
        st.markdown("- Document sharing: Team members only")
        st.markdown("- External access: Disabled")
        st.markdown("- Backup: Automatic daily backup")

def get_file_icon(file_type: str) -> str:
    """Get icon for file type"""
    icons = {
        '.pdf': '📄',
        '.doc': '📝', '.docx': '📝',
        '.xls': '📊', '.xlsx': '📊',
        '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
        '.txt': '📃',
        '.zip': '🗜️',
        '.mp4': '🎥', '.avi': '🎥',
        '.mp3': '🎵', '.wav': '🎵'
    }
    return icons.get(file_type.lower(), '📁')

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"