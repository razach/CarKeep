# CarKeep Database Design

## Overview
This document outlines the database schema design for CarKeep, aligning with our API-first architecture approach.

## Migration Strategy

### Phase 1: API Preparation (Current)
- Continue using JSON files
- Build complete REST API layer
- Implement data validation in API layer
- Document all API endpoints

### Phase 2: Database Implementation
- Implement SQLAlchemy models
- Add database migration scripts
- Keep API interface unchanged
- Run parallel with JSON storage

### Phase 3: Complete Migration
- Switch to database-only storage
- Remove JSON file handling
- Maintain API compatibility

## Database Architecture

### Technology Stack
- **Database**: SQLite (lightweight, file-based)
- **ORM**: SQLAlchemy
- **Migration Tool**: Alembic
- **API Layer**: Flask-RESTful
- **Authentication**: JWT (future)

## Database Schema

### 1. Core Tables

#### `users` Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `vehicles` Table
```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    make VARCHAR(50),
    model VARCHAR(50),
    year INTEGER,
    msrp DECIMAL(10,2),
    current_value DECIMAL(10,2),
    vehicle_type ENUM('sedan', 'suv', 'truck', 'ev', 'hybrid'),
    fuel_type ENUM('gasoline', 'electric', 'hybrid', 'diesel'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `vehicle_depreciation` Table
```sql
CREATE TABLE vehicle_depreciation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    year_0 DECIMAL(10,2) NOT NULL,
    year_1 DECIMAL(10,2) NOT NULL,
    year_2 DECIMAL(10,2) NOT NULL,
    year_3 DECIMAL(10,2) NOT NULL,
    year_4 DECIMAL(10,2),
    year_5 DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);
```

#### `states` Table
```sql
CREATE TABLE states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(2) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    property_tax_rate DECIMAL(5,4) NOT NULL,
    pptra_relief BOOLEAN DEFAULT FALSE,
    relief_cap DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `scenarios` Table
```sql
CREATE TABLE scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL,
    is_baseline BOOLEAN DEFAULT FALSE,
    state_id INTEGER,
    scenario_type ENUM('baseline', 'alternative') DEFAULT 'alternative',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (state_id) REFERENCES states(id)
);
```

#### `scenario_vehicles` Table
```sql
CREATE TABLE scenario_vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    role ENUM('current', 'alternative') NOT NULL,
    impairment DECIMAL(10,2) DEFAULT 0,
    impairment_affects_taxes BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);
```

#### `financing` Table
```sql
CREATE TABLE financing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    financing_type ENUM('loan', 'lease', 'cash') NOT NULL,
    monthly_payment DECIMAL(10,2),
    principal_balance DECIMAL(10,2),
    interest_rate DECIMAL(5,4),
    loan_term INTEGER,
    lease_terms INTEGER,
    extra_payment DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
);
```

#### `trade_ins` Table
```sql
CREATE TABLE trade_ins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    trade_in_value DECIMAL(10,2) NOT NULL,
    loan_balance DECIMAL(10,2) DEFAULT 0,
    incentives DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
);
```

#### `cost_overrides` Table
```sql
CREATE TABLE cost_overrides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    cost_type ENUM('insurance', 'maintenance', 'fuel') NOT NULL,
    monthly_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);
```

#### `incentives` Table
```sql
CREATE TABLE incentives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    financing_id INTEGER NOT NULL,
    incentive_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (financing_id) REFERENCES financing(id)
);
```

### 2. Analysis Tables

#### `cost_analysis_results` Table
```sql
CREATE TABLE cost_analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    baseline_id INTEGER NOT NULL,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_3yr_cost DECIMAL(12,2) NOT NULL,
    monthly_payment_total DECIMAL(10,2) NOT NULL,
    interest_total DECIMAL(10,2) NOT NULL,
    property_tax_total DECIMAL(10,2) NOT NULL,
    insurance_total DECIMAL(10,2) NOT NULL,
    maintenance_total DECIMAL(10,2) NOT NULL,
    fuel_total DECIMAL(10,2) NOT NULL,
    equity_36mo DECIMAL(10,2) NOT NULL,
    investment_opportunity DECIMAL(10,2) NOT NULL,
    net_out_of_pocket DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id),
    FOREIGN KEY (baseline_id) REFERENCES scenarios(id)
);
```

#### `monthly_cost_evolution` Table
```sql
CREATE TABLE monthly_cost_evolution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cost_analysis_id INTEGER NOT NULL,
    month INTEGER NOT NULL,
    payment DECIMAL(10,2) NOT NULL,
    property_tax DECIMAL(10,2) NOT NULL,
    insurance DECIMAL(10,2) NOT NULL,
    maintenance DECIMAL(10,2) NOT NULL,
    fuel DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (cost_analysis_id) REFERENCES cost_analysis_results(id)
);
```

### 3. Configuration Tables

#### `app_config` Table
```sql
CREATE TABLE app_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `default_costs` Table
```sql
CREATE TABLE default_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cost_type ENUM('insurance', 'maintenance', 'fuel') NOT NULL,
    default_amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Data Migration Strategy

### Phase 1: Schema Creation
1. Create database and all tables
2. Insert default data (states, default costs)
3. Create data validation functions

### Phase 2: Data Migration
1. Read existing `data/scenarios/scenarios.json`
2. Validate data structure
3. Insert into database with proper relationships
4. Verify data integrity

### Phase 3: Application Updates
1. Update all routes to use database
2. Add data validation middleware
3. Implement backup/restore functionality
4. Add data export capabilities

## Benefits of New Structure

### Data Integrity
- **Foreign Key Constraints** - Prevent orphaned records
- **Data Validation** - Enforce business rules
- **Transaction Support** - Atomic operations

### Performance
- **Indexed Queries** - Fast scenario lookups
- **Relationship Queries** - Efficient data retrieval
- **Aggregation** - Built-in summary calculations

### Maintainability
- **Schema Evolution** - Easy to add new fields
- **Data Backup** - Standard database backup tools
- **Query Flexibility** - SQL for complex analysis

### Scalability
- **Multiple Users** - User isolation
- **Large Datasets** - Handle thousands of scenarios
- **Complex Analysis** - Advanced reporting capabilities

## Implementation Timeline

### Week 5: Database Foundation
- [ ] Create database schema
- [ ] Implement data models with SQLAlchemy
- [ ] Create migration scripts

### Week 6: Data Migration
- [ ] Migrate existing JSON data
- [ ] Update core calculation engine
- [ ] Test data integrity

### Week 7: Application Updates
- [ ] Update all routes to use database
- [ ] Add data validation
- [ ] Implement backup system

### Week 8: Testing & Polish
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Documentation updates

## Risk Mitigation

### Data Loss Prevention
- **Backup Strategy** - Daily automated backups
- **Migration Testing** - Test on copy of production data
- **Rollback Plan** - Keep JSON files until migration verified

### Performance Considerations
- **Indexing Strategy** - Index frequently queried fields
- **Query Optimization** - Monitor slow queries
- **Connection Pooling** - Efficient database connections

### User Experience
- **Gradual Rollout** - Migrate one feature at a time
- **Fallback Support** - Keep JSON support during transition
- **User Notifications** - Clear communication about changes

## Conclusion

The proposed database structure provides a solid foundation for CarKeep's growth while maintaining the simplicity and ease of use that makes the application valuable. The migration path ensures minimal disruption while unlocking significant improvements in data integrity, performance, and maintainability.
