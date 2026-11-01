# Abandoned Cart Recovery System

An end-to-end application that identifies abandoned shopping carts, manages customer communication consent, coordinates recovery campaigns, tracks customer interactions, and measures conversions using synthetic data.


## Database Design – ER Diagram

The following diagram shows the database entities and their relationships.

[View the Abandoned Cart Recovery ER Diagram](documentation/ER_Diagram.md)

## 1. Problem Statement

### Business Context

In e-commerce platforms, customers often add products to their shopping carts but leave the website without completing their purchases. These are known as abandoned carts.

Abandoned carts represent potential lost sales for businesses. Sending recovery messages without checking customer consent, purchase activity, and communication frequency can also result in unwanted messages and inaccurate campaign performance.

### Objective

The objective of this project is to develop an Abandoned Cart Recovery System that identifies inactive shopping carts, respects customer communication preferences, coordinates recovery campaigns, and tracks subsequent purchases.

### Proposed Solution

The application provides a simulated workflow for managing abandoned carts and recovery campaigns.

It includes:

- Identifying abandoned carts based on inactivity.
- Managing customer email and SMS consent.
- Suppressing messages when communication is not permitted.
- Applying configured message frequency rules.
- Managing recovery campaigns and message templates.
- Simulating message sending and customer interactions.
- Tracking subsequent purchases.
- Calculating campaign conversion attribution.
- Identifying data-quality issues and business-rule violations.

## 2. Application Workflow

The application follows these major steps:

1. **Data Generation:** Generates synthetic customer, consent, session, cart and cart-item records.
2. **Cart Abandonment Detection:** Identifies carts that remain inactive beyond the configured abandonment period.
3. **Consent Management:** Checks customer communication preferences before recovery messages are attempted.
4. **Message Suppression:** Identifies customers who should not receive recovery messages based on consent, purchase status and configured frequency rules.
5. **Campaign Management:** Coordinates recovery campaigns and their message templates.
6. **Message Tracking:** Simulates message sending and customer interaction events.
7. **Purchase Tracking:** Records orders and identifies purchases associated with recovery activity.
8. **Conversion Attribution:** Calculates eligible campaign attribution within a configured attribution window.
9. **Data Validation:** Checks data consistency and identifies deliberately introduced anomaly scenarios.

## 3. Main Features

- Synthetic customer and transaction data generation.
- Abandoned cart identification.
- Email and SMS consent management.
- Opt-out and purchase-based message suppression.
- Configurable message frequency limits.
- Campaign and message template management.
- Simulated messaging events.
- Order and conversion tracking.
- Campaign attribution.
- Data validation and anomaly detection.
- Ground-truth records for known negative scenarios.
- CSV, JSON and SQL data exports.
- Validation and generation reports.

## 4. Data Entities

The project uses the following ten core entities:

| Entity | Purpose |
|---|---|
| Customer | Stores synthetic customer information |
| Consent | Stores communication preferences |
| Session | Tracks customer browsing sessions |
| Cart | Stores shopping cart information |
| CartLine | Stores products and quantities in carts |
| Campaign | Stores recovery campaign information |
| MessageTemplate | Stores recovery message content |
| SendAttempt | Tracks attempted recovery messages |
| Order | Stores purchase information |
| Attribution | Stores campaign conversion attribution |

The project also maintains supporting data for order items, events, audit decisions and anomaly/ground-truth records where implemented.

## 5. Business Rules and Edge Cases

The application uses the following configured business rules:

- Cart abandonment threshold: 60 minutes.
- Conversion attribution window: 7 days.
- Maximum configured messages: 3 per 7 days.
- Minimum configured interval between messages: 24 hours.
- Email and SMS communication consent checks.
- Purchase-based suppression.

### Negative Scenarios

The synthetic dataset includes four labelled anomaly scenarios:

1. **MESSAGE_AFTER_OPTOUT:** A message is sent after a customer withdraws consent.
2. **PURCHASE_BEFORE_ABANDONMENT:** A cart is considered abandoned after a purchase.
3. **DUPLICATE_ATTRIBUTION:** An order receives duplicate campaign attribution.
4. **STALE_CART_TOTAL:** The cart total does not reflect a quantity update.

These scenarios are used to demonstrate exception detection and data validation.

## 6. Technology Stack

| Technology | Purpose |
|---|---|
| React | Frontend application |
| Vite | Frontend development |
| Recharts | Data visualization |
| Python | Data generation and processing |
| FastAPI | Backend API |
| SQLAlchemy | Database interaction |
| PyMySQL | MySQL connectivity |
| MySQL | Relational database |
| Pytest | Automated testing |

