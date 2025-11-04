# SWAG Pricing Intelligence Tool - React Frontend

## 🚀 Quick Start

### Launch Both Servers

```bash
cd /Users/ryanwatson/Desktop/SwagInvoice
./launch_react.sh
```

This will start:
- **Backend (FastAPI)**: http://localhost:8000
- **Frontend (React)**: http://localhost:5173

### Access the Application

Open your browser to: **http://localhost:5173**

## ✅ Phase 5 Complete - What's Been Built

### Backend (FastAPI) ✅
- 11 RESTful API endpoints
- CORS enabled for React frontend
- Background job processing
- Google Sheets integration
- File upload handling
- Configuration management

### Frontend (React) ✅
- **Dashboard Page**: Real-time stats, variance tracking, recent activity table
- **Upload Page**: Drag-and-drop upload, live progress, processing results
- **Settings Page**: Azure config, Google Sheets settings, variance thresholds
- **History Page**: Recently processed files with metadata
- **Components**: UploadZone, ProgressCard, VarianceTable, ConfigEditor, Sidebar
- **Design System**: Swag Golf brand colors, animations, responsive layout

## 🎨 Features

### Visual Design
- Matte black background (#0F0F0F)
- Neon green accent (#32FF6A)
- Neon blue (#00BFFF)
- Gold highlights (#D4AF37)
- Orbitron + Inter fonts
- Animated card hovers
- Glowing borders
- Smooth transitions

### Functionality
- Real-time dashboard updates (every 10s)
- Live processing progress (polling every 2s)
- Drag-and-drop file upload
- Multi-file support
- Toast notifications
- Form validation
- Auto-refresh data
- Responsive design

## 📁 Project Structure

```
SwagInvoice/
├── backend/
│   ├── main.py              ✅ FastAPI server
│   └── requirements.txt     ✅ Python deps
├── frontend/
│   ├── src/
│   │   ├── components/      ✅ All components
│   │   ├── pages/           ✅ All pages
│   │   ├── lib/api.ts       ✅ API client
│   │   ├── App.tsx          ✅ Router
│   │   └── index.css        ✅ Styles
│   ├── .env                 ✅ Config
│   └── package.json         ✅ Dependencies
├── launch_react.sh          ✅ Launch script
└── PHASE5_REACT_MIGRATION.md ✅ Documentation
```

## 🔧 Manual Start (if needed)

### Terminal 1 - Backend
```bash
cd /Users/ryanwatson/Desktop/SwagInvoice
python3 -m uvicorn backend.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
cd /Users/ryanwatson/Desktop/SwagInvoice/frontend
npm run dev
```

## 🎯 Usage Flow

1. **Start servers** → `./launch_react.sh`
2. **Open browser** → http://localhost:5173
3. **Navigate to Upload** → Click "Upload & Process" in sidebar
4. **Drag PDFs** → Drop invoice PDFs into upload zone
5. **Click "RUN ANALYSIS"** → Watch live progress
6. **View results** → See processing summary and metrics
7. **Check Dashboard** → See aggregated statistics
8. **Configure Settings** → Update Azure/Google Sheets credentials

## 🌐 API Endpoints

- `GET /` - API root
- `GET /health` - Health check
- `POST /upload` - Upload PDFs
- `POST /process` - Start processing
- `GET /status/{job_id}` - Job status
- `GET /dashboard-stats` - Dashboard data
- `GET /variance-summary` - Variance data
- `GET /config` - Get config
- `POST /config/update` - Update config
- `GET /processed-files` - File history

API Documentation: http://localhost:8000/docs

## 🎨 Design System

### Colors
```css
Primary Dark:     #0F0F0F (base background)
Secondary Dark:   #1C1C1C (cards)
Tertiary Dark:    #2A2A2A (hover)
Neon Green:       #32FF6A (primary accent)
Neon Blue:        #00BFFF (secondary accent)
Gold:             #D4AF37 (highlights)
Skull White:      #F8F8F8 (text)
```

### Custom Classes
- `.swag-card` - Container with gradient border
- `.swag-btn` - Primary CTA button
- `.swag-btn-secondary` - Secondary button
- `.upload-zone` - Drag-and-drop area
- `.stat-card` - Dashboard metric card
- `.swag-input` - Form input field
- `.sidebar` - Navigation sidebar

## 🎭 Tech Stack

- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Framer Motion (animations)
- React Query (data fetching)
- React Router (routing)
- Axios (HTTP client)
- Lucide React (icons)
- React Hot Toast (notifications)

## 📊 Pages Overview

### Dashboard (`/dashboard`)
- Files processed count
- Variance alerts count
- Impact cost calculation
- Variance breakdown (🟢🟡🔴)
- Recent activity table (last 10)
- Auto-refresh every 10s

### Upload & Process (`/upload`)
- Drag-and-drop zone
- File preview list
- Upload progress
- Processing status
- Live progress bar
- Results summary
- Link to Google Sheet

### Settings (`/settings`)
- Azure Form Recognizer config
- Google Sheets settings
- Variance thresholds
- Password masking
- Form validation
- Save confirmation

### History (`/history`)
- Processed files list
- File metadata (date, size)
- Auto-refresh every 30s

## 🔔 Notifications

Toast notifications appear for:
- ✅ Successful configuration save
- ❌ Configuration save errors
- ✅ Successful file upload
- ❌ Upload errors

## 🚀 Performance

- Code splitting by route
- React Query caching
- Auto-refresh intervals configurable
- GPU-accelerated animations
- Optimized production build

## 📱 Responsive Design

- **Desktop**: Full sidebar, 4-column grid
- **Tablet**: Collapsible sidebar, 2-column grid
- **Mobile**: Hidden sidebar, single column

## 🔮 Future Enhancements (Phase 6)

- Real-time WebSocket updates
- Electron desktop app packaging
- Theme toggle (dark/light)
- Export to CSV/Excel
- Advanced filtering
- User authentication
- Multi-language support

## 📝 Notes

### Existing Functionality Preserved
All backend logic from Streamlit version is preserved:
- Azure Form Recognizer integration
- Google Sheets sync
- Variance calculation engine
- PDF processing pipeline
- Configuration management

### New Capabilities
- Professional UI/UX
- Real-time updates
- Better error handling
- Form validation
- Toast notifications
- Responsive design
- Smooth animations

## 🐛 Troubleshooting

### Backend won't start
```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn main:app --reload
```

### Frontend won't start
```bash
cd frontend
npm install
npm run dev
```

### CORS errors
Check that backend is running on port 8000 and CORS is configured.

### API connection errors
Verify `.env` file exists with `VITE_API_URL=http://localhost:8000`

## 📄 Documentation

- `PHASE5_REACT_MIGRATION.md` - Complete implementation guide
- `backend/main.py` - API documentation (inline comments)
- `frontend/src/lib/api.ts` - API client with TypeScript types

---

## ✅ Success!

The SWAG Pricing Intelligence Tool has been successfully migrated from Streamlit to React + FastAPI with a world-class, production-ready UI featuring the Swag Golf brand aesthetic.

**Launch command**: `./launch_react.sh`

**Built with ⚡ by Claude Code - Phase 5 Complete**
