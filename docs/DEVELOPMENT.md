# CarKeep Development Guide

This document provides a comprehensive overview of the CarKeep project, from high-level vision to technical implementation details.

## 1. Project Overview & Vision

CarKeep is a tool for comparing the total cost of ownership between keeping a current vehicle and purchasing a new one. The project transforms a command-line tool into a user-friendly web application, allowing users to create, manage, and compare vehicle cost scenarios through a browser interface.

### 1.1. Core Concept: Baseline + Scenarios

The system uses a **baseline + scenarios** approach:

*   **Baseline**: Represents the "do nothing" option (i.e., keeping the current vehicle).
*   **Scenarios**: Represent different alternatives, such as leasing a new car or financing a certified pre-owned (CPO) vehicle.

All scenarios are compared against the baseline, providing a clear and consistent analysis.

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
*   **Data Storage**: Scenarios are stored in a JSON file (`data/scenarios/scenarios.json`).

### 2.3. User Experience

*   **Ease of Use**: Intuitive navigation and clear labeling.
*   **Performance**: Fast page loads and responsive interactions.
*   **Accessibility**: Keyboard navigation, screen reader support, and high-contrast design.

## 3. Architecture & Technical Implementation

### 3.1. Technology Stack

*   **Backend**: Flask
*   **Frontend**: HTML, CSS, JavaScript
*   **Data Processing**: Pandas, NumPy
*   **Data Storage**: JSON

### 3.2. File Structure

A detailed explanation of the file structure can be found in [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md).

### 3.3. Core Components

*   **`app/`**: The Flask web application, including routes, templates, and static files.
*   **`core/`**: The core business logic and calculation engine.
*   **`data/`**: Data files, including `scenarios.json`.
*   **`run.py`**: The entry point for running the Flask application.

## 4. Database Design

The current implementation uses a JSON file for data storage. A future enhancement is to migrate to a relational database (SQLite with SQLAlchemy). The detailed schema and migration plan can be found in [DATABASE_DESIGN.md](DATABASE_DESIGN.md).

## 5. Project Roadmap & Implementation Plan

### 5.1. High-Level Roadmap

*   **Phase 1 (Complete)**: Foundational web application with core functionality.
*   **Phase 2 (In Progress)**: Advanced features, including data validation and a backup system.
*   **Phase 3 (Future)**: Database migration.
*   **Phase 4 (Future)**: User accounts and scenario sharing.

### 5.2. Current Status & Immediate Next Steps

*   **Current Status**: All core CRUD operations are functional. The file structure has been cleaned up and organized.
*   **Immediate Next Steps**:
    1.  Implement data validation for all JSON operations.
    2.  Create a simple backup system for the `scenarios.json` file.
    3.  Add data export functionality (e.g., to CSV or PDF).

## 6. Frontend-Backend Decoupling Plan

To improve maintainability and user experience, the long-term goal is to decouple the frontend and backend into two separate applications. The Flask backend will serve a REST API, and the frontend will be a single-page application (SPA).

### Stage 1: API Expansion (Current Focus)

*   **Goal**: Expose all application functionality through a comprehensive REST API.
*   **Checklist** (Backend - Flask):
    *   [ ] **Review existing API endpoints**: Identify gaps for full CRUD operations (Create, Read, Update, Delete) for scenarios and state tax configurations.
    *   [ ] **Implement missing API endpoints**: Develop new endpoints for any functionality not yet exposed (e.g., detailed scenario data, state tax management).
    *   [ ] **Standardize API responses**: Ensure consistent JSON response formats for all endpoints (e.g., success/error messages, data structures).
    *   [ ] **Implement API authentication/authorization**: (Future consideration, if user accounts are introduced).
    *   [ ] **Document API endpoints**: Use tools like Swagger/OpenAPI to generate interactive API documentation.

### Stage 2: Frontend Scaffolding

