# CarKeep Development Guide

This document provides a comprehensive overview of the CarKeep project, from high-level vision to technical implementation details.

## 1. Project Overview & Vision

CarKeep is a tool for comparing the total cost of ownership between keeping a current vehicle and purchasing a new one. The project transforms a command-line tool into a user-friendly web application, allowing users to create, manage, and compare vehicle cost scenarios through a browser interface.

### 1.1. Core Concept: Baseline + Scenarios

The system uses a **baseline + scenarios** approach:

*   **Baseline**: Represents the "do nothing" option (i.e., keeping the current vehicle).
*   **Scenarios**: Represent different alternatives, such as leasing a new car or financing a certified pre-owned (CPO) vehicle.

All scenarios are compared against the baseline, providing a clear and consistent analysis.

## 2. Web Application Requirements

### 2.1. Core Features

*   **Scenario Management**: CRUD (Create, Read, Update, Delete) operations for vehicle cost scenarios.
*   **Cost Comparison**: View detailed cost breakdowns for individual scenarios and a side-by-side comparison matrix of all scenarios.
*   **User-Friendly Interface**: A responsive, intuitive web interface with clear forms and data displays.

### 2.2. Technical Requirements

*   **Backend**: Python 3.12+ with Flask.
*   **Frontend**: HTML5, CSS3, and vanilla JavaScript.
*   **Data Storage**: Scenarios and configurations stored in JSON files.

### 2.3. User Experience

*   **Ease of Use**: Intuitive navigation and clear labeling.
*   **Performance**: Fast page loads and responsive interactions.
*   **Accessibility**: Keyboard navigation, screen reader support, and high-contrast design.

## 3. Architecture & Technical Implementation

### 3.1. Technology Stack

*   **Backend**: Flask
*   **Frontend**: HTML, CSS, JavaScript
*   **Data Processing**: Pandas, NumPy
*   **Data Storage**: JSON (with planned migration to SQLite)

### 3.2. File Structure

A detailed explanation of the file structure can be found in [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md).

### 3.3. Application Structure

The application is split into two main components:

1. **API Server (run_api.py)**
   - Runs on port 5050
   - Handles all data processing and storage
   - Uses Blueprint with prefix `/api`
   - Key endpoints:
     - `/api/scenarios` - CRUD operations for scenarios
     - `/api/comparison-results` - Cost comparison calculations
     - `/api/cost-analysis` - Detailed cost analysis
     - `/api/state-taxes` - State tax configuration management

2. **Frontend Server (run.py)**
   - Runs on port 5001
   - Handles UI rendering and user interactions
   - Uses Blueprint named 'frontend'
   - Key routes:
     - `/` - Homepage with scenario list
     - `/scenario/<name>` - Individual scenario view
     - `/comparison` - Side-by-side comparison
     - `/cost-analysis` - Detailed cost analysis
     - `/state-taxes` - Tax configuration management
     - `/create` - Create new scenario
     - `/edit-baseline` - Edit baseline scenario
     - `/scenario/<name>/edit` - Edit existing scenario

### 3.4. Data Management

1. **File Locations**
   - Scenarios: `data/scenarios/scenarios.json`
   - State Taxes: `data/configs/state_tax_configs.json`
   - Exports: `data/exports/` (various CSV files)

2. **Path Resolution**
   - All file paths are resolved relative to the application root
   - The `DATA_FOLDER` configuration points to the root data directory
   - Both API and Frontend servers use consistent path resolution

### 3.3. Core Components

*   **`frontend/`**: The Flask web application, including routes, templates, and static files.
*   **`core/`**: The core business logic and calculation engine.
*   **`data/`**: Data files, including scenarios and configurations.
*   **`run.py`**: The frontend application entry point.
*   **`run_api.py`**: The API server entry point.

## 4. Database Design

The current implementation uses JSON files for data storage. A future enhancement is to migrate to a relational database (SQLite with SQLAlchemy). The detailed schema and migration plan can be found in [DATABASE_DESIGN.md](DATABASE_DESIGN.md).

## 5. Project Roadmap & Implementation Plan

### Decision (Sep 2025): Keep It Simple

We will keep the stack lightweight and maintainable:

- Continue using Flask + Jinja server-rendered pages.
- Incrementally enhance interactions with htmx (and optionally Alpine.js) via CDN.
- Defer a full SPA or multi-repo service separation. Sections 6–7 remain as future options but are not active work.
- Focus immediate work on the UI Overhaul Plan (Section 8) and small API quality-of-life improvements.

### 5.1. High-Level Roadmap

*   **Phase 1 (Complete)**: Foundational web application with core functionality.
*   **Phase 2 (In Progress)**: Advanced features, frontend-backend decoupling.
*   **Phase 3 (Planned)**: Database migration.
*   **Phase 4 (Planned)**: User accounts and scenario sharing.

