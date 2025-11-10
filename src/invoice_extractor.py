"""
Invoice Extraction Module for Swag Golf Pricing Intelligence Tool
Uses Azure Form Recognizer (prebuilt-invoice) to extract structured data from invoice PDFs.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential


class InvoiceExtractor:
    """Extracts structured data from invoice PDFs using Azure Form Recognizer."""

    def __init__(self, endpoint: str, key: str):
        """
        Initialize Azure Form Recognizer client.

        Args:
            endpoint: Azure Form Recognizer endpoint URL
            key: Azure Form Recognizer API key
        """
        self.client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )

    def extract_invoice(self, pdf_path: Path) -> pd.DataFrame:
        """
        Extract invoice data from a single PDF file.

        Args:
            pdf_path: Path to PDF invoice file

        Returns:
            DataFrame with extracted line items containing:
            - vendor_sku: Product SKU/item number
            - description: Item description
            - quantity: Quantity ordered
            - unit_cost: Price per unit
            - total_cost: Total line item cost
            - supplier: Vendor/supplier name
            - invoice_number: Invoice identifier
            - invoice_date: Invoice date
            - variance_%: Price variance percentage (None for now)
            - variance_flag: Variance status flag (None for now)
            - source_file: Original PDF filename
            - processed_date: Timestamp of extraction

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If Azure extraction fails
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Invoice PDF not found: {pdf_path}")

        print(f"📄 Processing: {pdf_path.name}")

        try:
            # Read PDF file
            with open(pdf_path, "rb") as f:
                poller = self.client.begin_analyze_document(
                    "prebuilt-invoice", document=f
                )

            # Wait for analysis to complete
            result = poller.result()

            # Extract invoice-level data
            invoice_data = self._extract_invoice_metadata(result, pdf_path)

            # Extract line items
            line_items = self._extract_line_items(result, invoice_data)

            # Convert to DataFrame
            if line_items:
                df = pd.DataFrame(line_items)
                print(f"  [OK] Extracted {len(df)} line items")
                return df
            else:
                print("  [WARN] No line items found in invoice")
                return pd.DataFrame()

        except Exception as e:
            raise Exception(f"Azure extraction failed for {pdf_path.name}: {str(e)}")

    def _extract_invoice_metadata(self, result, pdf_path: Path) -> Dict:
        """
        Extract invoice-level metadata (supplier, invoice number, date).

        Args:
            result: Azure Form Recognizer result object
            pdf_path: Path to source PDF

        Returns:
            Dictionary with invoice metadata
        """
        metadata = {
            'supplier': None,
            'invoice_number': None,
            'invoice_date': None,
            'source_file': pdf_path.name,
            'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Process analyzed invoices
        for invoice in result.documents:
            fields = invoice.fields

            # Extract vendor/supplier name
            if 'VendorName' in fields and fields['VendorName'].value:
                raw_supplier = str(fields['VendorName'].value)
                metadata['supplier'] = raw_supplier.encode("utf-8", errors="ignore").decode("utf-8")

            # Extract invoice number
            if 'InvoiceId' in fields and fields['InvoiceId'].value:
                raw_invoice_id = str(fields['InvoiceId'].value)
                metadata['invoice_number'] = raw_invoice_id.encode("utf-8", errors="ignore").decode("utf-8")

            # Extract invoice date
            if 'InvoiceDate' in fields and fields['InvoiceDate'].value:
                invoice_date = fields['InvoiceDate'].value
                # Convert to string format
                if hasattr(invoice_date, 'strftime'):
                    metadata['invoice_date'] = invoice_date.strftime('%Y-%m-%d')
                else:
                    metadata['invoice_date'] = str(invoice_date)

        return metadata

    def _extract_line_items(self, result, invoice_metadata: Dict) -> List[Dict]:
        """
        Extract line items from invoice.

        Args:
            result: Azure Form Recognizer result object
            invoice_metadata: Invoice-level metadata

        Returns:
            List of dictionaries, each representing a line item
        """
        items = []

        for invoice in result.documents:
            fields = invoice.fields

            # Check if Items field exists
            if 'Items' not in fields or not fields['Items'].value:
                continue

            # Process each line item
            for item in fields['Items'].value:
                item_fields = item.value

                line_item = {
                    'vendor_sku': self._get_field_value(item_fields, 'ProductCode'),
                    'description': self._get_field_value(item_fields, 'Description'),
                    'quantity': self._get_numeric_value(item_fields, 'Quantity'),
                    'unit_cost': self._get_numeric_value(item_fields, 'UnitPrice'),
                    'total_cost': self._get_numeric_value(item_fields, 'Amount'),
                    'supplier': invoice_metadata['supplier'],
                    'invoice_number': invoice_metadata['invoice_number'],
                    'invoice_date': invoice_metadata['invoice_date'],
                    'variance_%': None,  # Calculated by Variance Engine
                    'variance_flag': None,  # Calculated by Variance Engine
                    'supplier_baseline_%': None,  # Calculated by Variance Engine
                    'impact_$': None,  # Calculated by Variance Engine
                    'source_file': invoice_metadata['source_file'],
                    'processed_date': invoice_metadata['processed_date']
                }

                # Calculate unit_cost if missing but total_cost and quantity available
                if (line_item['unit_cost'] is None and
                    line_item['total_cost'] is not None and
                    line_item['quantity'] is not None and
                    line_item['quantity'] > 0):
                    line_item['unit_cost'] = round(
                        line_item['total_cost'] / line_item['quantity'], 2
                    )

                # Calculate total_cost if missing but unit_cost and quantity available
                if (line_item['total_cost'] is None and
                    line_item['unit_cost'] is not None and
                    line_item['quantity'] is not None):
                    line_item['total_cost'] = round(
                        line_item['unit_cost'] * line_item['quantity'], 2
                    )

                items.append(line_item)

        return items

    def _get_field_value(self, fields: Dict, field_name: str) -> Optional[str]:
        """
        Safely extract string field value with UTF-8 sanitization.

        Args:
            fields: Field dictionary
            field_name: Name of field to extract

        Returns:
            Field value as string, or None if not found
        """
        if field_name in fields and fields[field_name].value:
            raw_value = str(fields[field_name].value)
            # Sanitize text: encode to UTF-8 with error handling, then decode
            # This removes any problematic surrogate pairs or invalid characters
            cleaned_value = raw_value.encode("utf-8", errors="ignore").decode("utf-8")
            return cleaned_value
        return None

    def _get_numeric_value(self, fields: Dict, field_name: str) -> Optional[float]:
        """
        Safely extract numeric field value.

        Args:
            fields: Field dictionary
            field_name: Name of field to extract

        Returns:
            Field value as float, or None if not found
        """
        if field_name in fields and fields[field_name].value is not None:
            try:
                value = fields[field_name].value
                # Handle currency values that might have currency code
                if hasattr(value, 'amount'):
                    return float(value.amount)
                return float(value)
            except (ValueError, TypeError):
                return None
        return None


def test_invoice_extractor(config_loader):
    """
    Test invoice extraction with first PDF in Invoices/new.

    Args:
        config_loader: ConfigLoader instance

    Returns:
        DataFrame with extracted data, or None if test fails
    """
    try:
        # Initialize extractor
        extractor = InvoiceExtractor(
            endpoint=config_loader.get_azure_endpoint(),
            key=config_loader.get_azure_key()
        )

        # Get first PDF from new invoices
        pdf_files = config_loader.list_new_invoices()
        if not pdf_files:
            print("[WARN] No PDF files found in Invoices/new")
            print("   Please add a test invoice PDF to continue.")
            return None

        # Process first PDF
        test_pdf = pdf_files[0]
        print(f"\n[CONFIG] Testing extraction with: {test_pdf.name}\n")

        df = extractor.extract_invoice(test_pdf)

        if df.empty:
            print("\n[ERROR] No data extracted from invoice")
            return None

        # Display results
        print("\n" + "=" * 80)
        print("EXTRACTED DATA PREVIEW:")
        print("=" * 80)
        print(df.to_string(index=False))
        print("=" * 80)
        print(f"\n[OK] Successfully extracted {len(df)} line items")

        return df

    except Exception as e:
        print(f"\n[ERROR] Extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test with config loader
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from config_loader import ConfigLoader

    print("=" * 80)
    print("STEP 2 TEST: Azure Invoice Extraction")
    print("=" * 80)

    config = ConfigLoader()
    result_df = test_invoice_extractor(config)

    print("\n" + "=" * 80)
    if result_df is not None:
        print("[OK] STEP 2 COMPLETE - Ready to proceed to Step 3")
    else:
        print("[ERROR] STEP 2 FAILED - Please review errors above")
    print("=" * 80)
