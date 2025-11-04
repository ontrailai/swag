# Google Sheets Writer - Bulletproof Upgrade

## 🎯 Objective

Upgraded the Google Sheets writer to enforce perfect column alignment, prevent data misalignment, and ensure bulletproof appending without overwriting existing rows.

---

## ✨ Key Enhancements

### 1. **Canonical Column Order (COLUMNS constant)**

**Location:** `src/sheets_writer.py:24-37`

```python
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
    "source_file",
    "processed_date"
]
```

**Purpose:**
- Defines the exact column order for all data writes
- Acts as the single source of truth for schema
- All DataFrames are reindexed to match this order before writing

---

### 2. **Data Sanitization Pipeline**

**Method:** `_sanitize_dataframe()` at `src/sheets_writer.py:142-175`

**Process:**
1. **Reindex to canonical order** - Missing columns filled with empty string
2. **Replace NaN/None** - All null values become empty strings
3. **Sanitize numeric fields** - Remove "$" and "," from quantity, unit_cost, total_cost, variance_%
4. **Convert to strings** - All values converted to strings for consistent upload
5. **Trim whitespace** - All string fields have leading/trailing spaces removed
6. **Clean "nan" strings** - String conversion artifacts removed

**Example:**
```python
# Before sanitization
unit_cost = "$5.50"
quantity = 100.0
description = "  Widget  "

# After sanitization
unit_cost = "5.50"
quantity = "100.0"
description = "Widget"
```

---

### 3. **Strict Header Verification**

**Method:** `_verify_headers()` at `src/sheets_writer.py:199-249`

**Behavior:**
- **Empty sheet** → Writes canonical headers automatically
- **Headers match** → Proceeds with append
- **Headers mismatch** → **BLOCKS append** and throws clear error

**Error Example:**
```
❌ Cannot append data: Header mismatch!
   Expected: ['vendor_sku', 'description', 'quantity', ...]
   Found:    ['SKU', 'Item', 'Qty', ...]
   Please fix the Google Sheet headers to match exactly.
```

**Why This Matters:**
- Prevents data from landing in wrong columns
- Catches manual header edits immediately
- Forces schema consistency

---

### 4. **Next Row Detection**

**Method:** `_get_next_row()` at `src/sheets_writer.py:251-281`

**How It Works:**
1. Fetch ALL values in column A (first column)
2. Count rows: `next_row = len(existing_values) + 1`
3. Write to specific range: `Pricing Data!A{next_row}`

**Example:**
```
Sheet has rows 1-5 (header + 4 data rows)
Next row detected: A6
Append range: "Pricing Data!A6"
```

**Why This Matters:**
- Never overwrites existing data
- Works even if manual edits exist between rows
- Handles sparse data correctly

---

### 5. **RAW Value Input**

**Code:** `valueInputOption='RAW'` at `src/sheets_writer.py:336`

**Purpose:**
- Prevents Google Sheets from auto-formatting numbers
- "$5.50" stays as "5.50" (not converted to currency)
- "100" stays as text (not converted to number with locale formatting)
- Preserves exact data as uploaded

---

### 6. **Enhanced Logging**

**Console Output Shows:**
```
🧹 Sanitizing 5 row(s)...
✅ Header validation: OK
📍 Next available row: A23
📤 Appending 5 row(s) starting at Pricing Data!A23...
✅ Write complete: 5 row(s) appended
```

**Error Messages:**
```
❌ Header validation: MISMATCH
❌ Sheet tab 'Pricing Data' not found
❌ Google Sheets API quota exceeded
❌ Permission denied
```

---

## 📊 Data Flow

```
DataFrame Input
    ↓
Reindex to COLUMNS Order
    ↓
Sanitize Numeric Fields (remove $, ,)
    ↓
Convert All to Strings
    ↓
Trim Whitespace
    ↓
Verify Headers Match Exactly
    ↓
Detect Next Available Row
    ↓
Write to Specific Range with RAW Mode
    ↓
Success!
```

---

## 🔒 Safety Features

### 1. **Header Mismatch Protection**
- **Problem:** Manual header edits cause data misalignment
- **Solution:** Strict validation blocks writes if headers don't match exactly

### 2. **Overwrite Prevention**
- **Problem:** Append mode might overwrite if row detection fails
- **Solution:** Explicit row counting ensures writes always go to next empty row

### 3. **Data Corruption Prevention**
- **Problem:** Mixed data types cause formatting issues
- **Solution:** All values converted to clean strings before upload

### 4. **Schema Drift Protection**
- **Problem:** Missing columns or reordered columns break alignment
- **Solution:** DataFrame reindexed to canonical order every time

---

## 🧪 Testing

### Test Script: `test_sheets.py`

**What It Tests:**
1. Authentication flow
2. Header verification/creation
3. Data sanitization (tests "$5.50" → "5.50")
4. Column reordering
5. Next row detection
6. Write operation

**Run Test:**
```bash
python test_sheets.py
```

