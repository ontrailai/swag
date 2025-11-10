"""
Swag Golf Pricing Intelligence Tool - Main Entry Point
Processes invoice PDFs and writes pricing data to Google Sheets.
"""

import sys
import shutil
import os
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config_loader import ConfigLoader
from invoice_extractor import InvoiceExtractor
from sheets_writer import SheetsWriter
from variance_engine import VarianceEngine


def move_processed_file(pdf_path: Path, processed_dir: Path) -> bool:
    """
    Move successfully processed PDF to archive folder.

    Args:
        pdf_path: Path to PDF file to move
        processed_dir: Destination directory

    Returns:
        True if move succeeded, False otherwise
    """
    try:
        # Ensure processed directory exists
        processed_dir.mkdir(parents=True, exist_ok=True)

        # Destination path
        dest_path = processed_dir / pdf_path.name

        # If file already exists, append timestamp
        if dest_path.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            stem = pdf_path.stem
            suffix = pdf_path.suffix
            dest_path = processed_dir / f"{stem}_{timestamp}{suffix}"

        # Move file
        shutil.move(str(pdf_path), str(dest_path))
        print(f"[MOVE] Moved {pdf_path.name} → {processed_dir.name}/")
        return True

    except Exception as e:
        print(f"[WARN]  Failed to move {pdf_path.name}: {e}")
        return False


