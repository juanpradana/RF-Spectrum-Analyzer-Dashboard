### PROJECT REQUIREMENTS DOCUMENT (PRD)

**Project Title:** RF Spectrum Analyzer Dashboard for Balai Monitor SFR Lampung  
**Version:** 1.0  
**Date:** December 15, 2025  
**Author:** Grok (based on user requirements)  
**Objective:** Build a full-stack web application to automate analysis of spectrum monitoring CSV files exported from spectrum analyzers, focusing on field strength measurements, occupancy calculation, anomaly detection, visualization, and automated PDF reporting. This tool will reduce manual analysis time for tasks like occupancy evaluation in FM broadcast and other bands, supporting internal reporting at Balai Monitor Spektrum Frekuensi Radio Kelas II Lampung.

**Scope:**  
- Single/multiple CSV upload and parsing.  
- Focus on FM band (87-108 MHz) by default, support all bands in file.  
- Interactive dashboard with charts and stats.  
- Automated occupancy calculation and PDF report generation.  
- Internal use (optional simple auth).  
- No hardware integration.  
- Out of scope: Real-time scanning, external API integration (except optional static licensed stations list), multi-user collaboration advanced.

**Target Users:**  
- Pengendali Frekuensi Radio (like user).  
- Tim Balai Monitor Lampung for internal analysis and reporting.

**Functional Requirements:**

1. **File Upload & Parsing**  
   - Support upload single or multiple CSV files with exact format: separator '^', three sections (Metadata, Bands, Channels).  
   - Auto-detect and parse:  
     - Metadata (Task ID, Location lat/lon, Start/Stop Time, etc.).  
     - Bands list (Band #, Start/Stop Freq, Bandwidth).  
     - Channels data (Channel No., Frequency MHz, Max dBµV/m, Average dBµV/m) as float.  
   - Handle large files (>50k rows) efficiently with Pandas.  
   - Validation: Error message if format invalid (wrong separator, missing sections).  
   - Store parsed data in session or temporary DB for analysis.

2. **Dashboard & Visualization**  
   - Home: Upload form + list recent analyses.  
   - Per-file dashboard:  
     - Display metadata summary (Task ID, Location on map via Leaflet/OpenStreetMap, Time).  
     - Select band (dropdown from parsed bands, default Band 1 FM).  
     - Interactive plots (Plotly):  
       - Line plot: Frequency (x) vs Average Field Strength (y), with Max optional.  
       - Scatter for peaks.  
       - Optional heatmap if multiple files compared.  
     - Table: Top 20 strongest channels (Freq, Avg/Max, sortable).

3. **Analysis Features**  
   - Configurable threshold for "occupied" (default 50 dBµV/m for FM, adjustable 30-70 dB; alternative ITU-style: >10-20 dB above noise floor).  
   - Calculate:  
     - Occupancy percentage: (number channels Avg > threshold / total channels in band) * 100.  
     - Noise floor estimate (median lowest 10% Avg in band).  
     - List occupied channels with potential station match (hardcode or JSON list known FM Lampung stations, e.g. from public sources).  
     - Anomaly flag: Signals >80 dBµV/m or unexpected in guarded bands.

4. **Report Generation**  
   - One-click PDF export (use ReportLab or WeasyPrint).  
   - Template:  
     - Header: Balai Monitor Lampung logo/placeholder, Task ID, Date, Location.  
     - Summary: Occupancy %, number occupied channels, top signals table.  
     - Charts embedded.  
     - Recommendations section (text input or auto: "Occupancy tinggi, saran penertiban jika ilegal").  
     - Footer: Operator note.

5. **Additional Features**  
   - Compare multiple files (overlay plots, trending occupancy).  
   - Simple user auth (username/password hardcoded or env var) for internal security.  
   - Export raw data as CSV/JSON.

**Non-Functional Requirements:**

- **Tech Stack:**  
  - Frontend: Next.js 14+ with Tailwind CSS for responsive UI.  
  - Backend: Python FastAPI (or Flask if simpler).  
  - Database: SQLite for history (optional Postgres later).  
  - Charts: Plotly.js (frontend) or Dash.  
  - PDF: Python library (pdfkit or ReportLab).  
  - Deployment: Vercel for frontend, Render/Heroku for backend, or self-hosted.

- **Performance:** Handle files up to 100k rows <5 sec parse. Responsive on mobile/desktop.

- **Security:** No public deploy if sensitive; rate limit uploads.

- **Reliability:** Full error handling (invalid file, parse fail), logging. Zero crash on valid input.

- **Testing:** Include unit tests for parser, occupancy calc. 100% coverage critical functions.

- **Documentation:** Full README with setup, env vars, how to add licensed stations JSON.

**Data Example for Testing:**  
Include the provided CSV in repo as sample.csv for dev/testing.

**Success Criteria:**  
- MVP ready in one full generation.  
- Parses provided sample perfectly.  
- Generates accurate occupancy for FM band (~40-60% at 50 dB threshold based on sample).  
- PDF report professional-looking.

**Risks & Mitigations:**  
- Format variations: Make parser robust with try/except sections.  
- Large data: Use streaming Pandas read.  
- No licensed list accurate: Start with empty, user add JSON.
