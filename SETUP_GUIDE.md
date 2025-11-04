# Swag Golf Pricing Intelligence Tool - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Google account with access to Google Sheets
- Azure Form Recognizer subscription

---

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `azure-ai-formrecognizer` - Azure Form Recognizer SDK
- `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client` - Google Sheets API
- `pandas`, `openpyxl` - Data processing

---

## 🔧 Configuration

### 2. Configure Azure Form Recognizer

The Azure credentials are already configured in `config.json`:
- Endpoint: `https://swag-docintelligence.cognitiveservices.azure.com/`
- API Key: Already set

✅ **No action needed for Azure**

---

### 3. Set Up Google Sheets

#### Step 3a: Create a Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Add a tab named **"Pricing Data"** (or your preferred name)
4. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
                                          ^^^^^^^^^^^^^^^^^^^
   ```

#### Step 3b: Enable Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **Google Sheets API**:
   - Navigate to **APIs & Services > Library**
   - Search for "Google Sheets API"
   - Click **Enable**

#### Step 3c: Create OAuth Credentials

1. In Google Cloud Console, go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Configure OAuth consent screen if prompted:
   - User Type: **External**
   - App name: "Swag Pricing Tool"
   - Add your email as test user
4. Application type: **Desktop app**
5. Name: "Swag Pricing Tool"
6. Click **Create**
7. Download the credentials JSON file
8. **Rename it to `credentials.json`** and place in project root

#### Step 3d: Update config.json

Edit `config.json` and update the Google Sheets section:

```json
{
  "google_sheets": {
    "sheet_id": "PASTE_YOUR_SHEET_ID_HERE",
    "credentials_file": "credentials.json",
    "token_file": "token.json",
    "sheet_name": "Pricing Data"
  }
}
```

---

## 🧪 Testing

### Test 1: Configuration & Azure Extraction

```bash
python test_step2.py
```

**Expected Output:**
- ✅ Configuration loaded
- ✅ Azure connection successful
- ✅ Invoice data extracted

---

### Test 2: Google Sheets Integration

```bash
python test_sheets.py
```

**What happens:**
1. Verifies Google Sheets configuration
2. Opens browser for Google authentication (first time only)
3. Creates `token.json` for future runs
4. Writes a test row to your Google Sheet

**Expected Output:**
- ✅ Authentication successful
- ✅ Test row written to Google Sheet

**Verify:** Check your Google Sheet for the test row.

---

## ▶️ Running the Tool

### Process Invoices

1. Place invoice PDF files in `Invoices/new/`
2. Run the main script:

```bash
python main.py
```

**What happens:**
1. Loads configuration
2. Connects to Azure Form Recognizer
3. Authenticates with Google Sheets
4. Processes each PDF in `Invoices/new/`
5. Extracts pricing data using Azure
6. Appends data to Google Sheet
7. Displays summary

**Output Example:**
```
==================================================================================
SWAG GOLF PRICING INTELLIGENCE TOOL
==================================================================================

📋 Loading configuration...
✅ Configuration loaded successfully

🔗 Connecting to Azure Form Recognizer...
✅ Connected to Azure Form Recognizer

🔗 Connecting to Google Sheets...
📋 Using existing authentication token
🔗 Connected to Google Sheets API
✅ Connected to Google Sheets

📂 Scanning for invoice PDFs...
✅ Found 1 PDF(s) to process

==================================================================================
Processing 1/1: Swag 251007(Lily) PO#003335 DraftKings Covers PI#223A.pdf
==================================================================================
📄 Processing: Swag 251007(Lily) PO#003335 DraftKings Covers PI#223A.pdf
  ✅ Extracted 1 line items

📤 Writing to Google Sheets...
📤 Appending 1 row(s) to Google Sheet...
✅ Successfully appended 1 row(s)
✅ Swag 251007(Lily) PO#003335 DraftKings Covers PI#223A.pdf processed successfully

