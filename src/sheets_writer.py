"""
Google Sheets Writer for Swag Golf Pricing Intelligence Tool
Handles authentication and writing data to Google Sheets via Sheets API v4.
Enhanced with bulletproof column alignment and data sanitization.
"""

import os
import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete token.json
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Canonical column order - MUST match Google Sheet headers exactly
COLUMNS = [
    "vendor_sku",
    "description",
    "quantity",
    "unit_cost",
    "total_cost",
    "supplier",
    "invoice_number",
    "invoice_date",
    "variance_%",
    "variance_flag",
    "supplier_baseline_%",
    "impact_$",
    "source_file",
    "processed_date"
]

# Numeric columns that require sanitization
NUMERIC_COLUMNS = ["quantity", "unit_cost", "total_cost", "variance_%", "supplier_baseline_%", "impact_$"]


class SheetsWriter:
    """Writes pricing data to Google Sheets with authentication and error handling."""

    def __init__(self, sheet_id: str, credentials_file: str = "credentials.json",
                 token_file: str = "token.json", sheet_name: str = "Pricing Data"):
        """
        Initialize Google Sheets writer.

        Args:
            sheet_id: Google Sheets spreadsheet ID
            credentials_file: Path to OAuth2 credentials JSON
            token_file: Path to store authentication token
            sheet_name: Name of the sheet tab to write to

        Raises:
            FileNotFoundError: If credentials.json doesn't exist
            ValueError: If sheet_id is invalid
        """
        self.sheet_id = sheet_id
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self.sheet_name = sheet_name
        self.service = None

        # Validate inputs
        if not self.sheet_id or self.sheet_id == "YOUR_GOOGLE_SHEET_ID_HERE":
            raise ValueError(
                "Google Sheet ID not configured. Please update config.json with your "
                "Google Sheets spreadsheet ID."
            )

        if not self.credentials_file.exists():
            raise FileNotFoundError(
                f"Google API credentials not found: {self.credentials_file}\n"
                "Please download credentials.json from Google Cloud Console:\n"
                "1. Go to https://console.cloud.google.com/\n"
                "2. Enable Google Sheets API\n"
                "3. Create OAuth 2.0 credentials\n"
                "4. Download as credentials.json"
            )

    def authenticate(self) -> None:
        """
        Authenticate with Google Sheets API using OAuth2.
        Creates token.json if it doesn't exist or refreshes if expired.

        Raises:
            Exception: If authentication fails
        """
        creds = None

        # Load existing token if available
        if self.token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
                print("[CONFIG] Using existing authentication token")
            except Exception as e:
                print(f"[WARN]  Existing token invalid: {e}")
                creds = None

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("[REFRESH] Refreshing expired authentication token...")
                try:
                    creds.refresh(Request())
                    print("[OK] Token refreshed successfully")
                except Exception as e:
                    print(f"[WARN]  Token refresh failed: {e}")
                    creds = None

            # If still no valid creds, run OAuth flow
            if not creds:
                print("[AUTH] Starting OAuth authentication flow...")
                print("   A browser window will open for Google authentication.")
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    print("[OK] Authentication successful")
                except Exception as e:
                    raise Exception(f"OAuth authentication failed: {e}")

            # Save credentials for next run
            try:
                with open(self.token_file, 'w', encoding='utf-8') as token:
                    token.write(creds.to_json())
                print(f"[SAVE] Authentication token saved to {self.token_file}")
            except Exception as e:
                print(f"[WARN]  Could not save token: {e}")

        # Build Sheets API service
        try:
            self.service = build('sheets', 'v4', credentials=creds)
            print("[OK] Connected to Google Sheets API")
        except Exception as e:
            raise Exception(f"Failed to connect to Google Sheets API: {e}")

    def _sanitize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sanitize DataFrame for Google Sheets upload.
        - Reindex to canonical column order
        - Remove "$" and "," from numeric columns
        - Convert all values to strings
        - Replace NaN/None with empty string
        - Trim whitespace from all fields

        Args:
            df: Input DataFrame

        Returns:
            Sanitized DataFrame with correct column order
        """
        # Reindex to canonical column order, filling missing columns with empty string
        df = df.reindex(columns=COLUMNS, fill_value="")

        # Replace NaN and None with empty string
        df = df.fillna("")

        # Sanitize numeric columns
        for col in NUMERIC_COLUMNS:
            if col in df.columns:
                df[col] = df[col].apply(self._sanitize_numeric)

        # Convert all values to strings and trim whitespace
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()

        # Replace "nan" strings (from str conversion) with empty string
        df = df.replace("nan", "")

        return df

    def _sanitize_numeric(self, value) -> str:
        """
        Sanitize numeric value for Google Sheets.
        - Remove "$" and "," characters
        - Convert to string
        - Handle None/NaN

        Args:
            value: Numeric value to sanitize

        Returns:
            Sanitized string value
        """
        if pd.isna(value) or value is None or value == "":
            return ""

        # Convert to string and remove currency/thousand separators
        value_str = str(value)
        value_str = value_str.replace("$", "").replace(",", "")

        return value_str.strip()

    def _verify_headers(self) -> Tuple[bool, List[str]]:
        """
        Verify that sheet headers match canonical column order exactly.

        Returns:
            Tuple of (headers_match: bool, existing_headers: List[str])

        Raises:
            Exception: If sheet access fails
        """
        try:
            # Read first row to check headers
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=f"{self.sheet_name}!A1:Z1"
            ).execute()

            existing_headers = result.get('values', [[]])[0] if 'values' in result else []

            # If sheet is empty, write headers
            if not existing_headers:
                print(f"[WRITE] Sheet is empty. Writing canonical headers...")
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.sheet_id,
                    range=f"{self.sheet_name}!A1",
                    valueInputOption='RAW',
                    body={'values': [COLUMNS]}
                ).execute()
                print(f"[OK] Headers written: {COLUMNS}")
                return True, COLUMNS

            # Verify headers match exactly
            headers_match = existing_headers == COLUMNS

            if headers_match:
                print(f"[OK] Header validation: OK")
            else:
                print(f"[ERROR] Header validation: MISMATCH")
                print(f"   Expected: {COLUMNS}")
                print(f"   Found:    {existing_headers}")

            return headers_match, existing_headers

        except HttpError as e:
            if e.resp.status == 404:
                raise Exception(
                    f"[ERROR] Sheet tab '{self.sheet_name}' not found. "
                    f"Please create a tab named '{self.sheet_name}' in your Google Sheet."
                )
            else:
                raise Exception(f"[ERROR] Failed to access sheet: {e}")

    def _get_next_row(self) -> int:
        """
        Detect the next available row by counting existing values in column A.

        Returns:
            Next row number (1-indexed for Google Sheets)

        Raises:
            Exception: If sheet access fails
        """
        try:
            # Fetch all values in column A
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=f"{self.sheet_name}!A:A"
            ).execute()

            existing_values = result.get('values', [])
            next_row = len(existing_values) + 1

            print(f"[ROW] Next available row: A{next_row}")
            return next_row

        except HttpError as e:
            if e.resp.status == 404:
                raise Exception(
                    f"[ERROR] Sheet tab '{self.sheet_name}' not found. "
                    f"Please create a tab named '{self.sheet_name}' in your Google Sheet."
                )
            else:
                raise Exception(f"[ERROR] Failed to detect next row: {e}")

    def append_data(self, df: pd.DataFrame) -> int:
        """
        Append DataFrame rows to Google Sheet with bulletproof alignment.

        Process:
        1. Sanitize DataFrame (reindex, clean data)
        2. Verify headers match canonical order
        3. Detect next available row
        4. Append data to specific range
        5. Use RAW value input to prevent auto-formatting

        Args:
            df: DataFrame with data to append

        Returns:
            Number of rows appended

        Raises:
            Exception: If append operation fails or headers mismatch
        """
        if df.empty:
            print("[WARN]  No data to append (DataFrame is empty)")
            return 0

        # Step 1: Sanitize DataFrame
        print(f"[CLEAN] Sanitizing {len(df)} row(s)...")
        df_clean = self._sanitize_dataframe(df)

        # Step 2: Verify headers
        headers_match, existing_headers = self._verify_headers()

        if not headers_match:
            raise Exception(
                f"[ERROR] Cannot append data: Header mismatch!\n"
                f"   Expected: {COLUMNS}\n"
                f"   Found:    {existing_headers}\n"
                f"   Please fix the Google Sheet headers to match exactly."
            )

        # Step 3: Detect next row
        next_row = self._get_next_row()

        # Step 4: Prepare data for upload
        values = df_clean.values.tolist()

        # Step 5: Append to specific range
        try:
            range_name = f"{self.sheet_name}!A{next_row}"
            print(f"📤 Appending {len(values)} row(s) starting at {range_name}...")

            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={'values': values}
            ).execute()

            rows_written = result.get('updatedRows', 0)
            print(f"[OK] Write complete: {rows_written} row(s) appended")

            return rows_written

        except HttpError as e:
            if e.resp.status == 429:
                raise Exception(
                    "[ERROR] Google Sheets API quota exceeded. Please try again later or "
                    "increase your API quota in Google Cloud Console."
                )
            elif e.resp.status == 403:
                raise Exception(
                    "[ERROR] Permission denied. Please ensure you have edit access to the "
                    "Google Sheet and that the Sheets API is enabled."
                )
            elif e.resp.status == 404:
                raise Exception(
                    f"[ERROR] Sheet tab '{self.sheet_name}' not found. "
                    f"Please verify the sheet name in config.json."
                )
            else:
                raise Exception(f"[ERROR] Failed to append data: {e}")

    def write_dataframe(self, df: pd.DataFrame) -> int:
        """
        Main method to write DataFrame to Google Sheets.
        Handles authentication, header verification, and data append.

        Args:
            df: DataFrame with data to write

        Returns:
            Number of rows written

        Raises:
            Exception: If any step fails
        """
        if df.empty:
            print("[WARN]  No data to write (DataFrame is empty)")
            return 0

        # Authenticate if not already authenticated
        if self.service is None:
            self.authenticate()

        # Append data (includes all validation steps)
        rows_written = self.append_data(df)

        return rows_written


def test_sheets_writer(config_loader):
    """
    Test Google Sheets writer with sample data.

    Args:
        config_loader: ConfigLoader instance

    Returns:
        True if test succeeds, False otherwise
    """
    try:
        # Get Google Sheets config
        if 'google_sheets' not in config_loader.config:
            print("[ERROR] Google Sheets configuration not found in config.json")
            return False

        gs_config = config_loader.config['google_sheets']

        # Initialize writer
        print("\n" + "=" * 80)
        print("Testing Google Sheets Writer (Enhanced)")
        print("=" * 80 + "\n")

        writer = SheetsWriter(
            sheet_id=gs_config['sheet_id'],
            credentials_file=gs_config['credentials_file'],
            token_file=gs_config['token_file'],
            sheet_name=gs_config['sheet_name']
        )

        # Create sample DataFrame with all canonical columns
        sample_data = pd.DataFrame({
            'vendor_sku': ['TEST123'],
            'description': ['Test Item'],
            'quantity': [10.0],
            'unit_cost': ['$5.50'],  # Test with $ symbol
            'total_cost': ['55.00'],
            'supplier': ['Test Supplier'],
            'invoice_number': ['TEST-001'],
            'invoice_date': ['2024-10-27'],
            'variance_%': [''],  # Empty for now
            'variance_flag': [''],  # Empty for now
            'source_file': ['test.pdf'],
            'processed_date': ['2024-10-27 12:00:00']
        })

        print("\nTest Data (before sanitization):")
        print(sample_data.to_string(index=False))
        print()

        # Write to Google Sheets
        rows = writer.write_dataframe(sample_data)

        print("\n" + "=" * 80)
        if rows > 0:
            print(f"[OK] TEST PASSED - {rows} row(s) written to Google Sheet")
            print(f"   Sheet ID: {gs_config['sheet_id']}")
            print(f"   Sheet Name: {gs_config['sheet_name']}")
            print(f"   Column Order: {COLUMNS}")
        else:
            print("[ERROR] TEST FAILED - No rows written")
        print("=" * 80)

        return rows > 0

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test with config loader
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from config_loader import ConfigLoader

    print("=" * 80)
    print("GOOGLE SHEETS WRITER TEST (ENHANCED)")
    print("=" * 80)

    config = ConfigLoader()
    success = test_sheets_writer(config)

    print("\n" + "=" * 80)
    if success:
        print("[OK] Google Sheets integration ready")
    else:
        print("[ERROR] Google Sheets integration failed - please review errors above")
    print("=" * 80)