**Expected Output:**
```
================================================================================
Testing Google Sheets Writer (Enhanced)
================================================================================

📋 Using existing authentication token
✅ Connected to Google Sheets API

Test Data (before sanitization):
vendor_sku description  quantity unit_cost total_cost  ...
   TEST123   Test Item      10.0     $5.50      55.00  ...

🧹 Sanitizing 1 row(s)...
📝 Sheet is empty. Writing canonical headers...
✅ Headers written: ['vendor_sku', 'description', ...]
📍 Next available row: A2
📤 Appending 1 row(s) starting at Pricing Data!A2...
✅ Write complete: 1 row(s) appended

================================================================================
✅ TEST PASSED - 1 row(s) written to Google Sheet
   Sheet ID: 1zfLn_z8NdJFxBOHdFiAS7O41Fa9CntRmq0CB0Jx9onU
   Sheet Name: Pricing Data
   Column Order: ['vendor_sku', 'description', ...]
================================================================================
```

---

## 🔄 Integration with Main Pipeline

**File:** `main.py`

**No changes needed!** The main pipeline automatically benefits from the upgrade:

```python
# Extract data from PDF (includes variance columns now)
df = extractor.extract_invoice(pdf_path)

# Write to Google Sheets (automatically sanitized and aligned)
rows_written = writer.append_data(df)
```

---

## 📝 Schema Changes

### Updated invoice_extractor.py

**New Fields Added:**
- `variance_%` - Price variance percentage (None for now, populated in Step 4)
- `variance_flag` - Variance status flag (None for now, populated in Step 4)

**Location:** `src/invoice_extractor.py:162-163`

```python
line_item = {
    'vendor_sku': ...,
    'description': ...,
    ...
    'variance_%': None,      # ← NEW
    'variance_flag': None,   # ← NEW
    'source_file': ...,
    'processed_date': ...
}
```

---

## ⚙️ Configuration

### No Changes Needed

The existing `config.json` works with the upgraded system:

```json
{
  "google_sheets": {
    "sheet_id": "1zfLn_z8NdJFxBOHdFiAS7O41Fa9CntRmq0CB0Jx9onU",
    "sheet_name": "Pricing Data"
  }
}
```

---

## 🚨 Error Handling

### Common Errors and Solutions

**Error:** "Header validation: MISMATCH"
```
Expected: ['vendor_sku', 'description', 'quantity', ...]
Found:    ['SKU', 'Item', 'Qty', ...]
```
**Solution:** Update Google Sheet headers to match exactly, or delete row 1 to let the system write correct headers.

---

**Error:** "Sheet tab 'Pricing Data' not found"
**Solution:** Create a tab named "Pricing Data" in your Google Sheet, or update `sheet_name` in config.json.

---

**Error:** "Google Sheets API quota exceeded"
**Solution:** Wait and retry, or request quota increase in Google Cloud Console.

---

## 🎓 Best Practices

### 1. Never Manually Edit Headers
- Let the system write headers automatically
- If headers exist, they must match `COLUMNS` exactly

### 2. Manual Data Edits Are Safe
- You can manually edit data rows in Google Sheets
- The system will always append to the next empty row
- Data in existing rows won't be overwritten

### 3. Testing Before Production
- Always run `python test_sheets.py` after any changes
- Verify headers in Google Sheet match the canonical order
- Check that test data appears in correct columns

---

## 🔧 Maintenance

### Adding New Columns

**Steps:**
1. Update `COLUMNS` constant in `src/sheets_writer.py:24-37`
2. Update `NUMERIC_COLUMNS` if the new column needs sanitization
3. Add field to `invoice_extractor.py` line_item dict
4. Update Google Sheet headers manually OR delete row 1 to regenerate
5. Test with `python test_sheets.py`

**Example:**
```python
# Add "discount" column
COLUMNS = [
    "vendor_sku",
    "description",
    "quantity",
    "unit_cost",
    "discount",  # ← NEW
    "total_cost",
    ...
]

NUMERIC_COLUMNS = ["quantity", "unit_cost", "total_cost", "discount", "variance_%"]
```

---

## ✅ Upgrade Complete

**What Was Upgraded:**
- ✅ `src/sheets_writer.py` - Complete rewrite with bulletproof logic
- ✅ `src/invoice_extractor.py` - Added variance_% and variance_flag columns
- ✅ `test_sheets.py` - Enhanced test script with better output

**What Still Works:**
- ✅ `main.py` - No changes needed, automatically benefits
- ✅ `config.json` - No changes needed
- ✅ OAuth authentication flow
- ✅ Error handling and logging

**Ready For:**
- ✅ Step 4: Variance logic implementation
- ✅ Step 5: Batch processing and logging
- ✅ Step 6: Edge case hardening
- ✅ Step 7: Executable packaging

---

## 📞 Support

**Test the upgrade:**
```bash
python test_sheets.py
```

**Process invoices:**
```bash
python main.py
```

**Check Google Sheet:**
- Verify headers match canonical order
- Verify data appears in correct columns
- Verify no overwrites occurred

---

**Upgrade Status:** ✅ COMPLETE - Ready for production use