### 5.2. Current Status & Immediate Next Steps

*   **Current Status (as of Sep 2025)**: 
    - All core CRUD operations are functional and tested
    - File structure has been cleaned up and organized
    - Frontend components have been modularized
    - State tax configuration system implemented
    - Enhanced cost analysis with detailed breakdowns
    - Initial API endpoints established and integrated in UI
    - Frontend pages implemented and functional:
      - Scenarios (index)
      - Scenario detail view
      - Comparison overview
      - Cost Analysis (3-year and monthly breakdowns)
      - State Taxes management
      - Create/Edit Scenario and Edit Baseline
*   **Immediate Next Steps (Simple Path)**:
    1. UI v0.1 Visual Foundation (Section 8)
        - Add `static/css/tokens.css` and `static/css/components.css`
        - Polish base layout (nav/footer, container spacing)
        - Add basic toasts/badges and active-state nav
    2. Adopt htmx for targeted interactions
        - Scenario delete/duplicate with confirm + toast (partial swaps)
        - Inline edits for State Taxes rows with save/cancel
    3. Add lightweight charts on Cost Analysis
        - Chart.js via CDN for monthly totals and 3-year breakdown
    4. Accessibility & Performance basics
        - Visible focus styles, skip links; defer non-critical scripts
    5. API QoL (as time permits)
        - Standardize error payloads; document current endpoints briefly

    Note: Service separation, auth, and Docker-based multi-service setup are deferred. See Sections 6–7 for a future path.

### 5.3. Deployment Decision (Render.com, Two Services)

We will deploy two Render services (Option B):

- Frontend (Flask + Jinja) at https://<frontend>.onrender.com
- API (Flask) at https://<api>.onrender.com with the API blueprint under `/api`

Implications for UI work:

- Frontend calls the API server-side via `API_BASE_URL=https://<api>.onrender.com/api`.
- Browser should not call the API directly; htmx interactions should target Frontend routes that render or swap HTML.
- API must enable CORS for the Frontend origin (see `run_api.py`).
- Always use HTTPS URLs to avoid mixed content.

See `docs/DEPLOYMENT.md` for concrete steps and env vars.

## 6. Service Separation & Deployment Architecture

Status: Deferred — we are keeping a single Flask app with server-rendered pages and an internal API under `/api`. The following outlines a future option if we choose to decouple later.

The application will be split into two separate services for improved scalability and maintainability:

### 6.1. Service Architecture

#### Frontend Service (carkeep-frontend)
```
carkeep-frontend/
├── app/
│   ├── static/          # Static assets
│   └── templates/       # Jinja2 templates
├── data/
│   └── exports/         # Generated files for display
└── config/
    └── environment/     # Environment-specific configs
```

#### Backend Service (carkeep-backend)
```
carkeep-backend/
├── core/
│   ├── calculators/     # Business logic
│   └── models/         # Data models
├── data/
│   ├── configs/        # Backend configurations
│   └── templates/      # Calculation templates
└── api/
    └── routes/         # API endpoints
```

### 6.2. Data Management Strategy

#### Configuration Files
- Frontend: User interface configurations, display templates
- Backend: Tax rates, calculation parameters, business rules

#### Data Flow
1. Frontend makes authenticated API calls to backend
2. Backend processes requests and returns JSON responses
3. Frontend renders data and handles user interactions

### 6.3. Deployment Considerations

* **Environment Configuration**
  - Use environment variables for service URLs
  - Implement proper CORS policies
  - Set up API authentication

* **Development Environment**
  - Docker Compose for local development
  - Development proxy for API calls
  - Hot reloading for both services

* **Production Deployment**
  - Separate deployment pipelines
  - Independent scaling
  - Proper monitoring and logging

## 7. Frontend-Backend Separation for iOS Development

**Updated Goal**: Complete frontend/backend separation to enable iOS app development while maintaining current web application functionality.

**Current Status**: 95% complete - API-first architecture implemented with comprehensive endpoints. Frontend consumes API via HTTP requests. Ready for iOS development with minimal additional work.

To achieve complete separation for mobile development, we are focusing on:

### Stage 1: API Completion (Current Focus - iOS Ready)

