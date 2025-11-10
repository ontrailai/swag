# Swag Pricing Intelligence - Development Setup

## Running from GitHub Source on Windows

### Prerequisites

1. **Python 3.8+** installed with PATH enabled
2. **Git** installed
3. **(Optional) Node.js 18+** - only needed if you want to modify the frontend

### Quick Start

1. **Clone the repository**:
```cmd
git clone https://github.com/ontrailai/swag.git
cd swag
```

2. **Install Python dependencies**:
```cmd
pip install fastapi uvicorn azure-ai-formrecognizer google-auth google-auth-oauthlib google-api-python-client pandas openpyxl
```

3. **Setup configuration**:
   - Copy `config.template.json` to `config.json`
   - Add your Azure Form Recognizer credentials
   - Add your Google Sheets ID (if using)
   - Place your `credentials.json` for Google Sheets API

4. **Run the application**:

   **Option A - Streamlit UI** (simpler):
   ```cmd
   pip install streamlit
   streamlit run app.py
   ```

   **Option B - React UI with Backend**:
   ```cmd
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
   Then open browser to: `http://localhost:8000`

### Folder Structure

```
swag/
├── backend/           # FastAPI backend server
│   └── main.py       # API endpoints
├── frontend/         # React frontend (already built)
│   ├── dist/         # Built frontend files (committed to repo)
│   └── src/          # React source code
├── src/              # Core Python modules
│   ├── invoice_extractor.py   # Azure Form Recognizer integration
│   ├── sheets_writer.py        # Google Sheets API
│   └── variance_engine.py      # Pricing analysis
├── Invoices/
│   ├── new/          # Place PDFs here for processing
│   └── processed/    # Processed PDFs moved here
├── app.py            # Streamlit alternative UI
└── main.py           # CLI interface
```

### Development Workflow

#### Frontend Development

If you want to modify the React frontend:

1. **Install Node.js dependencies**:
```cmd
cd frontend
npm install
```

2. **Run development server** (with hot reload):
```cmd
npm run dev
```
This starts Vite dev server at `http://localhost:5173`

3. **Build for production**:
```cmd
npm run build
```
This creates optimized files in `frontend/dist/`

4. **Commit built files** (if deploying):
```cmd
git add frontend/dist
git commit -m "Update frontend build"
git push
```

#### Backend Development

The FastAPI backend automatically reloads when you modify Python files:

```cmd
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

1. **Test Azure extraction**:
```cmd
python src/invoice_extractor.py
```

2. **Test Google Sheets**:
```cmd
python src/sheets_writer.py
```

3. **Test variance engine**:
```cmd
python src/variance_engine.py
```

4. **Full pipeline**:
```cmd
python main.py
```

### Building Electron Desktop App

#### Windows Build

1. **Install Electron dependencies**:
```cmd
cd electron
npm install
```

2. **Build Windows installer**:
```cmd
npm run build:win
```

This creates `dist_electron/Swag Pricing Intelligence Setup 1.0.0.exe`

#### macOS Build

```bash
cd electron
npm install
npm run build:mac
```

### Troubleshooting

#### "Frontend components missing"
- The `frontend/dist` folder is now included in the repository
- If missing, run: `cd frontend && npm install && npm run build`

#### "Python not found"
- Ensure Python is in your PATH
- Try `python --version` or `python3 --version`

#### "Module not found"
- Install all Python dependencies: `pip install -r requirements.txt`

#### "Port 8000 already in use"
- Kill existing process: `lsof -ti:8000 | xargs kill` (Mac/Linux)
- Or use different port: `uvicorn backend.main:app --port 8001`

### Environment Variables

You can set these in `.env` file:

```env
# Backend
BACKEND_PORT=8000
PYTHONIOENCODING=utf-8
PYTHONUTF8=1

# Frontend (for development)
VITE_API_URL=http://localhost:8000
```

### Production Deployment

For production, use the **pre-built installers** from GitHub Releases:
- Windows: `Swag Pricing Intelligence Setup 1.0.0.exe`
- macOS: `Swag Pricing Intelligence.dmg`

These include all dependencies and are easier for end users.

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Build and test locally
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Create Pull Request

---

**© 2025 Swag Golf | Developed by Ryan Watson**
