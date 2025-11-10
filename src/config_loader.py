"""
Configuration Loader for Swag Golf Pricing Intelligence Tool
Validates and loads configuration from config.json with safety checks.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Loads and validates configuration from config.json"""

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration loader.

        Args:
            config_path: Path to config.json file

        Raises:
            FileNotFoundError: If config.json doesn't exist
            ValueError: If configuration is invalid
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                "Please ensure config.json exists in the project root."
            )

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def _validate_config(self) -> None:
        """Validate required configuration fields."""
        # Check Azure credentials
        if 'azure' not in self.config:
            raise ValueError("Missing 'azure' section in config.json")

        azure = self.config['azure']
        if not azure.get('endpoint') or azure['endpoint'] == "YOUR_AZURE_ENDPOINT_HERE":
            raise ValueError(
                "Azure endpoint not configured. Please update config.json with your "
                "Azure Form Recognizer endpoint."
            )

        if not azure.get('key') or azure['key'] == "YOUR_AZURE_KEY_HERE":
            raise ValueError(
                "Azure key not configured. Please update config.json with your "
                "Azure Form Recognizer API key."
            )

        # Check paths section
        if 'paths' not in self.config:
            raise ValueError("Missing 'paths' section in config.json")

        # Check variance thresholds
        if 'variance_thresholds' not in self.config:
            raise ValueError("Missing 'variance_thresholds' section in config.json")

        thresholds = self.config['variance_thresholds']
        if 'green' not in thresholds or 'yellow' not in thresholds:
            raise ValueError("Missing green or yellow threshold in variance_thresholds")

        # Check Google Sheets configuration (optional, for warning only)
        if 'google_sheets' in self.config:
            gs = self.config['google_sheets']
            if not gs.get('sheet_id') or gs['sheet_id'] == "YOUR_GOOGLE_SHEET_ID_HERE":
                print("[WARN]  Warning: Google Sheet ID not configured in config.json")

    def get_azure_endpoint(self) -> str:
        """Get Azure Form Recognizer endpoint."""
        return self.config['azure']['endpoint']

    def get_azure_key(self) -> str:
        """Get Azure Form Recognizer API key."""
        return self.config['azure']['key']

    def get_path(self, path_key: str) -> Path:
        """
        Get path from configuration.

        Args:
            path_key: Key name in paths section (e.g., 'invoices_new')

        Returns:
            Path object for the requested path
        """
        if path_key not in self.config['paths']:
            raise KeyError(f"Path key '{path_key}' not found in config.json")

        return Path(self.config['paths'][path_key])

    def get_variance_threshold(self, level: str) -> float:
        """
        Get variance threshold for specified level.

        Args:
            level: 'green' or 'yellow'

        Returns:
            Threshold percentage as float
        """
        if level not in self.config['variance_thresholds']:
            raise KeyError(f"Variance threshold '{level}' not found in config.json")

        return float(self.config['variance_thresholds'][level])

    def ensure_directories_exist(self) -> None:
        """Create necessary directories if they don't exist."""
        for path_key in ['invoices_new', 'invoices_processed', 'output_excel']:
            path = self.get_path(path_key)
            # For files, create parent directory
            if path_key.endswith('_excel') or path_key.endswith('_file'):
                path.parent.mkdir(parents=True, exist_ok=True)
            else:
                path.mkdir(parents=True, exist_ok=True)

    def list_new_invoices(self) -> list:
        """
        List all PDF files in the new invoices directory.

        Returns:
            List of Path objects for PDF files
        """
        invoices_path = self.get_path('invoices_new')
        if not invoices_path.exists():
            return []

        pdf_files = sorted(invoices_path.glob('*.pdf'))
        return pdf_files


# Test function for validation
def test_config_loader():
    """Test configuration loader functionality."""
    try:
        config = ConfigLoader()
        print("[OK] Configuration loaded successfully")
        print(f"  Azure Endpoint: {config.get_azure_endpoint()[:30]}...")
        print(f"  Invoices Path: {config.get_path('invoices_new')}")
        print(f"  Green Threshold: {config.get_variance_threshold('green')}%")

        # Ensure directories exist
        config.ensure_directories_exist()
        print("[OK] Directories verified/created")

        # List PDFs in new invoices folder
        pdf_files = config.list_new_invoices()
        print(f"[OK] Found {len(pdf_files)} PDF(s) in Invoices/new")
        for pdf in pdf_files:
            print(f"  - {pdf.name}")

        return True

    except Exception as e:
        print(f"[ERROR] Configuration Error: {e}")
        return False


if __name__ == "__main__":
    test_config_loader()