*   **Goal**: Ensure 100% API coverage for all application functionality.
*   **Status**: Nearly complete - comprehensive REST API implemented
*   **Checklist** (Backend - Flask):
    *   [x] **Core API endpoints implemented**:
        *   [x] Scenarios: GET, POST, PUT, DELETE (full CRUD)
        *   [x] Scenario operations: duplicate, detailed view
        *   [x] State tax management: full CRUD operations
        *   [x] Comparison and cost analysis endpoints
    *   [x] **API Infrastructure**:
        *   [x] CORS properly configured for cross-origin requests
        *   [x] JSON request/response handling
        *   [x] Error handling and validation
        *   [x] Request decorators and middleware
    *   [ ] **Missing endpoints for complete coverage**:
        *   [ ] GET/PUT `/api/baseline` - Baseline scenario management
        *   [ ] GET `/api/config` - Application configuration (optional)
    *   [x] **API Response Standardization**:
        *   [x] Consistent success/error message structure
        *   [x] Proper HTTP status codes
        *   [x] JSON schema validation
    *   [ ] **API Documentation**:
        *   [ ] OpenAPI/Swagger specification
        *   [ ] Interactive API documentation for iOS developers
        *   [ ] Endpoint examples and schemas

### Stage 2: Web Frontend Enhancement (Maintaining Current Architecture)

*   **Goal**: Enhance web frontend while maintaining separation from backend.
*   **Current Status**: Well-separated Flask frontend consuming API
*   **Approach**: Keep Flask + Jinja + htmx for web, focus on iOS-ready backend
*   **Checklist** (Frontend):
    *   [x] **API Integration Complete**:
        *   [x] APIClient class for all backend communication
        *   [x] No direct file system access from frontend
        *   [x] All data via HTTP requests to API
    *   [x] **Dynamic UI Components**:
        *   [x] State taxes: full CRUD via AJAX
        *   [x] Real-time UI updates with htmx
        *   [x] Form validation and error handling
    *   [ ] **Frontend Polish**:
        *   [ ] Update frontend to use new baseline endpoints
        *   [ ] Enhanced error handling and user feedback
        *   [ ] Improved loading states and transitions
    *   [x] **No Framework Lock-in**: Current vanilla JS + htmx approach ensures easy future migration if needed

### Stage 3: iOS Development Readiness

*   **Goal**: Ensure backend API is fully iOS-ready and well-documented.
*   **Status**: Ready for iOS development - comprehensive API available
*   **Checklist**:
    *   [x] **API Architecture**:
        *   [x] RESTful endpoints with proper HTTP methods
        *   [x] JSON request/response format
        *   [x] CORS enabled for cross-origin requests
        *   [x] Comprehensive error handling
    *   [ ] **iOS Development Support**:
        *   [ ] OpenAPI 3.0 specification document
        *   [ ] Postman/Insomnia collection for testing
        *   [ ] API endpoint documentation with examples
        *   [ ] Authentication strategy (future consideration)
    *   [ ] **Deployment for Mobile Backend**:
        *   [ ] Backend API deployed independently to Render
        *   [ ] Environment configuration for production
        *   [ ] Proper CORS policies for mobile apps
        *   [ ] API versioning strategy (future consideration)

### Stage 4: Production Deployment Architecture

*   **Goal**: Deploy frontend and backend independently for scalability and iOS support.
*   **Architecture**: Separate deployments optimized for different needs
*   **Checklist**:
    *   [ ] **Backend API Deployment** (Render Web Service):
        *   [ ] Deploy `run_api.py` as independent web service
        *   [ ] Configure environment variables for production
        *   [ ] Set up proper CORS for web and mobile clients  
        *   [ ] Monitor API performance and errors
    *   [ ] **Frontend Web Deployment** (Render Web Service):
        *   [ ] Deploy `run.py` as separate web service
        *   [ ] Configure API_BASE_URL for production backend
        *   [ ] Set up static file serving
        *   [ ] Optimize for web performance
    *   [ ] **Documentation and Monitoring**:
        *   [ ] API health checks and monitoring
        *   [ ] Error tracking and logging
        *   [ ] Performance metrics
        *   [ ] API usage analytics

### Future: iOS App Development

*   **Goal**: Develop native iOS app using the CarKeep API.
*   **Prerequisites**: Stages 1-3 complete (API ready)
*   **Approach**: Native iOS app consuming REST API
*   **Key Features for iOS**:
    *   [ ] Native iOS UI for scenario management
    *   [ ] Core calculation features via API
    *   [ ] Offline capability (future consideration)
    *   [ ] Push notifications for updates (future)
    *   [ ] iOS-specific UX optimizations

### Future Consideration: Database Backend Integration

While a significant change, integrating a database backend (as outlined in [DATABASE_DESIGN.md](DATABASE_DESIGN.md)) can be pursued in parallel with or after the frontend decoupling. The API-first approach makes this transition smoother, as the frontend would continue to interact with the same API endpoints, regardless of the underlying data storage mechanism.

