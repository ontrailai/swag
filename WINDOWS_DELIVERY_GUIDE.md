# Swag Pricing Intelligence - Windows Installation Guide

## 📦 What You're Getting

**File**: `Swag Pricing Intelligence Setup 1.0.0.exe`
**Size**: ~91 MB
**Platform**: Windows 10/11 (64-bit)

---

## ⚠️ IMPORTANT: Prerequisites

Your Windows PC must have **Python 3.8 or newer** installed before running this application.

### 1️⃣ Check if Python is Installed

Open **Command Prompt** (search for `cmd` in Windows) and type:

```cmd
python --version
```

**If Python is installed**, you'll see something like: `Python 3.10.5`

**If Python is NOT installed**, download and install it from:
👉 [https://www.python.org/downloads/](https://www.python.org/downloads/)

**During Python installation, make sure to check the box that says:**
✅ **"Add Python to PATH"**

---

## 2️⃣ Install Required Python Packages

After Python is installed, open **Command Prompt** and run:

```cmd
pip install fastapi uvicorn azure-ai-formrecognizer google-auth google-auth-oauthlib google-api-python-client pandas openpyxl
```

This will install all the necessary components for the application to work.

---

## 3️⃣ Install Swag Pricing Intelligence

1. **Run the installer**: Double-click `Swag Pricing Intelligence Setup 1.0.0.exe`

2. **Follow the installation wizard**:
   - Choose installation location (default is recommended)
   - Select "Create Desktop Shortcut" ✅
   - Click "Install"

3. **Wait for installation** to complete (~2-3 minutes)

4. **Launch the application** from:
   - Desktop shortcut, OR
   - Start Menu → Swag Pricing Intelligence

---

## 4️⃣ First Time Setup

### Configuration Files

The application stores its configuration and data in:
```
C:\Users\[YourUsername]\AppData\Roaming\swag-pricing-intelligence\
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

## 🚀 Using the Application

1. **Launch** the app from your desktop shortcut
2. **Wait** for the splash screen (~5-10 seconds)
3. The main application window will open automatically
4. Follow the on-screen interface for invoice processing and pricing analysis

---

## 🔧 Troubleshooting

### "Python not found" Error
- Reinstall Python and ensure "Add to PATH" is checked
- Restart your computer after installing Python

### Application Won't Start
- Check Windows Event Viewer for error details
- Ensure all Python packages are installed (see step 2)
- Try running as Administrator (right-click → Run as Administrator)

### Configuration Issues
- Locate the app data folder: `%APPDATA%\swag-pricing-intelligence\`
- Check that `config.json` and `credentials.json` are present
- Verify the format matches the template files

### Firewall/Antivirus Warnings
- The app runs a local web server (localhost:8000)
- Allow the application through Windows Firewall if prompted
- Add exception to antivirus if needed

---

## 📞 Support

For technical support or questions:
- Contact: Ryan Watson
- Email: [Your Email]

---

## 📋 System Requirements

- **OS**: Windows 10 or Windows 11 (64-bit)
- **RAM**: 4 GB minimum (8 GB recommended)
- **Disk Space**: 500 MB free space
- **Python**: Version 3.8 or newer
- **Internet**: Required for Google Sheets and Azure API access

---

## 🔄 Updates

To update the application:
1. Download the new installer
2. Run the installer (it will automatically update the existing installation)
3. Your configuration and data will be preserved

---

## 🗑️ Uninstalling

To remove the application:
1. Go to **Settings** → **Apps** → **Apps & features**
2. Find "Swag Pricing Intelligence"
3. Click **Uninstall**

**Note**: Your configuration files and processed invoices will remain in:
`%APPDATA%\swag-pricing-intelligence\`

Delete this folder manually if you want to remove all data.

---

**© 2025 Swag Golf | Developed by Ryan Watson**
