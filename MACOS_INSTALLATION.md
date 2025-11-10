# Swag Pricing Intelligence - macOS Installation Guide

## 📦 What You're Getting

**File**: `Swag Pricing Intelligence-1.0.0-arm64.dmg`
**Size**: ~103 MB
**Platform**: macOS (Apple Silicon - M1/M2/M3/M4)

---

## ⚠️ IMPORTANT: Prerequisites

Your Mac must have **Python 3.8 or newer** installed before running this application.

### 1️⃣ Check if Python is Installed

Open **Terminal** (Applications → Utilities → Terminal) and type:

```bash
python3 --version
```

**If Python is installed**, you'll see something like: `Python 3.10.5`

**If Python is NOT installed**, install it using Homebrew:

```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11
```

---

## 2️⃣ Install Required Python Packages

After Python is installed, open **Terminal** and run:

```bash
pip3 install fastapi uvicorn azure-ai-formrecognizer google-auth google-auth-oauthlib google-api-python-client pandas openpyxl
```

This will install all the necessary components for the application to work.

---

## 3️⃣ Install Swag Pricing Intelligence

### Download and Install

1. **Download**: Get `Swag Pricing Intelligence-1.0.0-arm64.dmg` from the release page
2. **Open the DMG**: Double-click the downloaded file
3. **Drag to Applications**: Drag `Swag Pricing Intelligence.app` to the Applications folder
4. **Eject the DMG**: Eject the disk image

### ⚠️ CRITICAL: Fix macOS Security Block

**Before launching the app**, you MUST run this command in Terminal:

```bash
xattr -cr "/Applications/Swag Pricing Intelligence.app"
```

**What this does**: Removes the quarantine flag that macOS applies to downloaded apps. Without this, you'll see **"App is damaged"** error.

---

## 4️⃣ First Time Setup

### Launch the Application

Now you can launch the app from:
- Applications folder
- Spotlight search (⌘ + Space, type "Swag")
- Launchpad

### Configuration Files

The application stores its configuration and data in:
```
~/Library/Application Support/swag-pricing-intelligence/
```

On first run, you'll need to configure:

1. **Google Sheets API** (if using Google Sheets integration)
   - Place your `credentials.json` file in the app data directory
   - The app will guide you through authentication

2. **Azure Form Recognizer** (if using invoice scanning)
   - Configure `config.json` with your Azure credentials

### Invoice Processing

The app will create these folders in the app data directory:
- `Invoices/new/` - Place new invoices here for processing
- `Invoices/processed/` - Processed invoices are moved here

---

## 🔧 Troubleshooting

### "App is damaged and can't be opened"

This is the most common issue - **the app is NOT damaged**, it's just macOS security being overly cautious.

**Fix**:
```bash
xattr -cr "/Applications/Swag Pricing Intelligence.app"
```

**Why this happens**: The app is not code-signed with an Apple Developer certificate ($99/year), so macOS marks it as "damaged" by default.

### Alternative Method

If the xattr command doesn't work:

1. **Disable Gatekeeper temporarily**:
   ```bash
   sudo spctl --master-disable
   ```

2. **Right-click the app** → Select **Open** (NOT double-click)

3. **Click "Open"** on the warning dialog

4. **Re-enable Gatekeeper**:
   ```bash
   sudo spctl --master-enable
   ```

### "Python not found" Error

- Install Python 3.8+ using Homebrew (see step 1)
- Make sure Python is in your PATH
- Try `python3` instead of `python`

### Application Won't Start

- Check Console.app (Applications → Utilities → Console) for error logs
- Ensure all Python packages are installed (see step 2)
- Verify Python path is correct

### Configuration Issues

- Locate the app data folder: `~/Library/Application Support/swag-pricing-intelligence/`
- Check that `config.json` and `credentials.json` are present
- Verify the format matches the template files

### Firewall Warnings

- The app runs a local web server (localhost:8000)
- Allow the application through macOS Firewall if prompted
- This is normal and safe - it only listens on localhost

---

## 🖥️ System Requirements

- **Mac**: Apple Silicon (M1, M2, M3, M4)
- **macOS**: 11.0 (Big Sur) or newer
- **RAM**: 4 GB minimum (8 GB recommended)
- **Disk Space**: 500 MB free space
- **Python**: Version 3.8 or newer
- **Internet**: Required for Google Sheets and Azure API access

---

## 📞 Support

For technical support or questions:
- Contact: Ryan Watson
- GitHub: https://github.com/ontrailai/swag/releases

---

## 🔄 Updates

To update the application:
1. Download the new DMG file
2. Drag the new app to Applications (replacing the old one)
3. Run the xattr command again if needed
4. Your configuration and data will be preserved

---

## 🗑️ Uninstalling

To remove the application:
1. Drag `Swag Pricing Intelligence.app` from Applications to Trash
2. Empty Trash

**Note**: Your configuration files and processed invoices will remain in:
`~/Library/Application Support/swag-pricing-intelligence/`

To completely remove all data:
```bash
rm -rf ~/Library/Application\ Support/swag-pricing-intelligence/
```

---

## 🔒 Security Note

**Why isn't the app code-signed?**

Apple Developer code signing requires a $99/year certificate. Since this is an internal business tool, we've opted not to purchase the certificate. The app is completely safe - you just need to tell macOS to trust it using the xattr command.

**Is it safe to disable Gatekeeper?**

Only temporarily and only for this specific app. We recommend using the xattr command instead, which is safer and more targeted.

---

**© 2025 Swag Golf | Developed by Ryan Watson**
