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
