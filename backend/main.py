"""
FastAPI Backend for SWAG Pricing Intelligence Tool
Production-grade API with CORS support for React frontend
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
import asyncio
import uuid

# Add src to path for existing modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_loader import ConfigLoader
from main import run_pipeline

# Initialize FastAPI app
app = FastAPI(
    title="SWAG Pricing Intelligence API",
    description="Backend API for invoice processing and variance analysis",
    version="2.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for processing jobs
processing_jobs: Dict[str, Dict] = {}


# ==================== Pydantic Models ====================

class ConfigUpdate(BaseModel):
    """Model for configuration updates"""
    azure: Optional[Dict[str, str]] = None
    google_sheets: Optional[Dict[str, str]] = None
    variance_thresholds: Optional[Dict[str, float]] = None
    paths: Optional[Dict[str, str]] = None


class ProcessingStatus(BaseModel):
    """Model for processing status"""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: float
    message: str
    results: Optional[Dict] = None


class VarianceSummary(BaseModel):
    """Model for variance summary data"""
    total_items: int
    green_count: int
    yellow_count: int
    red_count: int
    recent_data: List[Dict]


# ==================== Helper Functions ====================

def load_config_json() -> Dict:
    """Load configuration from config.json"""
    config_path = Path("config.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load config: {str(e)}")


def save_config_json(config_data: Dict) -> bool:
    """Save configuration to config.json"""
    config_path = Path("config.json")
    try:
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save config: {str(e)}")


def get_recent_sheet_data(limit: int = 10) -> List[Dict]:
    """Fetch recent data from Google Sheets"""
    try:
        config = ConfigLoader()
        gs_config = config.config.get('google_sheets', {})

        from sheets_writer import SheetsWriter
        writer = SheetsWriter(
            sheet_id=gs_config.get('sheet_id', ''),
            credentials_file=gs_config.get('credentials_file', 'credentials.json'),
            token_file=gs_config.get('token_file', 'token.json'),
            sheet_name=gs_config.get('sheet_name', 'Pricing Data')
        )

        writer.authenticate()

        # Get all data from sheet
        result = writer.service.spreadsheets().values().get(
            spreadsheetId=gs_config.get('sheet_id'),
            range=f"{gs_config.get('sheet_name')}!A:N"
        ).execute()

        values = result.get('values', [])

        if not values or len(values) < 2:
            return []

        # First row is headers
        headers = values[0]
        data_rows = values[1:]

        # Get last N rows
        recent_rows = data_rows[-limit:] if len(data_rows) >= limit else data_rows

        # Convert to list of dicts
        result_data = []
        for row in recent_rows:
            # Pad row if needed
            padded_row = row + [''] * (len(headers) - len(row))
            result_data.append(dict(zip(headers, padded_row)))

        return result_data

    except Exception as e:
        print(f"Error fetching sheet data: {e}")
        return []


async def run_processing_job(job_id: str, pdf_files: List[Path]):
    """Background task to run the processing pipeline"""
    try:
        processing_jobs[job_id]['status'] = 'processing'
        processing_jobs[job_id]['progress'] = 0.1
        processing_jobs[job_id]['message'] = 'Initializing services...'

        await asyncio.sleep(0.5)
        processing_jobs[job_id]['progress'] = 0.3
        processing_jobs[job_id]['message'] = 'Processing invoices...'

        # Run the pipeline
        results = run_pipeline()

        # Add Google Sheets URL to results
        config = load_config_json()
        sheet_id = config.get('google_sheets', {}).get('sheet_id', '')
        if sheet_id:
            results['sheet_url'] = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"

        # Immediately update to show completion
        processing_jobs[job_id]['progress'] = 0.95
        processing_jobs[job_id]['message'] = 'Finalizing results...'
        await asyncio.sleep(0.1)

        # Update job status to completed
        processing_jobs[job_id]['status'] = 'completed' if results['success'] else 'failed'
        processing_jobs[job_id]['progress'] = 1.0
        processing_jobs[job_id]['message'] = 'Processing complete!' if results['success'] else 'Processing failed'
        processing_jobs[job_id]['results'] = results

    except Exception as e:
        processing_jobs[job_id]['status'] = 'failed'
        processing_jobs[job_id]['progress'] = 0
        processing_jobs[job_id]['message'] = f'Error: {str(e)}'
        processing_jobs[job_id]['results'] = {'error': str(e)}


# ==================== API Endpoints ====================

@app.get("/api")
async def root():
    """API root endpoint"""
    return {
        "name": "SWAG Pricing Intelligence API",
        "version": "2.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload PDF files for processing
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Ensure Invoices/new directory exists
    invoices_dir = Path("Invoices/new")
    invoices_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files = []
    errors = []

    for file in files:
        if not file.filename.endswith('.pdf'):
            errors.append(f"{file.filename}: Only PDF files are allowed")
            continue

        try:
            # Save file to Invoices/new
            file_path = invoices_dir / file.filename

            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            uploaded_files.append({
                "filename": file.filename,
                "size": len(content),
                "path": str(file_path)
            })

        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    return {
        "success": len(uploaded_files) > 0,
        "uploaded": uploaded_files,
        "errors": errors,
        "total": len(uploaded_files)
    }


@app.post("/process")
async def process_invoices(background_tasks: BackgroundTasks):
    """
    Start processing uploaded invoices
    Returns job_id for tracking progress
    """
    # Check for files in Invoices/new
    invoices_dir = Path("Invoices/new")
    pdf_files = list(invoices_dir.glob("*.pdf")) if invoices_dir.exists() else []

    if not pdf_files:
        raise HTTPException(status_code=400, detail="No PDF files found to process")

    # Create job
    job_id = str(uuid.uuid4())
    processing_jobs[job_id] = {
        'status': 'pending',
        'progress': 0.0,
        'message': 'Job queued',
        'results': None,
        'created_at': datetime.now().isoformat()
    }

    # Start background task
    background_tasks.add_task(run_processing_job, job_id, pdf_files)

    return {
        "job_id": job_id,
        "status": "started",
        "files_count": len(pdf_files)
    }


@app.get("/status/{job_id}")
async def get_processing_status(job_id: str):
    """
    Get status of a processing job
    """
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return processing_jobs[job_id]


@app.get("/variance-summary")
async def get_variance_summary():
    """
    Get variance summary with recent data
    """
    try:
        recent_data = get_recent_sheet_data(limit=10)

        # Count variance flags
        variance_counts = {
            'green': 0,
            'yellow': 0,
            'red': 0
        }

        for item in recent_data:
            flag = item.get('variance_flag', '')
            if flag == '🟢':
                variance_counts['green'] += 1
            elif flag == '🟡':
                variance_counts['yellow'] += 1
            elif flag == '🔴':
                variance_counts['red'] += 1

        return {
            "total_items": len(recent_data),
            "variance_counts": variance_counts,
            "recent_data": recent_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch variance summary: {str(e)}")


@app.get("/config")
async def get_config():
    """
    Get current configuration
    """
    try:
        config = load_config_json()

        # Mask sensitive values
        if 'azure' in config and 'key' in config['azure']:
            key = config['azure']['key']
            if key and len(key) > 4:
                config['azure']['key'] = '*' * (len(key) - 4) + key[-4:]

        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/config/update")
async def update_config(config_update: ConfigUpdate):
    """
    Update configuration settings
    """
    try:
        # Load current config
        config = load_config_json()

        # Update sections
        if config_update.azure:
            if 'azure' not in config:
                config['azure'] = {}
            config['azure'].update(config_update.azure)

        if config_update.google_sheets:
            if 'google_sheets' not in config:
                config['google_sheets'] = {}
            config['google_sheets'].update(config_update.google_sheets)

        if config_update.variance_thresholds:
            if 'variance_thresholds' not in config:
                config['variance_thresholds'] = {}
            config['variance_thresholds'].update(config_update.variance_thresholds)

        if config_update.paths:
            if 'paths' not in config:
                config['paths'] = {}
            config['paths'].update(config_update.paths)

        # Save config
        save_config_json(config)

        return {
            "success": True,
            "message": "Configuration updated successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/processed-files")
async def get_processed_files():
    """
    Get list of recently processed files
    """
    try:
        processed_dir = Path("Invoices/processed")

        if not processed_dir.exists():
            return []

        files = []
        for pdf_file in processed_dir.glob("*.pdf"):
            modified_time = datetime.fromtimestamp(pdf_file.stat().st_mtime)
            files.append({
                "filename": pdf_file.name,
                "modified": modified_time.isoformat(),
                "size": pdf_file.stat().st_size
            })

        # Sort by modified time, most recent first
        files.sort(key=lambda x: x['modified'], reverse=True)

        return files[:10]  # Return last 10 files

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch processed files: {str(e)}")


@app.get("/dashboard-stats")
async def get_dashboard_stats():
    """
    Get dashboard statistics
    """
    try:
        recent_data = get_recent_sheet_data(limit=50)

        # Count variance flags
        variance_counts = {
            'green': 0,
            'yellow': 0,
            'red': 0
        }

        impact_cost = 0.0

        for item in recent_data:
            # Count flags
            flag = item.get('variance_flag', '')
            if flag == '🟢':
                variance_counts['green'] += 1
            elif flag == '🟡':
                variance_counts['yellow'] += 1
            elif flag == '🔴':
                variance_counts['red'] += 1

            # Calculate impact cost
            try:
                cost = float(str(item.get('unit_cost', 0)).replace('$', '').replace(',', ''))
                variance = float(str(item.get('variance_%', 0)).replace('%', ''))
                impact_cost += abs(cost * variance / 100)
            except:
                pass

        # Get processed files count
        processed_dir = Path("Invoices/processed")
        files_count = len(list(processed_dir.glob("*.pdf"))) if processed_dir.exists() else 0

        return {
            "files_processed": files_count,
            "variance_alerts": variance_counts['yellow'] + variance_counts['red'],
            "impact_cost": round(impact_cost, 2),
            "variance_counts": variance_counts
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")


# Serve React build in production
# Check if running in packaged Electron app
frontend_dist_path = Path("frontend/dist")
if not frontend_dist_path.exists():
    # Running from packaged app - look in parent directories
    possible_paths = [
        Path(__file__).parent.parent / "frontend" / "dist",  # Development
        Path("/Applications/Swag Pricing Intelligence.app/Contents/Resources/app/frontend/dist"),  # Packaged macOS
    ]
    for p in possible_paths:
        if p.exists():
            frontend_dist_path = p
            break

app.mount("/", StaticFiles(directory=str(frontend_dist_path), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