*   **Key steps for Database Integration**:
    *   [ ] Implement SQLAlchemy models based on `DATABASE_DESIGN.md`.
    *   [ ] Develop data migration scripts from JSON to the database.
    *   [ ] Update Flask API endpoints to interact with the database instead of JSON files.
    *   [ ] Implement robust error handling and data validation at the database level.

## 8. UI Overhaul Plan (September 2025)

This plan modernizes the current Flask/Jinja UI while keeping the stack simple (vanilla JS + CSS). It focuses on clarity, consistency, and performance without requiring an immediate SPA migration.

### Goals
* Improve information hierarchy and scannability
* Establish a consistent design system (spacing, colors, typography, components)
* Enhance accessibility (keyboard, contrast, ARIA)
* Keep performance lean (no heavy frameworks; optional CDN charting only)

### Foundation
* Design tokens: colors, spacing, radius, shadows defined in a single CSS file (`static/css/tokens.css`)
* CSS architecture: small utility classes + component styles (`static/css/components/*.css`)
* Global states: success/info/warn/error badges and toasts
* Dark mode (prefers-color-scheme) with safe contrast

Deployment constraint: All htmx requests should hit Frontend routes (same origin). The Frontend will orchestrate server-side API calls and return HTML partials for swaps. Avoid browser-to-API cross-origin calls to keep CORS simple.

### Global Layout & Navigation
* Persistent top nav with active-state highlight; add quick status pill (total scenarios)
* Breadcrumb bar under nav on detail pages
* Footer with version/build info (API base, commit hash when available)

### Page Improvements
1) Scenarios Home (index)
    - Card grid refinements: consistent headers, iconography, and metadata alignment
    - Add client-side sort/filter (type: lease/loan; payment; MSRP)
    - Convert destructive actions (Delete) to confirm modal; unobtrusive toast feedback
    - Quick actions row pinned at bottom on mobile

2) Scenario Detail
    - Sticky summary panel with key numbers (Monthly total, 3-year net, recommendation)
    - Color-coded chips: green for savings, red for higher costs, neutral for equal
    - Expand/collapse descriptions in tables; default collapsed on mobile
    - Export buttons (CSV for monthly/summary; print-friendly view)

3) Comparison
    - Responsive table with sticky header; sortable columns (Scenario, MSRP, Monthly)
    - Inline tags for state and financing type
    - Optional: CSV export of visible rows; client-side filter bar

4) Cost Analysis
    - Visual charts for monthly totals and 3-year breakdown (Chart.js via CDN, no build step)
    - Sectioned layout: Key Metrics, 3-Year Breakdown, Monthly Evolution, Decision Summary
    - Clear legend explaining sign conventions (positive = costs more; negative = saves)

5) State Taxes
    - Editable rows with inline validation and save/cancel; success/error toasts
    - Form help text and input masks for percent/currency
    - Add search/filter for state list

6) Create/Edit Scenario & Edit Baseline
    - Multi-section form with sticky sidebar summary
    - Inline helpers and validation states; keyboard and screen-reader friendly
    - Warn on unsaved changes when navigating away

### Accessibility Checklist
* [ ] Visible focus states and skip-to-content link
* [ ] Sufficient color contrast (WCAG AA)
* [ ] Semantic landmarks (nav, main, footer) and ARIA labels for complex widgets
* [ ] Keyboard operability for menus, modals, and tables

### Performance
* [ ] Defer non-critical scripts; inline critical CSS for above-the-fold
* [ ] Reduce repaint/relayout by minimizing DOM thrash in JS
* [ ] Cache API responses where safe; add ETags on backend responses (future)

### Deliverables & Milestones
1) v0.1 Visual Foundation (1–2 days)
    - [ ] tokens.css, components.css, basic toasts and badges
    - [ ] Base layout polish (nav/footer, container spacing)

2) v0.2 Scenarios + Scenario Detail (2–3 days)
    - [ ] Cards polish, filter/sort, confirm modal for delete, toasts
    - [ ] Detail page sticky summary, colored chips, CSV/print exports

3) v0.3 Comparison + Cost Analysis (2–3 days)
    - [ ] Sortable responsive table with tags and CSV export
    - [ ] Charts for monthly and 3-year breakdown via Chart.js CDN

4) v0.4 Forms + State Taxes (2–3 days)
    - [ ] Multi-section forms, validation, unsaved-changes guard
    - [ ] Inline editable state tax rows with validation and toasts

5) v0.5 Accessibility & Perf Polish (1–2 days)
    - [ ] Focus states, contrast audit, keyboard flows
    - [ ] Script defers, small CSS/JS trims

### Notes
* This overhaul keeps the current Flask/Jinja structure. If we later choose a SPA, the design system and component styling will carry over.
* Optional library additions (no build step):
  - Chart.js (charts) via CDN
  - Shoelace or Pico.css for minimal components (optional; can stay custom)
