"""
SWAG PRICING INTELLIGENCE - Premium UI
Phase 4: Swag Golf Brand Makeover
Dark mode premium interface with neon accents, bold typography, and stunning visual design.
Features: Tab navigation, live progress tracking, premium dashboard, settings editor.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import io
import os
import time
import pandas as pd
import threading
import queue
import json
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from main import run_pipeline
from config_loader import ConfigLoader
from sheets_writer import SheetsWriter


# Page configuration
st.set_page_config(
    page_title="SWAG Pricing Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SWAG GOLF BRAND - Dark Mode Premium UI
st.markdown("""
    <style>
    /* Global Dark Theme */
    .stApp {
        background-color: #1C1C1C;
        color: #F8F8F8;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Header Bar */
    .swag-header {
        background: linear-gradient(135deg, #1C1C1C 0%, #2A2A2A 100%);
        border-bottom: 2px solid #00FF7F;
        padding: 1.5rem 2rem;
        margin: -2rem -2rem 2rem -2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0, 255, 127, 0.1);
    }

    .swag-logo {
        font-family: 'EB Garamond', 'Georgia', serif;
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00FF7F 0%, #00BFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .swag-version {
        font-family: 'Roboto', 'Segoe UI', sans-serif;
        font-size: 0.75rem;
        color: #D4AF37;
        letter-spacing: 1px;
        opacity: 0.8;
    }

    /* Tab Navigation */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: #2A2A2A;
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid #00FF7F33;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #F8F8F8;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-family: 'Roboto', 'Segoe UI', sans-serif;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #00FF7F22;
        border-color: #00FF7F;
        transform: translateY(-2px);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00FF7F 0%, #00BFFF 50%, #D4AF37 100%);
        color: #1C1C1C !important;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(0, 255, 127, 0.3);
    }

    /* Card Styling */
    .swag-card {
        background: linear-gradient(135deg, #2A2A2A 0%, #1C1C1C 100%);
        border: 2px solid #00FF7F44;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }

    .swag-card:hover {
        border-color: #00FF7F;
        box-shadow: 0 12px 32px rgba(0, 255, 127, 0.2);
        transform: translateY(-4px);
    }

    /* Stat Cards */
    .stat-card {
        background: linear-gradient(135deg, #2A2A2A 0%, #1C1C1C 100%);
        border: 2px solid #00BFFF66;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0, 191, 255, 0.15);
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        border-color: #00BFFF;
        box-shadow: 0 8px 28px rgba(0, 191, 255, 0.3);
        transform: scale(1.02);
    }

    .stat-value {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00FF7F 0%, #00BFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.5rem 0;
    }

    .stat-label {
        font-size: 0.9rem;
        color: #F8F8F8;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }

    /* Drag-and-Drop Zone */
    .upload-zone {
        background: linear-gradient(135deg, #2A2A2A 0%, #1C1C1C 100%);
        border: 3px dashed #00FF7F66;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .upload-zone:hover {
        border-color: #00FF7F;
        background: linear-gradient(135deg, #2A2A2A 0%, #2A2A2A 100%);
        box-shadow: 0 0 40px rgba(0, 255, 127, 0.3);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00BFFF 0%, #00FF7F 100%);
        color: #1C1C1C;
        border: 2px solid #D4AF37;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 191, 255, 0.3);
    }

    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 24px rgba(0, 191, 255, 0.5), 0 0 30px rgba(212, 175, 55, 0.3);
        background: linear-gradient(135deg, #00FF7F 0%, #00BFFF 100%);
    }

    .stButton > button:active {
        transform: scale(0.98);
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00FF7F 0%, #00BFFF 100%);
        box-shadow: 0 0 20px rgba(0, 255, 127, 0.5);
    }

    .stProgress > div > div {
        background-color: #2A2A2A;
        border-radius: 10px;
        border: 1px solid #00FF7F33;
    }

    /* Log Container */
    .log-container {
        background-color: #0D0D0D;
        border: 2px solid #00FF7F33;
        border-radius: 12px;
        padding: 1.5rem;
        font-family: 'Courier New', 'Monaco', monospace;
        font-size: 0.85rem;
        color: #00FF7F;
        max-height: 500px;
        overflow-y: auto;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
    }

    .log-container::-webkit-scrollbar {
        width: 10px;
    }

    .log-container::-webkit-scrollbar-track {
        background: #1C1C1C;
        border-radius: 10px;
    }

    .log-container::-webkit-scrollbar-thumb {
        background: #00FF7F;
        border-radius: 10px;
    }

    .log-success {
        color: #00FF7F;
        font-weight: 600;
    }

    .log-error {
        color: #FF0054;
        font-weight: 600;
    }

    .log-warning {
        color: #FFD700;
        font-weight: 600;
    }

    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #2A2A2A;
        color: #F8F8F8;
        border: 2px solid #00FF7F44;
        border-radius: 8px;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #00FF7F;
        box-shadow: 0 0 20px rgba(0, 255, 127, 0.3);
    }

    /* Labels */
    label {
        color: #F8F8F8 !important;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-weight: 600;
    }

    .stSuccess {
        background-color: #00FF7F22;
        border: 2px solid #00FF7F;
        color: #00FF7F;
    }

    .stError {
        background-color: #FF005422;
        border: 2px solid #FF0054;
        color: #FF0054;
    }

    .stWarning {
        background-color: #FFD70022;
        border: 2px solid #FFD700;
        color: #FFD700;
    }

    .stInfo {
        background-color: #00BFFF22;
        border: 2px solid #00BFFF;
        color: #00BFFF;
    }

    /* Data Tables */
    .stDataFrame {
        background-color: #2A2A2A;
        border: 2px solid #00FF7F44;
        border-radius: 12px;
        overflow: hidden;
    }

    .stDataFrame tbody tr:hover {
        background-color: #00FF7F11 !important;
    }

    .stDataFrame tbody tr:nth-child(even) {
        background-color: #1C1C1C;
    }

    .stDataFrame tbody tr:nth-child(odd) {
        background-color: #252525;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00FF7F 0%, #00BFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #2A2A2A;
        border: 1px solid #00FF7F44;
        border-radius: 8px;
        color: #F8F8F8;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background-color: #00FF7F22;
        border-color: #00FF7F;
    }

    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #2A2A2A 0%, #1C1C1C 100%);
        border: 3px dashed #00FF7F66;
        border-radius: 16px;
        padding: 2rem;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #00FF7F;
        box-shadow: 0 0 30px rgba(0, 255, 127, 0.3);
    }

    /* Animations */
    @keyframes glow {
        0%, 100% {
            box-shadow: 0 0 20px rgba(0, 255, 127, 0.3);
        }
        50% {
            box-shadow: 0 0 40px rgba(0, 255, 127, 0.6);
        }
    }

    .glow-effect {
        animation: glow 2s ease-in-out infinite;
    }

    /* Skull Icon (subtle) */
    .skull-icon {
        opacity: 0.1;
        position: fixed;
        bottom: 20px;
        right: 20px;
        font-size: 4rem;
        pointer-events: none;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)


def save_uploaded_files(uploaded_files):
    """
    Save uploaded PDF files to Invoices/new/ directory.

    Args:
        uploaded_files: List of Streamlit UploadedFile objects

    Returns:
        tuple: (success_count, error_list)
    """
    # Ensure Invoices/new directory exists
    invoices_dir = Path("Invoices/new")
    invoices_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    errors = []

    for uploaded_file in uploaded_files:
        try:
            # Save file to Invoices/new
            file_path = invoices_dir / uploaded_file.name

            # Write uploaded file bytes to disk
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            success_count += 1

        except Exception as e:
            errors.append(f"{uploaded_file.name}: {str(e)}")

    return success_count, errors


def get_processed_files_summary():
    """
    Get list of recently processed files from Invoices/processed/.

    Returns:
        list: List of tuples (filename, modified_time)
    """
    processed_dir = Path("Invoices/processed")

    if not processed_dir.exists():
        return []

    files = []
    for pdf_file in processed_dir.glob("*.pdf"):
        modified_time = datetime.fromtimestamp(pdf_file.stat().st_mtime)
        files.append((pdf_file.name, modified_time))

    # Sort by modified time, most recent first
    files.sort(key=lambda x: x[1], reverse=True)

    return files[:10]  # Return last 10 files


def get_recent_sheet_activity():
    """
    Fetch the last 10 rows from the Pricing Data Google Sheet.

    Returns:
        pd.DataFrame: Recent pricing data, or empty DataFrame if error
    """
    try:
        # Load config
        config = ConfigLoader()
        gs_config = config.config.get('google_sheets', {})

        # Initialize sheets writer
        writer = SheetsWriter(
            sheet_id=gs_config.get('sheet_id', ''),
            credentials_file=gs_config.get('credentials_file', 'credentials.json'),
            token_file=gs_config.get('token_file', 'token.json'),
            sheet_name=gs_config.get('sheet_name', 'Pricing Data')
        )

        # Authenticate
        writer.authenticate()

        # Get all data from sheet
        result = writer.service.spreadsheets().values().get(
            spreadsheetId=gs_config.get('sheet_id'),
            range=f"{gs_config.get('sheet_name')}!A:N"
        ).execute()

        values = result.get('values', [])

        if not values or len(values) < 2:
            return pd.DataFrame()

        # First row is headers
        headers = values[0]
        data_rows = values[1:]

        # Get last 10 rows
        recent_rows = data_rows[-10:] if len(data_rows) >= 10 else data_rows

        # Create DataFrame
        df = pd.DataFrame(recent_rows, columns=headers)

        return df

    except Exception as e:
        st.error(f"Failed to fetch recent activity: {e}")
        return pd.DataFrame()


class LogCapture:
    """Thread-safe log capture for real-time streaming."""

    def __init__(self):
        self.log_queue = queue.Queue()
        self.log_buffer = []

    def write(self, message):
        """Write message to queue and buffer."""
        self.log_buffer.append(message)
        self.log_queue.put(message)

    def flush(self):
        """Flush buffer (required for file-like interface)."""
        pass

    def getvalue(self):
        """Get all captured logs as string."""
        return ''.join(self.log_buffer)


def run_pipeline_with_progress(total_files, log_container, progress_bar, status_text):
    """
    Run pipeline with live progress updates.

    Args:
        total_files: Total number of files to process
        log_container: Streamlit container for logs
        progress_bar: Streamlit progress bar
        status_text: Streamlit text for status messages

    Returns:
        dict: Pipeline results
    """
    # Create log capture
    log_capture = LogCapture()

    # Redirect stdout
    old_stdout = sys.stdout
    sys.stdout = log_capture

    try:
        # Initialize progress
        progress = 0
        processed_count = 0

        # Run pipeline
        results = run_pipeline()

        # Update progress to 100%
        progress_bar.progress(1.0)
        status_text.text("✅ Processing complete!")

        # Get all logs
        sys.stdout = old_stdout
        all_logs = log_capture.getvalue()

        return results, all_logs

    except Exception as e:
        sys.stdout = old_stdout
        all_logs = log_capture.getvalue()
        raise e

    finally:
        sys.stdout = old_stdout


def load_config():
    """
    Load configuration from config.json.

    Returns:
        dict: Configuration dictionary
    """
    config_path = Path("config.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load config.json: {e}")
        return {}


def save_config(config_data):
    """
    Save configuration to config.json.

    Args:
        config_data: Dictionary with configuration

    Returns:
        bool: True if successful, False otherwise
    """
    config_path = Path("config.json")
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Failed to save config.json: {e}")
        return False


def mask_sensitive_value(value, show_chars=4):
    """
    Mask sensitive values showing only last N characters.

    Args:
        value: String to mask
        show_chars: Number of characters to show at end

    Returns:
        str: Masked string
    """
    if not value or len(value) <= show_chars:
        return "*" * 8

    return "*" * (len(value) - show_chars) + value[-show_chars:]


def validate_url(url):
    """
    Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        bool: True if valid URL format
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return url_pattern.match(url) is not None


def test_google_sheets_connection(sheet_id, credentials_file, token_file, sheet_name):
    """
    Test Google Sheets connection with lightweight API call.

    Args:
        sheet_id: Google Sheet ID
        credentials_file: Path to credentials JSON
        token_file: Path to token JSON
        sheet_name: Sheet tab name

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Initialize sheets writer
        writer = SheetsWriter(
            sheet_id=sheet_id,
            credentials_file=credentials_file,
            token_file=token_file,
            sheet_name=sheet_name
        )

        # Authenticate
        writer.authenticate()

        # Try to read just the first cell
        result = writer.service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"{sheet_name}!A1"
        ).execute()

        return True, "✅ Connection successful! Sheet is accessible."

    except Exception as e:
        return False, f"❌ Connection failed: {str(e)}"


def get_default_config():
    """
    Get default configuration structure.

    Returns:
        dict: Default configuration
    """
    return {
        "azure": {
            "endpoint": "https://your-resource.cognitiveservices.azure.com/",
            "key": "YOUR_AZURE_KEY_HERE"
        },
        "google_sheets": {
            "sheet_id": "YOUR_GOOGLE_SHEET_ID_HERE",
            "credentials_file": "credentials.json",
            "token_file": "token.json",
            "sheet_name": "Pricing Data"
        },
        "paths": {
            "invoices_new": "Invoices/new",
            "invoices_processed": "Invoices/processed",
            "output": "Output"
        },
        "variance_thresholds": {
            "green": 3.0,
            "yellow": 10.0
        }
    }


def render_dashboard_tab():
    """Render the Dashboard tab with premium stat cards."""
    st.markdown("## 📊 Performance Dashboard")

    # Try to load recent processing results
    try:
        config = ConfigLoader()
        gs_config = config.config.get('google_sheets', {})

        # Fetch recent sheet data
        recent_data = get_recent_sheet_activity()

        if not recent_data.empty:
            # Calculate stats
            total_files = len(get_processed_files_summary())

            # Count variance flags if available
            variance_counts = {
                '🟢': 0,
                '🟡': 0,
                '🔴': 0
            }

            if 'variance_flag' in recent_data.columns:
                for flag in recent_data['variance_flag']:
                    if flag in variance_counts:
                        variance_counts[flag] += 1

            # Calculate estimated impact cost (placeholder logic)
            impact_cost = 0
            if 'unit_cost' in recent_data.columns and 'variance_%' in recent_data.columns:
                try:
                    for idx, row in recent_data.iterrows():
                        cost = float(str(row.get('unit_cost', 0)).replace('$', '').replace(',', ''))
                        variance = float(str(row.get('variance_%', 0)).replace('%', ''))
                        impact_cost += abs(cost * variance / 100)
                except:
                    impact_cost = 0

            # Stat Cards Row
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-label">Files Processed</div>
                        <div class="stat-value">{total_files}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                variance_alerts = variance_counts['🟡'] + variance_counts['🔴']
                st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-label">Variance Alerts</div>
                        <div class="stat-value">🔴{variance_counts['🔴']} 🟡{variance_counts['🟡']}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-label">Impact Cost</div>
                        <div class="stat-value">${impact_cost:,.2f}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Interactive Table
            st.markdown("### 📋 Recent Activity (Last 10 Items)")

            # Display key columns in a cleaner format
            display_columns = ['vendor_sku', 'description', 'unit_cost',
                             'variance_flag', 'variance_%', 'processed_date']

            # Filter to existing columns
            display_cols = [col for col in display_columns if col in recent_data.columns]

            if display_cols:
                st.dataframe(
                    recent_data[display_cols],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.dataframe(recent_data, use_container_width=True, hide_index=True)

            # Google Sheets Link Button
            st.markdown("---")
            sheet_url = f"https://docs.google.com/spreadsheets/d/{gs_config.get('sheet_id', '')}"
            st.markdown(f"""
                <a href="{sheet_url}" target="_blank" style="text-decoration: none;">
                    <div class="swag-card" style="text-align: center; cursor: pointer;">
                        <h3 style="color: #00FF7F; margin: 0;">📊 View Full Data in Google Sheets →</h3>
                        <p style="color: #F8F8F8; opacity: 0.7; margin-top: 0.5rem;">Open complete pricing data with all analysis details</p>
                    </div>
                </a>
            """, unsafe_allow_html=True)

        else:
            # No data available
            st.markdown("""
                <div class="swag-card" style="text-align: center; padding: 4rem;">
                    <h2 style="color: #00FF7F;">📊 Dashboard Ready</h2>
                    <p style="color: #F8F8F8; opacity: 0.7; font-size: 1.1rem;">
                        Process invoices in the <strong>Upload & Process</strong> tab to see analytics here.
                    </p>
                </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Failed to load dashboard data: {str(e)}")
        st.info("💡 Process some invoices first to populate the dashboard.")


def render_settings_tab():
    """Render the Settings tab with premium SWAG card styling."""
    # Header
    st.markdown("""
        <div class="swag-card">
            <h2 style="color: #D4AF37; margin: 0 0 0.5rem 0;">⚙️ Configuration Settings</h2>
            <p style="color: #F8F8F8; opacity: 0.7;">
                Edit your application settings below. All changes are saved to <code style="color: #00BFFF;">config.json</code>
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Load current config
    config = load_config()

    if not config:
        st.error("❌ Failed to load configuration. Using default values.")
        config = get_default_config()

    # Azure Configuration Card
    st.markdown("""
        <div class="swag-card">
            <h3 style="color: #00BFFF; margin: 0 0 1rem 0;">🔷 Azure Form Recognizer</h3>
        </div>
    """, unsafe_allow_html=True)

    with st.form("azure_config"):
        azure_endpoint = st.text_input(
            "Azure Endpoint",
            value=config.get('azure', {}).get('endpoint', ''),
            help="Azure Form Recognizer endpoint URL (e.g., https://your-resource.cognitiveservices.azure.com/)"
        )

        # Check if key exists and mask it
        current_key = config.get('azure', {}).get('key', '')
        is_key_set = current_key and current_key != "YOUR_AZURE_KEY_HERE"

        if is_key_set:
            st.info(f"🔒 Current Key: {mask_sensitive_value(current_key)}")
            azure_key = st.text_input(
                "Azure API Key (leave blank to keep current)",
                type="password",
                help="Enter new key or leave blank to keep existing key"
            )
        else:
            azure_key = st.text_input(
                "Azure API Key",
                type="password",
                help="Enter your Azure Form Recognizer API key"
            )

        azure_submit = st.form_submit_button("💾 Save Azure Settings")

        if azure_submit:
            # Validate endpoint
            if not azure_endpoint:
                st.error("❌ Azure endpoint cannot be empty")
            elif not validate_url(azure_endpoint):
                st.error("❌ Invalid Azure endpoint URL format")
            else:
                # Update config
                if 'azure' not in config:
                    config['azure'] = {}

                config['azure']['endpoint'] = azure_endpoint

                # Only update key if provided
                if azure_key:
                    config['azure']['key'] = azure_key
                elif not is_key_set:
                    st.error("❌ Azure API key is required for new configuration")
                    return

                # Save config
                if save_config(config):
                    st.success("✅ Azure settings saved successfully!")
                    st.info("ℹ️ Restart the app to apply changes")
                else:
                    st.error("❌ Failed to save settings")

    st.markdown("---")

    # Google Sheets Configuration
    st.markdown("### 📊 Google Sheets")

    with st.form("sheets_config"):
        sheet_id = st.text_input(
            "Google Sheet ID",
            value=config.get('google_sheets', {}).get('sheet_id', ''),
            help="The ID from your Google Sheet URL"
        )

        sheet_name = st.text_input(
            "Sheet Tab Name",
            value=config.get('google_sheets', {}).get('sheet_name', 'Pricing Data'),
            help="Name of the sheet tab to write data to"
        )

        credentials_file = st.text_input(
            "Credentials File",
            value=config.get('google_sheets', {}).get('credentials_file', 'credentials.json'),
            help="Path to OAuth2 credentials JSON file"
        )

        token_file = st.text_input(
            "Token File",
            value=config.get('google_sheets', {}).get('token_file', 'token.json'),
            help="Path to store authentication token"
        )

        col1, col2 = st.columns(2)

        with col1:
            sheets_submit = st.form_submit_button("💾 Save Google Sheets Settings")

        with col2:
            test_connection = st.form_submit_button("🔌 Test Connection")

        if sheets_submit:
            # Validate fields
            if not sheet_id:
                st.error("❌ Google Sheet ID cannot be empty")
            elif not sheet_name:
                st.error("❌ Sheet name cannot be empty")
            else:
                # Update config
                if 'google_sheets' not in config:
                    config['google_sheets'] = {}

                config['google_sheets']['sheet_id'] = sheet_id
                config['google_sheets']['sheet_name'] = sheet_name
                config['google_sheets']['credentials_file'] = credentials_file
                config['google_sheets']['token_file'] = token_file

                # Save config
                if save_config(config):
                    st.success("✅ Google Sheets settings saved successfully!")
                    st.info("ℹ️ Restart the app to apply changes")
                else:
                    st.error("❌ Failed to save settings")

        if test_connection:
            with st.spinner("Testing Google Sheets connection..."):
                success, message = test_google_sheets_connection(
                    sheet_id, credentials_file, token_file, sheet_name
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)

    st.markdown("---")

    # Variance Thresholds
    st.markdown("### 🚦 Variance Thresholds")

    with st.form("variance_config"):
        green_threshold = st.number_input(
            "Green Threshold (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(config.get('variance_thresholds', {}).get('green', 3.0)),
            step=0.5,
            help="Variance percentage for green flag (≤ this value)"
        )

        yellow_threshold = st.number_input(
            "Yellow Threshold (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(config.get('variance_thresholds', {}).get('yellow', 10.0)),
            step=0.5,
            help="Variance percentage for yellow flag (≤ this value, > green)"
        )

        variance_submit = st.form_submit_button("💾 Save Variance Thresholds")

        if variance_submit:
            # Validate thresholds
            if green_threshold >= yellow_threshold:
                st.error("❌ Green threshold must be less than yellow threshold")
            else:
                # Update config
                if 'variance_thresholds' not in config:
                    config['variance_thresholds'] = {}

                config['variance_thresholds']['green'] = green_threshold
                config['variance_thresholds']['yellow'] = yellow_threshold

                # Save config
                if save_config(config):
                    st.success("✅ Variance thresholds saved successfully!")
                    st.info("ℹ️ Restart the app to apply changes")
                else:
                    st.error("❌ Failed to save settings")

    st.markdown("---")

    # Folder Paths
    st.markdown("### 📁 Folder Paths")

    with st.form("paths_config"):
        invoices_new = st.text_input(
            "New Invoices Folder",
            value=config.get('paths', {}).get('invoices_new', 'Invoices/new'),
            help="Folder for new PDF invoices to process"
        )

        invoices_processed = st.text_input(
            "Processed Invoices Folder",
            value=config.get('paths', {}).get('invoices_processed', 'Invoices/processed'),
            help="Folder for archived processed invoices"
        )

        output_folder = st.text_input(
            "Output Folder",
            value=config.get('paths', {}).get('output', 'Output'),
            help="Folder for output files and logs"
        )

        paths_submit = st.form_submit_button("💾 Save Folder Paths")

        if paths_submit:
            # Validate paths
            if not invoices_new or not invoices_processed or not output_folder:
                st.error("❌ All folder paths must be specified")
            else:
                # Update config
                if 'paths' not in config:
                    config['paths'] = {}

                config['paths']['invoices_new'] = invoices_new
                config['paths']['invoices_processed'] = invoices_processed
                config['paths']['output'] = output_folder

                # Save config
                if save_config(config):
                    st.success("✅ Folder paths saved successfully!")
                    st.info("ℹ️ Restart the app to apply changes")
                else:
                    st.error("❌ Failed to save settings")

    st.markdown("---")

    # Utilities
    st.markdown("### 🛠️ Utilities")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            default_config = get_default_config()
            if save_config(default_config):
                st.success("✅ Configuration reset to defaults!")
                st.info("ℹ️ Restart the app to apply changes")
                st.rerun()
            else:
                st.error("❌ Failed to reset configuration")

    with col2:
        if st.button("📄 View Current Config", use_container_width=True):
            st.json(config)


def render_upload_process_tab():
    """Render the Upload & Process tab with premium SWAG styling."""
    # Premium section header
    st.markdown("""
        <div class="swag-card">
            <h2 style="color: #00FF7F; margin: 0 0 0.5rem 0;">📄 Upload Invoice PDFs</h2>
            <p style="color: #F8F8F8; opacity: 0.7;">
                Drag and drop your supplier invoices below. Our AI-powered system extracts pricing data,
                analyzes variance, and syncs to Google Sheets automatically.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # File uploader with premium styling
    uploaded_files = st.file_uploader(
        "SELECT PDFs TO ANALYZE",
        type=["pdf"],
        accept_multiple_files=True,
        help="⚡ Upload one or more PDF invoices to begin processing",
        label_visibility="collapsed"
    )

    # Display uploaded files in styled cards
    if uploaded_files:
        st.markdown(f"""
            <div class="swag-card">
                <h3 style="color: #00BFFF; margin: 0 0 1rem 0;">✅ {len(uploaded_files)} File(s) Ready</h3>
            </div>
        """, unsafe_allow_html=True)

        with st.expander("📋 View File Details", expanded=False):
            for idx, file in enumerate(uploaded_files, 1):
                file_size_kb = len(file.getvalue()) / 1024
                st.markdown(f"""
                    <div style="padding: 0.5rem; border-left: 3px solid #00FF7F; margin: 0.5rem 0; background: #2A2A2A22;">
                        <strong style="color: #00FF7F;">{idx}.</strong>
                        <span style="color: #F8F8F8;">{file.name}</span>
                        <span style="color: #D4AF37; opacity: 0.8;">({file_size_kb:.1f} KB)</span>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Premium Process Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button(
            "⚡ RUN ANALYSIS →",
            type="primary",
            use_container_width=True,
            disabled=(not uploaded_files)
        )

    # Process invoices
    if process_button and uploaded_files:
        # Save uploaded files
        with st.spinner("💾 Saving uploaded files..."):
            success_count, errors = save_uploaded_files(uploaded_files)

            if errors:
                st.error(f"❌ Failed to save {len(errors)} file(s):")
                for error in errors:
                    st.text(f"  • {error}")
                return

            st.success(f"✅ Saved {success_count} file(s) to Invoices/new/")

        # Run pipeline with live progress
        st.markdown("---")
        st.subheader("⚙️ Processing Pipeline")

        # Create progress components
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        status_text.text("🔄 Starting processing pipeline...")

        # Create container for live logs
        log_expander = st.expander("📋 Live Processing Logs", expanded=True)
        log_container = log_expander.empty()

        # Capture console output
        old_stdout = sys.stdout
        sys.stdout = log_buffer = io.StringIO()

        try:
            # Update progress as we go
            progress_bar.progress(0.1)
            status_text.text("🔄 Initializing services...")

            # Run the pipeline
            results = run_pipeline()

            # Update progress to 100%
            progress_bar.progress(1.0)
            status_text.text("✅ Processing complete!")

            # Restore stdout
            sys.stdout = old_stdout
            log_output = log_buffer.getvalue()

            # Display logs in container
            log_container.code(log_output, language="text")

            # Display results
            st.markdown("---")

            if results['success']:
                # Enhanced Summary Card
                st.markdown('<div class="summary-card">', unsafe_allow_html=True)
                st.markdown("### 📊 Processing Summary")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(f"**Total Processed**")
                    st.markdown(f"# {results['total_files']}")

                with col2:
                    st.markdown(f"**✅ Successful**")
                    st.markdown(f"# {len(results['successful_files'])}")

                with col3:
                    green_count = results['variance_counts']['🟢']
                    yellow_count = results['variance_counts']['🟡']
                    st.markdown(f"**⚠️ Moderate (🟡)**")
                    st.markdown(f"# {yellow_count}")

                with col4:
                    red_count = results['variance_counts']['🔴']
                    st.markdown(f"**🔺 High Variance (🔴)**")
                    st.markdown(f"# {red_count}")

                # Timestamp and link
                st.markdown(f"**Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                if results['sheet_url']:
                    st.markdown(f"**📊 [View Google Sheet →]({results['sheet_url']})**")

                st.markdown('</div>', unsafe_allow_html=True)

                # Detailed Metrics
                st.markdown("---")
                st.subheader("📈 Detailed Metrics")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total PDFs", results['total_files'])
                    st.metric("Rows Written", results['total_rows_written'])

                with col2:
                    st.metric("Successful", len(results['successful_files']))
                    st.metric("Failed", len(results['failed_files']))

                with col3:
                    st.metric(
                        "🟢 Green (≤3%)",
                        results['variance_counts']['🟢'],
                        help="Pricing within normal range"
                    )
                    st.metric(
                        "🟡 Yellow (≤10%)",
                        results['variance_counts']['🟡'],
                        help="Moderate variance"
                    )
                    st.metric(
                        "🔴 Red (>10%)",
                        results['variance_counts']['🔴'],
                        help="High variance"
                    )

                # Recent Activity Table
                st.markdown("---")
                st.subheader("📊 Recent Activity (Last 10 Rows)")

                with st.spinner("Fetching recent data from Google Sheets..."):
                    recent_data = get_recent_sheet_activity()

                if not recent_data.empty:
                    # Display key columns in a cleaner format
                    display_columns = ['vendor_sku', 'description', 'unit_cost',
                                     'variance_flag', 'variance_%', 'processed_date']

                    # Filter to existing columns
                    display_cols = [col for col in display_columns if col in recent_data.columns]

                    if display_cols:
                        st.dataframe(
                            recent_data[display_cols],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.dataframe(recent_data, use_container_width=True, hide_index=True)
                else:
                    st.info("No recent activity found in Google Sheet.")

                # Successfully processed files
                if results['successful_files']:
                    st.markdown("---")
                    st.subheader("✅ Successfully Processed Files")

                    for filename in results['successful_files']:
                        archived = "→ Archived" if filename in results['moved_files'] else ""
                        st.text(f"✓ {filename} {archived}")

                # Failed files
                if results['failed_files']:
                    st.markdown("---")
                    st.subheader("❌ Failed Files")

                    for filename, error in results['failed_files']:
                        st.error(f"**{filename}**")
                        st.text(f"  Error: {error}")
                        st.text("  Status: Kept in Invoices/new/ for review")

            else:
                # Error message
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error(f"❌ **Processing failed:** {results.get('error', 'Unknown error')}")
                st.markdown('</div>', unsafe_allow_html=True)

                # Show logs for debugging
                with st.expander("📋 View error logs", expanded=True):
                    st.code(log_output, language="text")

        except Exception as e:
            sys.stdout = old_stdout
            st.error(f"❌ **Unexpected error:** {str(e)}")

            # Show logs
            log_output = log_buffer.getvalue()
            with st.expander("📋 View error logs", expanded=True):
                st.code(log_output, language="text")

    # Recently processed files section
    st.markdown("---")
    st.subheader("📦 Recently Processed Files")

    processed_files = get_processed_files_summary()

    if processed_files:
        st.text(f"Showing last {len(processed_files)} processed file(s)")

        # Create a simple table
        for filename, modified_time in processed_files:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"📄 {filename}")
            with col2:
                st.text(f"{modified_time.strftime('%Y-%m-%d %H:%M')}")
    else:
        st.info("ℹ️ No processed files found. Upload and process invoices to see them here.")

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <div style="color: #D4AF37; font-size: 0.9rem; font-weight: 600; letter-spacing: 1px;">
                ⚡ SWAG PRICING INTELLIGENCE ⚡
            </div>
            <div style="color: #00FF7F; font-size: 0.75rem; margin-top: 0.5rem; opacity: 0.6;">
                PHASE 4: PREMIUM UI MAKEOVER • LOCAL DEPLOY • v1.0
            </div>
        </div>
    """, unsafe_allow_html=True)


def main():
    """Main application with tab navigation - SWAG GOLF PREMIUM UI"""

    # Premium Header Bar
    st.markdown("""
        <div class="swag-header">
            <div>
                <div class="swag-logo">⚡ SWAG PRICING INTELLIGENCE</div>
                <div class="swag-version">v1.0 • LOCAL DEPLOY • PHASE 4</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Subtle skull icon watermark
    st.markdown('<div class="skull-icon">💀</div>', unsafe_allow_html=True)

    # Create tabs with new styling
    tab1, tab2, tab3 = st.tabs(["📄 Upload & Process", "📊 Dashboard", "⚙️ Settings"])

    with tab1:
        render_upload_process_tab()

    with tab2:
        render_dashboard_tab()

    with tab3:
        render_settings_tab()


if __name__ == "__main__":
    main()