*   **Goal**: Set up the foundation for the new frontend application.
*   **Checklist** (Frontend - React/Vue/Svelte):
    *   [ ] **Choose a JavaScript framework**: Select React, Vue, or Svelte based on project needs and team expertise.
    *   [ ] **Initialize new frontend project**: Use the framework's CLI (e.g., Create React App, Vue CLI) to set up the `frontend/` directory.
    *   [ ] **Configure development environment**: Set up hot-reloading, build processes, and testing tools for the frontend.
    *   [ ] **Implement basic API client**: Create a service or utility to make HTTP requests to the Flask API.
    *   [ ] **Create a "Hello World" component**: Fetch and display a simple piece of data from an existing API endpoint (e.g., a list of scenario names) to verify the connection.

### Stage 3: Gradual Component Migration

*   **Goal**: Incrementally replace server-rendered pages with client-side components.
*   **Checklist** (Frontend & Backend):
    *   [ ] **Migrate "State Taxes" page**:
        *   [ ] Create a new frontend component for state tax management.
        *   [ ] Implement fetching, adding, editing, and deleting state tax configurations using the API.
        *   [ ] Integrate the new component into the existing Flask template (e.g., by embedding the SPA or serving it from a new Flask route).
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


## 3. Architecture & Technical Implementation

### 3.1. Technology Stack

*   **Backend**: Flask
*   **Frontend**: HTML, CSS, JavaScript
*   **Data Processing**: Pandas, NumPy
*   **Data Storage**: JSON

### 3.2. File Structure

A detailed explanation of the file structure can be found in [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md).

### 3.3. Core Components

*   **`app/`**: The Flask web application, including routes, templates, and static files.
*   **`core/`**: The core business logic and calculation engine.
*   **`data/`**: Data files, including `scenarios.json`.
*   **`run.py`**: The entry point for running the Flask application.

## 4. Database Design

The current implementation uses a JSON file for data storage. A future enhancement is to migrate to a relational database (SQLite with SQLAlchemy). The detailed schema and migration plan can be found in [DATABASE_DESIGN.md](DATABASE_DESIGN.md).

## 5. Project Roadmap & Implementation Plan

### 5.1. High-Level Roadmap

*   **Phase 1 (Complete)**: Foundational web application with core functionality.
*   **Phase 2 (In Progress)**: Advanced features, including data validation and a backup system.
*   **Phase 3 (Future)**: Database migration.
*   **Phase 4 (Future)**: User accounts and scenario sharing.

### 5.2. Current Status & Immediate Next Steps

*   **Current Status**: All core CRUD operations are functional. The file structure has been cleaned up and organized.
*   **Immediate Next Steps**:
    1.  Implement data validation for all JSON operations.
    2.  Create a simple backup system for the `scenarios.json` file.
    3.  Add data export functionality (e.g., to CSV or PDF).

## 6. Frontend-Backend Decoupling Plan

To improve maintainability and user experience, the long-term goal is to decouple the frontend and backend into two separate applications. The Flask backend will serve a REST API, and the frontend will be a single-page application (SPA).

### Stage 1: API Expansion

*   **Goal**: Expose all application functionality through a comprehensive REST API.
*   **Tasks**:
    *   Expand the existing Flask API to cover all CRUD operations for scenarios and state tax configurations.
    *   Ensure all data needed by the frontend is available through the API.
    *   Document the API endpoints and their usage.

### Stage 2: Frontend Scaffolding

*   **Goal**: Set up the foundation for the new frontend application.
*   **Tasks**:
    *   Create a new `frontend/` directory.
    *   Initialize a new project using a modern JavaScript framework (e.g., React, Vue, or Svelte).
    *   Create a basic project structure with components, services, and views.
    *   Implement a simple component to fetch and display data from the Flask API (e.g., the list of scenarios) to verify the connection.

### Stage 3: Gradual Component Migration

*   **Goal**: Incrementally replace server-rendered pages with client-side components.
*   **Tasks**:
    *   Re-implement one feature at a time as a frontend component that consumes the API.
    *   Start with a simple, self-contained feature, such as the "State Taxes" page.
    *   Gradually migrate more complex features, like the scenario creation and editing forms.

### Stage 4: Finalization and Cleanup

*   **Goal**: Complete the migration and remove legacy code.
*   **Tasks**:
    *   Once all pages have been migrated to the SPA, remove the old Jinja2 templates.
    *   Remove the parts of the Flask backend that were responsible for rendering templates.
    *   Update the project's documentation to reflect the new, decoupled architecture.
