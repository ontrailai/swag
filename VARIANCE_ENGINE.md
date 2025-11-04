# Variance Intelligence Engine (V2) - Documentation

## 🎯 Overview

The Variance Intelligence Engine transforms raw invoice data into actionable business intelligence using rolling statistics, supplier baselines, and cost impact scoring.

**Key Capabilities:**
- 📊 Rolling average cost tracking (last 3 invoices per SKU)
- 🏢 Supplier-level baseline variance patterns
- 💰 Dollar impact scoring for prioritization
- 🚦 Intelligent flagging (🟢 🟡 🔴) based on business thresholds
- 🔺 Automatic prioritization of high-impact variances

---

## 📋 New Schema Fields

### Added Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `variance_%` | Float | Rolling variance from 3-invoice average | `+12.5` |
| `variance_flag` | Emoji | Visual flag: 🟢 ≤3%, 🟡 ≤10%, 🔴 >10% | `🔴` |
| `supplier_baseline_%` | Float | Supplier's historical avg variance | `4.8` |
| `impact_$` | Float | Dollar impact = (new - old) × quantity | `+850.00` |

### Updated Canonical Column Order

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
    "variance_%",          # ← NEW
    "variance_flag",       # ← NEW
    "supplier_baseline_%", # ← NEW
    "impact_$",            # ← NEW
    "source_file",
    "processed_date"
]
```

---

## 🧮 Calculation Methodology

### 1. **Rolling Average Baseline**

**Purpose:** Smooth out single-invoice noise by using recent pricing history.

**Algorithm:**
```python
# For each SKU, get last 3 invoices sorted by date
sku_history = historical_df[historical_df['vendor_sku'] == sku]
recent_3 = sku_history.tail(3)

rolling_avg_cost = recent_3['unit_cost'].mean()
rolling_median_cost = recent_3['unit_cost'].median()
```

**Example:**
```
SKU: ABC123
Invoice 1: $10.00 (2024-01-01)
Invoice 2: $10.50 (2024-02-01)
Invoice 3: $11.00 (2024-03-01)
→ Rolling Avg: $10.50
→ Rolling Median: $10.50

New Invoice: $12.00 (2024-04-01)
→ Variance: ((12.00 - 10.50) / 10.50) × 100 = +14.29%
```

---

### 2. **Supplier Baseline Variance**

**Purpose:** Understand if a supplier historically has volatile pricing.

**Algorithm:**
```python
# Get supplier's last 30 historical records
supplier_history = historical_df[historical_df['supplier'] == supplier]
last_30 = supplier_history.tail(30)

# Average of absolute variance percentages
supplier_baseline_% = last_30['variance_%'].abs().mean()
```

**Use Case:**
- Supplier A: baseline 2.5% → Very stable
- Supplier B: baseline 8.0% → Volatile pricing
- **Insight:** 10% variance from Supplier B is normal; from Supplier A is concerning

---

### 3. **Variance Percentage**

**Formula (Rolling-based):**
```python
variance_% = ((new_unit_cost - rolling_avg_cost) / rolling_avg_cost) × 100
```

**Fallback (if <3 historical invoices):**
```python
variance_% = ((new_unit_cost - last_cost) / last_cost) × 100
```

**Rounding:** 2 decimal places

**Example:**
```
Rolling Avg: $10.50
New Cost: $12.00
Variance: ((12.00 - 10.50) / 10.50) × 100 = +14.29%
```

---

### 4. **Impact Scoring**

**Impact in Dollars:**
```python
impact_$ = (new_unit_cost - last_cost) × quantity
```

**Impact Score (for sorting):**
```python
impact_score = abs(variance_%) × quantity
```

**Example:**
```
Last Cost: $10.00
New Cost: $12.00
Quantity: 500

Impact $: (12.00 - 10.00) × 500 = $1,000.00
Impact Score: 20% × 500 = 10,000
```

**Why This Matters:**
- SKU A: +50% variance on 10 units = $50 impact → Low priority
- SKU B: +5% variance on 5000 units = $2,500 impact → High priority

---

### 5. **Flag Assignment Logic**

**Thresholds (from config.json):**
```json
{
  "variance_thresholds": {
    "green": 3.0,
    "yellow": 10.0
  }
}
```

**Logic:**
```python
abs_variance = abs(variance_%)

if abs_variance <= 3.0:
    flag = '🟢'  # Within normal range
elif abs_variance <= 10.0:
    flag = '🟡'  # Moderate variance
else:
    flag = '🔴'  # High variance - investigate
```

**No History:** If SKU has never been ordered before, `variance_%` and `variance_flag` are blank.

---

## 🔺 Prioritization Logic

**Process:**
1. Identify all 🔴 flagged items
2. Sort by `impact_$` descending (highest $ impact first)
3. Log high-impact variances to console
4. Reorder DataFrame so red flags appear first in Google Sheet

**Console Output Example:**
```
🔺 HIGH-IMPACT VARIANCES DETECTED:
   SKU 6015364: +12.3%, $+850.00 impact
   SKU 7890123: +15.7%, $+620.50 impact
   SKU 4567890: -8.9%, $-340.25 impact
