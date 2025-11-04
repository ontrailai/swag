# Swag Pricing Intelligence Tool - Streamlit UI Guide

## 🚀 Quick Start

### Launch the Application

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

---

## 📋 Features

### 1. **PDF Upload Interface**
- Upload single or multiple PDF invoices simultaneously
- Drag-and-drop support
- File size preview
- Automatic validation

### 2. **One-Click Processing**
- Single button to run complete pipeline:
  - Azure Form Recognizer extraction
  - Variance Intelligence Engine analysis
  - Google Sheets synchronization
  - Automatic file archiving

### 3. **Real-Time Progress**
- Live processing status with spinner
- Detailed console logs (expandable)
- Step-by-step progress updates

### 4. **Comprehensive Results Dashboard**
- **Processing Summary**: Total files, success/fail counts, rows written
- **Variance Alerts**: Visual indicators (🟢 🟡 🔴) with counts
- **Google Sheets Link**: Direct link to updated spreadsheet
- **File Status**: List of successful and failed files with details

### 5. **Recently Processed Files**
- View last 10 processed files
- Timestamps for each file
- Quick reference for recent activity

---

## 🎯 Workflow

### Step 1: Upload PDFs
1. Click "Browse files" or drag PDFs into the upload area
2. Review the list of uploaded files
3. Each file shows its size and name

### Step 2: Process & Sync
1. Click the **"🚀 Process & Sync to Google Sheets"** button
2. Wait for the processing pipeline to complete
3. Monitor real-time progress via spinner

### Step 3: Review Results
1. Check the **Processing Summary** metrics
2. Review **Variance Alerts** for pricing anomalies:
   - 🟢 **Green (≤3%)**: Normal pricing, no action needed
   - 🟡 **Yellow (≤10%)**: Moderate variance, review recommended
   - 🔴 **Red (>10%)**: High variance, investigate immediately
3. Click the **Google Sheets link** to view detailed data
4. Review successfully processed files (archived automatically)
5. Check failed files (kept in Invoices/new/ for review)

---

## 📊 Understanding Variance Alerts

### 🟢 Green Flag (≤3% variance)
- **Meaning**: Pricing is within normal range
- **Action**: No action required
- **Example**: Historical avg $10.00, current $10.25 (+2.5%)

### 🟡 Yellow Flag (≤10% variance)
- **Meaning**: Moderate variance detected
- **Action**: Review at next supplier meeting
- **Example**: Historical avg $10.00, current $10.80 (+8.0%)

### 🔴 Red Flag (>10% variance)
- **Meaning**: High variance detected
- **Action**: Investigate immediately with supplier
- **Example**: Historical avg $10.00, current $12.00 (+20.0%)
- **Impact Score**: Automatically prioritized by dollar impact

---

## 🔧 Configuration

The Streamlit UI uses the same `config.json` as the command-line version:

```json
{
  "azure": {
    "endpoint": "YOUR_AZURE_ENDPOINT",
    "key": "YOUR_AZURE_KEY"
  },
  "google_sheets": {
    "sheet_id": "YOUR_SHEET_ID",
    "credentials_file": "credentials.json",
    "token_file": "token.json",
    "sheet_name": "Pricing Data"
  },
  "variance_thresholds": {
    "green": 3.0,
    "yellow": 10.0
  }
}
```

---

## 📁 File Management

### Automatic File Organization
- **Upload**: Files saved to `Invoices/new/`
- **Processing**: System reads from `Invoices/new/`
- **Success**: Files moved to `Invoices/processed/`
- **Failure**: Files remain in `Invoices/new/` for review

### Recently Processed Files
- Displays last 10 files from `Invoices/processed/`
- Sorted by most recent first
- Shows filename and timestamp

---

## 🛠️ Troubleshooting

### Application won't start
```bash
# Ensure Streamlit is installed
pip install streamlit

# Verify installation
streamlit --version
```

