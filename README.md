# Swag Golf Pricing Intelligence Tool

**Automated invoice processing with Azure AI and Google Sheets integration**

## ✨ Features

- 📄 **PDF Invoice Extraction** - Azure Form Recognizer extracts pricing data automatically
- 📊 **Google Sheets Integration** - Appends data directly to Google Sheets
- 🔐 **Secure Authentication** - OAuth2 for Google Sheets, Azure API for document processing
- 🛡️ **Error Handling** - Graceful handling of missing fields and API errors
- 📈 **Batch Processing** - Process multiple invoices in one run

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Google Sheets

1. **Create credentials:** Download `credentials.json` from [Google Cloud Console](https://console.cloud.google.com/)
2. **Update config:** Add your Google Sheet ID to `config.json`
3. **See full setup:** Read `SETUP_GUIDE.md` for detailed instructions

### 3. Run the Tool

```bash
# Place invoice PDFs in Invoices/new/
python main.py
```

---

## 📋 Configuration

Edit `config.json`:

```json
{
  "google_sheets": {
    "sheet_id": "YOUR_GOOGLE_SHEET_ID",
    "sheet_name": "Pricing Data"
  }
}
```

**Azure credentials are pre-configured.**

---

## 🧪 Testing

```bash
# Test Azure extraction
python test_step2.py

# Test Google Sheets integration
python test_sheets.py
```

---

## 📊 Data Output

Each invoice line item creates a row with:

- `vendor_sku` - Product SKU
- `description` - Item name
- `quantity` - Quantity ordered
- `unit_cost` - Price per unit
- `total_cost` - Total line cost
- `supplier` - Vendor name
- `invoice_number` - Invoice ID
- `invoice_date` - Invoice date
- `source_file` - PDF filename
- `processed_date` - Processing timestamp

---

## 📁 Project Structure

```
SwagInvoice/
├── main.py                 # Main entry point
├── config.json            # Configuration
├── credentials.json       # Google OAuth (you create)
├── requirements.txt       # Dependencies
├── SETUP_GUIDE.md        # Detailed setup instructions
├── Invoices/
│   └── new/              # Drop PDFs here
└── src/
    ├── config_loader.py       # Config management
    ├── invoice_extractor.py   # Azure extraction
    └── sheets_writer.py       # Google Sheets API
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "credentials.json not found" | Download from Google Cloud Console |
| "Sheet ID not configured" | Update `sheet_id` in `config.json` |
| "No PDFs found" | Place PDFs in `Invoices/new/` |
| "Permission denied" | Ensure edit access to Google Sheet |

**Full troubleshooting guide:** See `SETUP_GUIDE.md`

---

## 🔐 Security

- `credentials.json` - OAuth client config (not sensitive for Desktop apps)
- `token.json` - Your access token (keep private, auto-generated)
- **Do not commit:** `credentials.json`, `token.json` to version control

---

## 🛠️ Development Status

### ✅ Completed (Steps 1-3)
- [x] Environment & configuration system
- [x] Azure Form Recognizer integration
- [x] Google Sheets API integration
- [x] OAuth2 authentication flow
- [x] Basic batch processing

### 🔄 Planned (Steps 4-7)
- [ ] Variance detection with color-coding
- [ ] File archiving and logging
- [ ] Duplicate prevention
- [ ] Executable packaging

---

## 📖 Documentation

- **Quick Start:** This README
- **Full Setup:** `SETUP_GUIDE.md` (detailed step-by-step)
- **Code Documentation:** Inline comments in `src/` modules

---

## 🎯 Usage Example

```bash
# 1. Place invoices in folder
cp ~/Downloads/invoice*.pdf Invoices/new/

# 2. Run processor
python main.py

# 3. Check Google Sheet
# Data automatically appended!
```

---

## 📞 Support

For setup assistance, refer to:
- `SETUP_GUIDE.md` - Comprehensive setup instructions
- [Google Sheets API Docs](https://developers.google.com/sheets/api)
- [Azure Form Recognizer Docs](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)

---

**Built with:** Python 3.10+ | Azure AI | Google Sheets API