==================================================================================
PROCESSING SUMMARY
==================================================================================
Total PDFs processed: 1
Successful: 1
Failed: 0
Total rows written to Google Sheets: 1

✅ Successfully processed:
   - Swag 251007(Lily) PO#003335 DraftKings Covers PI#223A.pdf

==================================================================================
```

---

## 📊 Data Schema

Each row appended to Google Sheets contains:

| Column | Description | Example |
|--------|-------------|---------|
| `vendor_sku` | Product SKU/item number | 6015364 |
| `description` | Item description | Draftkings Shamrock Blade |
| `quantity` | Quantity ordered | 100.0 |
| `unit_cost` | Price per unit | 8.0 |
| `total_cost` | Total line cost | 800.0 |
| `supplier` | Vendor/supplier name | Dongguan Kairay... |
| `invoice_number` | Invoice identifier | INV-2024-001 |
| `invoice_date` | Invoice date | 2025-10-07 |
| `source_file` | Original PDF filename | invoice.pdf |
| `processed_date` | Extraction timestamp | 2025-10-27 14:29:26 |

---

## 🔍 Troubleshooting

### Google Sheets Authentication Issues

**Problem:** "Permission denied" or "403 Forbidden"

**Solutions:**
1. Ensure you have **edit access** to the Google Sheet
2. Verify the Sheet ID in `config.json` is correct
3. Delete `token.json` and re-authenticate
4. Check that Google Sheets API is enabled in Google Cloud Console

---

### Missing credentials.json

**Problem:** "Google API credentials not found"

**Solutions:**
1. Download OAuth credentials from Google Cloud Console
2. Rename to `credentials.json`
3. Place in project root directory

---

### Azure Extraction Issues

**Problem:** "Azure extraction failed" or no data extracted

**Solutions:**
1. Verify PDF is a valid invoice format
2. Check Azure Form Recognizer quota in Azure Portal
3. Ensure Azure endpoint and key are correct in `config.json`

---

### No PDFs Found

**Problem:** "No PDF files found in Invoices/new/"

**Solutions:**
1. Verify PDFs are in `Invoices/new/` folder
2. Ensure files have `.pdf` extension (case-sensitive)
3. Check file permissions

---

## 🔐 Security Notes

- `credentials.json` contains OAuth client credentials (not sensitive if Desktop app)
- `token.json` contains your personal access token (keep private)
- Add to `.gitignore`: `credentials.json`, `token.json`
- Azure API keys should be kept secure and rotated periodically

---

## 📁 Project Structure

```
SwagInvoice/
├── config.json              # Configuration (Azure + Google Sheets)
├── credentials.json         # Google OAuth credentials (you create)
├── token.json              # Google auth token (auto-generated)
├── requirements.txt        # Python dependencies
├── main.py                 # Main entry point
├── test_step2.py          # Test Azure extraction
├── test_sheets.py         # Test Google Sheets integration
├── Invoices/
│   ├── new/               # Place PDFs here
│   └── processed/         # (Future: archived PDFs)
├── Output/                # (Future: local logs)
└── src/
    ├── config_loader.py   # Configuration loader
    ├── invoice_extractor.py  # Azure Form Recognizer integration
    └── sheets_writer.py   # Google Sheets writer
```

---

## 🎯 Next Steps

After completing this setup:

1. ✅ **Test the integration:** `python test_sheets.py`
2. ✅ **Process invoices:** Place PDFs in `Invoices/new/` and run `python main.py`
3. 🔄 **Verify results:** Check your Google Sheet for appended data

**Future enhancements (Steps 4-7):**
- Variance detection and color-coding
- Batch processing with file archiving
- Duplicate prevention
- Executable packaging

---

## 📞 Support

For issues or questions, contact the development team or refer to:
- [Google Sheets API Docs](https://developers.google.com/sheets/api)
- [Azure Form Recognizer Docs](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)