### Upload fails
- Check that `Invoices/new/` directory exists (created automatically)
- Ensure sufficient disk space
- Verify PDF file is not corrupted

### Processing fails
1. Expand "View processing logs" to see detailed error
2. Common issues:
   - **Azure connection failed**: Check Azure credentials in `config.json`
   - **Google Sheets failed**: Ensure `credentials.json` and `token.json` exist
   - **No data extracted**: PDF may be scanned image (OCR quality issue)

### Google Sheets authentication
- First run may open browser for OAuth2 authentication
- Approve access to Google Sheets
- Token saved to `token.json` for future runs

---

## 🎨 UI Customization

### Custom Styling
The app includes custom CSS in `app.py`:
- Color scheme matching Swag Golf branding
- Responsive layout for different screen sizes
- Professional metric cards and panels

### Modify Thresholds
Edit `config.json` to adjust variance thresholds:
```json
{
  "variance_thresholds": {
    "green": 5.0,    // More lenient
    "yellow": 15.0   // More lenient
  }
}
```

---

## 📊 Output Explanation

### Metrics Panel
- **Total PDFs**: Number of files uploaded and processed
- **Successful**: Files processed and synced to Google Sheets
- **Failed**: Files that encountered errors
- **Rows Written**: Total line items added to Google Sheets

### Variance Counts
- Count of line items by variance severity
- Helps prioritize which invoices need attention
- Sorted by impact (highest impact shown first in Google Sheet)

### Google Sheets Link
- Direct link to your pricing data spreadsheet
- Opens in new tab
- Shows all historical data plus new invoices

---

## 🔄 Comparison: CLI vs UI

| Feature | Command Line (`python main.py`) | Streamlit UI (`streamlit run app.py`) |
|---------|----------------------------------|----------------------------------------|
| Upload PDFs | Manual file copy to `Invoices/new/` | Drag-and-drop upload interface |
| Processing | Terminal output only | Visual dashboard with metrics |
| Progress | Text-based logs | Real-time spinner + expandable logs |
| Results | Terminal summary | Rich dashboard with charts and links |
| File Management | Manual | Automatic with status indicators |
| User Experience | Technical users | Business users |

**Recommendation**: Use Streamlit UI for regular operations, CLI for automation/scripting.

---

## 🚦 Status Indicators

### Processing States
- **💾 Saving**: Uploaded files being saved to disk
- **🔄 Processing**: Pipeline running (extraction → variance → sync)
- **✅ Success**: All operations completed successfully
- **❌ Error**: Processing failed (see logs for details)

### Variance Indicators
- **🟢**: Low variance, no action needed
- **🟡**: Moderate variance, monitor
- **🔴**: High variance, investigate
- **📊**: Google Sheets link available
- **📦**: File archived successfully

---

## 📝 Notes

1. **Offline Processing**: Works fully offline except for Azure and Google Sheets API calls
2. **Multi-File Support**: Process multiple invoices in a single batch
3. **Session State**: Streamlit refreshes on each interaction (no persistent state)
4. **Log Capture**: Console logs captured and displayed in expandable section
5. **Relative Paths**: Uses relative paths for portability

---

## 🆘 Support

### Error Logs
- All errors shown in UI with expandable log viewer
- Console logs captured for debugging
- Failed files remain in `Invoices/new/` for review

### Common Issues
1. **ModuleNotFoundError**: Run `pip install -r requirements.txt`
2. **Credentials missing**: Ensure `credentials.json` exists
3. **Sheet not found**: Verify `sheet_id` in `config.json`
4. **Header mismatch**: Delete row 1 in Google Sheet for auto-generation

---

## 🎓 Best Practices

1. **Batch Processing**: Upload all invoices at once for efficiency
2. **Review Logs**: Always check logs after processing
3. **Monitor Variance**: Regularly review red flags
4. **Archive Management**: Periodically clean up `Invoices/processed/`
5. **Backup Data**: Google Sheets provides automatic backups

---

**Ready to start? Run `streamlit run app.py` and upload your first invoice!**