def run_pipeline():
    """
    Run the complete processing pipeline.

    Returns:
        dict: Processing results with structure:
            {
                'success': bool,
                'total_files': int,
                'successful_files': list,
                'failed_files': list,
                'moved_files': list,
                'total_rows_written': int,
                'variance_counts': dict,
                'sheet_url': str,
                'error': str (if any)
            }
    """
    results = {
        'success': False,
        'total_files': 0,
        'successful_files': [],
        'failed_files': [],
        'moved_files': [],
        'total_rows_written': 0,
        'variance_counts': {'GREEN': 0, 'YELLOW': 0, 'RED': 0},
        'sheet_url': '',
        'error': None
    }

    # Step 1: Load Configuration
    print("[CONFIG] Loading configuration...")
    try:
        config = ConfigLoader()
        print("[OK] Configuration loaded successfully\n")
    except Exception as e:
        print(f"[ERROR] Configuration error: {e}")
        results['error'] = f"Configuration error: {e}"
        return results

    # Step 2: Initialize Azure Extractor
    print("[CONNECT] Connecting to Azure Form Recognizer...")
    try:
        extractor = InvoiceExtractor(
            endpoint=config.get_azure_endpoint(),
            key=config.get_azure_key()
        )
        print("[OK] Connected to Azure Form Recognizer\n")
    except Exception as e:
        print(f"[ERROR] Azure connection failed: {e}")
        results['error'] = f"Azure connection failed: {e}"
        return results

    # Step 3: Initialize Google Sheets Writer
    print("[CONNECT] Connecting to Google Sheets...")
    try:
        gs_config = config.config.get('google_sheets', {})
        writer = SheetsWriter(
            sheet_id=gs_config.get('sheet_id', ''),
            credentials_file=gs_config.get('credentials_file', 'credentials.json'),
            token_file=gs_config.get('token_file', 'token.json'),
            sheet_name=gs_config.get('sheet_name', 'Pricing Data')
        )
        writer.authenticate()
        print("[OK] Connected to Google Sheets\n")

        # Build sheet URL
        sheet_id = gs_config.get('sheet_id', '')
        results['sheet_url'] = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
    except Exception as e:
        print(f"[ERROR] Google Sheets connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure credentials.json exists in project root")
        print("2. Verify Google Sheet ID in config.json")
        print("3. Check that you have edit access to the sheet")
        results['error'] = f"Google Sheets connection failed: {e}"
        return results

    # Step 4: Get list of invoices to process
    print("📂 Scanning for invoice PDFs...")
    pdf_files = config.list_new_invoices()

    if not pdf_files:
        print("[WARN]  No PDF files found in Invoices/new/")
        print("   Please add invoice PDFs to process.")
        results['error'] = "No PDF files found in Invoices/new/"
        return results

    results['total_files'] = len(pdf_files)
    print(f"[OK] Found {len(pdf_files)} PDF(s) to process\n")

    # Step 4: Initialize Variance Engine
    print("🧠 Initializing Variance Intelligence Engine...")
    try:
        variance_engine = VarianceEngine(
            green_threshold=config.get_variance_threshold('green'),
            yellow_threshold=config.get_variance_threshold('yellow'),
            rolling_window=3,
            supplier_window=30
        )
        print("[OK] Variance Engine initialized\n")
    except Exception as e:
        print(f"[ERROR] Variance Engine initialization failed: {e}")
        results['error'] = f"Variance Engine initialization failed: {e}"
        return results

    # Step 5: Get processed directory path
    processed_dir = config.get_path('invoices_processed')

    # Step 6: Process each invoice
    for idx, pdf_path in enumerate(pdf_files, 1):
        print(f"\n{'='*80}")
        print(f"Processing {idx}/{len(pdf_files)}: {pdf_path.name}")
        print(f"{'='*80}")

        try:
            # Extract data from PDF
            df = extractor.extract_invoice(pdf_path)

            if df.empty:
                print(f"[WARN]  No data extracted from {pdf_path.name}")
                results['failed_files'].append((pdf_path.name, "No data extracted"))
                continue

            # Annotate with variance intelligence
            print(f"\n🧠 Running Variance Intelligence Engine...")
            df = variance_engine.annotate_invoice_data(
                df,
                writer.service,
                gs_config.get('sheet_id'),
                gs_config.get('sheet_name')
            )

            # Count variance flags in this invoice
            for flag in df.get('variance_flag', []):
                if flag in results['variance_counts']:
                    results['variance_counts'][flag] += 1

            # Write to Google Sheets
            print(f"\n📤 Writing to Google Sheets...")
            rows_written = writer.append_data(df)

            if rows_written > 0:
                results['total_rows_written'] += rows_written
                results['successful_files'].append(pdf_path.name)
                print(f"[OK] {pdf_path.name} processed successfully")

                # Move file to processed directory
                if move_processed_file(pdf_path, processed_dir):
                    results['moved_files'].append(pdf_path.name)
            else:
                results['failed_files'].append((pdf_path.name, "Failed to write to sheet"))
                print(f"[ERROR] Skipped moving {pdf_path.name} due to processing failure")

        except Exception as e:
            print(f"[ERROR] Error processing {pdf_path.name}: {e}")
            results['failed_files'].append((pdf_path.name, str(e)))
            print(f"[ERROR] Skipped moving {pdf_path.name} due to processing failure")
            continue

    # Step 7: Summary
    print("\n" + "=" * 80)
    print("PROCESSING SUMMARY")
    print("=" * 80)
    print(f"Total PDFs processed: {results['total_files']}")
    print(f"Successful: {len(results['successful_files'])}")
    print(f"Failed: {len(results['failed_files'])}")
    print(f"Total rows written to Google Sheets: {results['total_rows_written']}")
    print(f"[MOVE] Files moved to archive: {len(results['moved_files'])} / {results['total_files']}")

    if results['successful_files']:
        print("\n[OK] Successfully processed:")
        for filename in results['successful_files']:
            moved_status = "→ Archived" if filename in results['moved_files'] else ""
            print(f"   - {filename} {moved_status}")

    if results['failed_files']:
        print("\n[ERROR] Failed to process (kept in Invoices/new/):")
        for filename, error in results['failed_files']:
            print(f"   - {filename}: {error}")

    print("\n" + "=" * 80)

    results['success'] = len(results['successful_files']) > 0
    return results


def main():
    """
    Main entry point for command-line execution.
    """
    print("=" * 80)
    print("SWAG GOLF PRICING INTELLIGENCE TOOL")
    print("=" * 80)
    print()

    results = run_pipeline()
    return results['success']


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN]  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