### Why These Technologies?

- **React:** Used to build the interactive frontend.
- **FastAPI:** Provides APIs for communication between the frontend and backend.
- **MySQL:** Stores structured application data and maintains relationships between entities.
- **Python:** Handles synthetic-data generation, processing and validation.
- **SQLAlchemy:** Supports database operations.
- **Pytest:** Used for testing application functionality.

## 7. Synthetic Data Generation

The project uses synthetic data to simulate e-commerce customer activity and recovery workflows.

The generator supports different dataset profiles, including starter and full configurations.

The generated records include:

- Customers and communication consent.
- Sessions and shopping carts.
- Cart items and cart updates.
- Campaigns and message templates.
- Message attempts and interaction events.
- Orders and attribution records.
- Labelled anomaly scenarios.

A fixed random seed of `20261022` is used by the generator.

Generated data can be exported in CSV, JSON and SQL formats.

Actual generated record counts are available in the generation reports.

## 8. Project Structure

```text
abandoned-cart-recovery/
│
├── frontend/
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── .env.example
│
├── database/
│   └── schema.sql
│
├── generator/
│   ├── generate_data.py
│   └── validation.py
│
├── scripts/
│   └── load_mysql.py
│
├── data/
│   ├── starter/
│   └── full/
│
├── documentation/
│
├── tests/
│
├── .env.example
├── .gitignore
└── README.md
```

## 9. Prerequisites

Install the following software:

- Python 3.10 or higher.
- Node.js 18 or higher.
- MySQL Server 8.0 or higher.
- Git.

## 10. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Divya-Kanaparti/abandoned-cart-recovery.git
cd abandoned-cart-recovery
```


### Step 2: Create the MySQL Database

Open MySQL Command Line Client.

Create the database:

```sql
CREATE DATABASE cart_recovery;
```

Import the database schema:

```bash
In root directory:
mysql -u root -p cart_recovery < database/schema.sql
```

Enter your own MySQL password when prompted.

### Step 3: Configure the Backend

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Create your local environment file:

```powershell
Copy-Item backend/.env.example backend/.env
```

Configure the database connection in `backend/.env`:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/cart_recovery
```

Replace `YOUR_PASSWORD` with your own MySQL password.

Do not upload actual `.env` files or credentials to GitHub.

### Step 4: Generate Synthetic Data

Generate the starter dataset:

```bash
python generator/generate_data.py --profile starter --output data/starter
```

Generate the full dataset:

```bash
python generator/generate_data.py --profile full --output data/full
```

### Step 5: Validate Generated Data

For starter data:

```bash
python generator/validation.py --input data/starter --output data/starter/validation
```

For full data:

```bash
python generator/validation.py --input data/full --output data/full/validation
```

### Step 6: Load Data into MySQL

From the project root:

```bash
python scripts/load_mysql.py --input data/starter
```

To load the full dataset:

```bash
python scripts/load_mysql.py --input data/full
```

### Step 7: Start the Backend

From the project root:

```bash
uvicorn app.main:app --app-dir backend --reload
```

Backend URL:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

### Step 8: Start the Frontend

Open another terminal:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm ci
```

Start the frontend:

```bash
npm run dev
```

Open the local URL displayed in the terminal, normally:

http://localhost:5173

## 11. Testing

Run the available automated tests from the project root:

```bash
pytest -q
```

The project also includes a data validation script for checking generated records.

The validation covers data consistency, record relationships, business rules and labelled anomaly scenarios.

Refer to the test output and validation reports for the actual results.

## 12. Data Validation and Reproducibility

The generator and validation scripts support checking:

- Primary-key uniqueness.
- Foreign-key relationships.
- Valid data values.
- Date and timestamp consistency.
- Cart total calculations.
- Consent and suppression scenarios.
- Lifecycle and business-rule consistency.
- Known anomaly scenarios.

The project also generates data reports and SHA-256 checksum information for reproducibility verification.

## 13. Safety and Data Provenance

- All customer and transaction records are synthetic.
- No real customer information is used.
- Email addresses use the reserved `.example.test` domain.
- Messaging events are simulated; no real emails or SMS messages are sent.
- Ground-truth information is maintained separately from operational data.
- Database passwords and environment credentials must be configured locally.

This project is a demonstration application and is not a production messaging platform.

## 14. Project Purpose

It demonstrates the development of an end-to-end business workflow involving synthetic data generation, relational database management, abandoned cart detection, communication consent, recovery campaigns, conversion attribution and data validation.
