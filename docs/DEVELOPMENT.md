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

*   **`app/`**: The Flask web application, including routes, templates, and static files.
*   **`core/`**: The core business logic and calculation engine.
*   **`data/`**: Data files, including scenarios and configurations.
*   **`run.py`**: The entry point for running the Flask application.

## 4. Database Design

The current implementation uses JSON files for data storage. A future enhancement is to migrate to a relational database (SQLite with SQLAlchemy). The detailed schema and migration plan can be found in [DATABASE_DESIGN.md](DATABASE_DESIGN.md).

## 5. Project Roadmap & Implementation Plan

### 5.1. High-Level Roadmap

*   **Phase 1 (Complete)**: Foundational web application with core functionality.
*   **Phase 2 (In Progress)**: Advanced features, frontend-backend decoupling.
*   **Phase 3 (Planned)**: Database migration.
*   **Phase 4 (Planned)**: User accounts and scenario sharing.

### 5.2. Current Status & Immediate Next Steps

*   **Current Status**: 
    - All core CRUD operations are functional and tested
    - File structure has been cleaned up and organized
    - Frontend components have been modularized
    - State tax configuration system implemented
    - Enhanced cost analysis with detailed breakdowns
    - Initial API endpoints established
*   **Immediate Next Steps**:
    1. Service Separation Implementation:
        - Create new repository for frontend application
        - Restructure backend as dedicated API service
        - Set up cross-origin resource sharing (CORS)
        - Implement API authentication system
    2. Data Layer Improvements:
        - Move configuration files to appropriate services
        - Implement proper environment-based configuration
        - Set up data synchronization between services
    3. Development Environment Updates:
        - Create docker-compose for local development
        - Set up environment variable management
        - Implement development proxy configuration
    4. Documentation & Testing:
        - Create API documentation with OpenAPI/Swagger
        - Update deployment guides for separated services
        - Add service-specific testing suites

## 6. Service Separation & Deployment Architecture

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

## 7. Frontend-Backend Decoupling Plan

To achieve the service separation, we are implementing a phased approach:

### Stage 1: API Expansion (Current Focus)

*   **Goal**: Expose all application functionality through a comprehensive REST API.
*   **Checklist** (Backend - Flask):
    *   [x] **Review existing API endpoints**: Basic CRUD operations identified for scenarios and state tax configurations.
    *   [✓] **Initial JSON API Routes**: JSON response routes implemented for:
        *   [x] Scenario listing and individual retrieval
        *   [x] State tax configuration management
        *   [x] Cost analysis data export
    *   [ ] **Implement missing API endpoints**: Need to develop endpoints for:
        *   [ ] Detailed scenario comparison matrices
        *   [ ] Bulk operations
        *   [ ] Configuration backup/restore
    *   [~] **Standardize API responses**: Partially complete
        *   [x] Basic success/error message structure
        *   [ ] Comprehensive error handling
        *   [ ] Response schema documentation
    *   [ ] **Implement API authentication/authorization**: (Future consideration, if user accounts are introduced).
    *   [ ] **Document API endpoints**: Use tools like Swagger/OpenAPI to generate interactive API documentation.

### Stage 2: Frontend Scaffolding

*   **Goal**: Set up the foundation for the new frontend application.
*   **Current Status**: Initial frontend improvements in place with vanilla JavaScript
*   **Checklist** (Frontend - React/Vue/Svelte):
    *   [~] **Modern JavaScript Foundation**: 
        *   [x] Modular JavaScript structure
        *   [x] Client-side form validation
        *   [x] Dynamic UI updates
        *   [ ] Framework selection pending
    *   [ ] **Initialize new frontend project**: Use the framework's CLI (e.g., Create React App, Vue CLI) to set up the `frontend/` directory.
    *   [~] **Development Environment**: 
        *   [x] Basic asset pipeline
        *   [x] Static file organization
        *   [ ] Hot-reloading setup pending
    *   [x] **Basic API Integration**: 
        *   [x] AJAX requests for state tax management
        *   [x] JSON data handling
        *   [x] Dynamic form submission
    *   [ ] **Framework Migration**: Pending framework selection

### Stage 3: Gradual Component Migration

*   **Goal**: Incrementally replace server-rendered pages with client-side components.
*   **Checklist** (Frontend & Backend):
    *   [~] **State Taxes Management**:
        *   [x] Dynamic frontend component implemented
        *   [x] CRUD operations via API endpoints
        *   [x] Real-time UI updates
        *   [ ] Complete SPA conversion pending
    *   [ ] **Migrate "Scenario List" and "Scenario View" pages**:
        *   [ ] Create frontend components for displaying and viewing scenarios.
        *   [ ] Implement data fetching and display from the API.
    *   [ ] **Migrate "Create/Edit Scenario" forms**:
        *   [ ] Create frontend components for scenario creation and editing.
        *   [ ] Implement form validation and submission to the API.
    *   [ ] **Migrate "Comparison" and "Cost Analysis" pages**:
        *   [ ] Create frontend components for displaying comparison matrices and cost analysis results.
        *   [ ] Implement data fetching and visualization.

### Stage 4: Finalization and Cleanup

*   **Goal**: Complete the migration and remove legacy code.
*   **Checklist** (Backend & Frontend):
    *   [ ] **Remove old Jinja2 templates**: Delete all server-rendered HTML templates.
    *   [ ] **Refactor Flask routes**: Remove rendering logic and keep only API endpoint definitions.
    *   [ ] **Update deployment strategy**: Configure the server to serve the SPA and the Flask API separately.
    *   [ ] **Update project's documentation**: Ensure all documentation reflects the new, decoupled architecture.

### Future Consideration: Database Backend Integration

While a significant change, integrating a database backend (as outlined in [DATABASE_DESIGN.md](DATABASE_DESIGN.md)) can be pursued in parallel with or after the frontend decoupling. The API-first approach makes this transition smoother, as the frontend would continue to interact with the same API endpoints, regardless of the underlying data storage mechanism.

*   **Key steps for Database Integration**:
    *   [ ] Implement SQLAlchemy models based on `DATABASE_DESIGN.md`.
    *   [ ] Develop data migration scripts from JSON to the database.
    *   [ ] Update Flask API endpoints to interact with the database instead of JSON files.
    *   [ ] Implement robust error handling and data validation at the database level.