```

---

## 📊 Data Flow

```
PDF Invoice
    ↓
Azure Extraction (raw data)
    ↓
Variance Engine: Load Historical Data from Google Sheets
    ↓
Variance Engine: Calculate Rolling Averages (3-invoice window)
    ↓
Variance Engine: Calculate Supplier Baselines (30-invoice window)
    ↓
Variance Engine: Compute Variance % & Impact $
    ↓
Variance Engine: Assign Flags (🟢 🟡 🔴)
    ↓
Variance Engine: Prioritize High Impact (sort by impact_$)
    ↓
Google Sheets Writer: Append Annotated Data
    ↓
Google Sheet Updated with Intelligence
```

---

## 🧪 Testing

### Standalone Test

```bash
python src/variance_engine.py
```

**What It Tests:**
- Rolling average calculations
- Supplier baseline calculations
- Variance percentage calculations
- Flag assignment logic
- Impact scoring
- Prioritization

**Expected Output:**
```
================================================================================
VARIANCE ENGINE TEST
================================================================================

Calculating rolling statistics...
✅ Calculated rolling averages for 2 SKU(s)

Calculating supplier baselines...
✅ Applied supplier baselines for 2 row(s)

Calculating variance and impact...
✅ Calculated variance and impact scores for 3 row(s)

Assigning flags...
✅ Assigned flags: 🔴 1 🟡 1

Prioritizing high impact...

Annotated Data:
vendor_sku  unit_cost  variance_% variance_flag  supplier_baseline_%  impact_$
    SKU001      12.00        9.09            🟡                 4.88    100.00
    SKU002       5.10       -1.92            🟢                 4.00     -5.00
    SKU003       8.00

✅ Test complete
```

---

### Integration Test

```bash
python main.py
```

**Expected Workflow:**
```
================================================================================
SWAG GOLF PRICING INTELLIGENCE TOOL
================================================================================

📋 Loading configuration...
✅ Configuration loaded successfully

🔗 Connecting to Azure Form Recognizer...
✅ Connected to Azure Form Recognizer

🔗 Connecting to Google Sheets...
✅ Connected to Google Sheets

🧠 Initializing Variance Intelligence Engine...
✅ Variance Engine initialized

📂 Scanning for invoice PDFs...
✅ Found 1 PDF(s) to process

================================================================================
Processing 1/1: invoice.pdf
================================================================================
📄 Processing: invoice.pdf
  ✅ Extracted 5 line items

🧠 Running Variance Intelligence Engine...

================================================================================
VARIANCE INTELLIGENCE ENGINE (V2)
================================================================================

📊 Loading historical data from Google Sheets...
✅ Loaded 23 historical rows from Google Sheet

📈 Calculating rolling averages and medians...
✅ Calculated rolling averages for 4 SKU(s)

🏢 Calculating supplier-level baselines...
✅ Applied supplier baselines for 5 row(s)

🧮 Calculating variance percentages and impact scores...
✅ Calculated variance and impact scores for 5 row(s)

🚦 Assigning variance flags...
✅ Assigned flags: 🟢 3 🟡 1 🔴 1

🎯 Prioritizing high-impact variances...

🔺 HIGH-IMPACT VARIANCES DETECTED:
   SKU 6015364: +12.3%, $+850.00 impact

================================================================================
✅ Variance analysis complete: 5 annotated rows ready
================================================================================

📤 Writing to Google Sheets...
🧹 Sanitizing 5 row(s)...
✅ Header validation: OK
📍 Next available row: A24
📤 Appending 5 row(s) starting at Pricing Data!A24...
✅ Write complete: 5 row(s) appended
✅ invoice.pdf processed successfully

================================================================================
PROCESSING SUMMARY
================================================================================
Total PDFs processed: 1
Successful: 1
Failed: 0
Total rows written to Google Sheets: 5

✅ Successfully processed:
   - invoice.pdf

================================================================================
```

---

## ⚙️ Configuration

**File:** `config.json`

```json
{
  "variance_thresholds": {
    "green": 3.0,
    "yellow": 10.0
  }
}
```

**Parameters:**
- `green`: Threshold for 🟢 flag (default: 3.0%)
- `yellow`: Threshold for 🟡 flag (default: 10.0%)
- Anything > yellow → 🔴

**Customization Example:**
```json
{
  "variance_thresholds": {
    "green": 5.0,    // More lenient
    "yellow": 15.0   // More lenient
  }
}
```

---

## 🛡️ Edge Cases & Error Handling

### No Historical Data

**Scenario:** First time ordering a SKU

**Behavior:**
- `variance_%` → blank
- `variance_flag` → blank
- `supplier_baseline_%` → blank (if <3 supplier invoices)
- `impact_$` → blank

**Rationale:** Can't calculate variance without historical baseline

---

### Insufficient History (<3 invoices)

**Scenario:** SKU has only 1-2 previous orders

**Behavior:**
- Use simple variance (last cost vs new cost)
- No rolling average
- Flag still assigned based on simple variance

---

### Missing or Invalid Data

**Scenario:** `unit_cost` is blank or $0.00

**Behavior:**
- Skip variance calculation for that row
- Set variance columns to blank
- Continue processing other rows

---

### Supplier with No History

**Scenario:** New supplier, first invoice

**Behavior:**
- `supplier_baseline_%` → blank
- Variance still calculated based on SKU history (if available)

---

## 📈 Business Use Cases

### Use Case 1: Cost Increase Alert

**Scenario:**
- SKU: Golf Club Grip
- Historical avg: $2.50
- New cost: $3.00
- Quantity: 2,000

**Output:**
```
variance_%: +20.0%
variance_flag: 🔴
impact_$: +$1,000.00
```

**Action:** Investigate with supplier, negotiate, or find alternative

---

### Use Case 2: Normal Fluctuation

**Scenario:**
- SKU: Shipping Box
- Historical avg: $1.00
- New cost: $1.02
- Quantity: 500

**Output:**
```
variance_%: +2.0%
variance_flag: 🟢
impact_$: +$10.00
```

**Action:** No action needed, within normal range

---

### Use Case 3: High-Volume Moderate Variance

**Scenario:**
- SKU: Golf Ball (bulk)
- Historical avg: $0.50
- New cost: $0.53
- Quantity: 50,000

**Output:**
```
variance_%: +6.0%
variance_flag: 🟡
impact_$: +$1,500.00
```

**Action:** Moderate priority - review at next supplier meeting

---

## 🔧 Maintenance

### Adding New Thresholds

**Example: Add "critical" threshold**

1. Update `config.json`:
```json
{
  "variance_thresholds": {
    "green": 3.0,
    "yellow": 10.0,
    "critical": 25.0
  }
}
```

2. Update `variance_engine.py` flag logic:
```python
if abs_variance <= self.green_threshold:
    flag = '🟢'
elif abs_variance <= self.yellow_threshold:
    flag = '🟡'
elif abs_variance <= self.critical_threshold:
    flag = '🔴'
else:
    flag = '🔥'  # Critical
```

---

### Adjusting Rolling Window

**Current:** 3 invoices

**To change:**
```python
variance_engine = VarianceEngine(
    rolling_window=5  # Use last 5 invoices instead
)
```

---

## 📊 Sample Output

**Google Sheet After Processing:**

| vendor_sku | description | quantity | unit_cost | variance_% | variance_flag | supplier_baseline_% | impact_$ |
|------------|-------------|----------|-----------|------------|---------------|-------------------|----------|
| SKU001 | Item A | 1000 | 12.50 | +15.2 | 🔴 | 4.5 | +1,320.00 |
| SKU002 | Item B | 500 | 8.00 | +8.5 | 🟡 | 6.2 | +392.50 |
| SKU003 | Item C | 250 | 5.00 | +2.1 | 🟢 | 3.8 | +25.75 |
| SKU004 | Item D | 100 | 15.00 | | | | |

**Interpretation:**
- SKU001: High variance, high impact → **Immediate review**
- SKU002: Moderate variance, moderate impact → **Monitor**
- SKU003: Low variance, low impact → **Normal**
- SKU004: New item, no history → **Establish baseline**

---

## ✅ Implementation Complete

**Files Modified:**
1. ✅ `src/variance_engine.py` - New module (450+ lines)
2. ✅ `src/sheets_writer.py` - Updated COLUMNS (added 2 fields)
3. ✅ `src/invoice_extractor.py` - Updated line_item dict (added 2 fields)
4. ✅ `main.py` - Integrated variance engine into pipeline

**New Capabilities:**
- ✅ Rolling average cost tracking
- ✅ Supplier baseline variance patterns
- ✅ Dollar impact scoring
- ✅ Intelligent flagging with emojis
- ✅ Automatic prioritization by impact
- ✅ Console logging with variance details

**Ready For:**
- ✅ Production use
- ✅ Business decision support
- ✅ Cost variance monitoring
- ✅ Supplier performance analysis

---

## 🚀 Next Steps

1. **Fix Google Sheet Headers:**
   - Delete row 1 (headers)
   - Run `python main.py`
   - System will auto-create correct headers

2. **Process First Invoice:**
   - Place PDF in `Invoices/new/`
   - Run `python main.py`
   - Check Google Sheet for variance intelligence

3. **Monitor Results:**
   - Look for 🔴 flags
   - Review high-impact variances
   - Track supplier baselines over time

---

**Documentation:** This file + `SHEETS_UPGRADE.md` + `SETUP_GUIDE.md`
**Test:** `python src/variance_engine.py`
**Run:** `python main.py`
