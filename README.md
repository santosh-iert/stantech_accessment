# Python and SQL Assessment

This project is a Python-based web application that includes user authentication, CSV data processing, and a summary report generation using APIs. The application uses Flask for API endpoints and MySQL for database storage.

## Requirements

### Python Version: 3.9.6

### Database: MySQL

### Libraries: All required Python packages are listed in requirements.txt


## Python Assessment:
### Setup Instructions

### Step 1: Install Python 3.9.6
Ensure that Python 3.9.6 is installed on your system.
You can download it from the official [Python website](https://www.python.org/downloads/release/python-396/)

### Step 2: Create a Virtual Environment
python3 -m venv venv

### Step 3: Activate the virtual environment
source venv/bin/activate (Linux/macos)

### Step 4: Install dependencies
pip install -r requirements.txt

### Step 5: Change Database credentials
Change DB Credentials in python_assessment.py file under the connect_db function

### Step 6: Now to run the application running the python_assessment.py file
python python_assessment.py

The application will start running locally on http://127.0.0.1:5000.

### Step 6: Now application is running and hit the following apis for testing


# API Endpoints

### API 1: SignUP API
curl --location 'http://127.0.0.1:5000/signup' \
--header 'Content-Type: application/json' \
--data '{
    "username": "user123",
    "password": "Password123"
}'
#### Response:-
{
    "message": "User created successfully"
}

### API 2: Login API

curl --location 'http://127.0.0.1:5000/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "santosh1",
    "password": "password@1234"
}'

#### Response:-
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNhbnRvc2gxMjMiLCJleHAiOjE3MjU3OTA4NDN9.kmMM_2pyqrU584IeIR1e-sAsPIu_hAlkmKeEKEum3K4"
}

### API 3: Load CSV Data API

curl --location 'http://127.0.0.1:5000/load_csv' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNhbnRvc2gxMjMiLCJleHAiOjE3MjU3NzE3NDN9.GaKL4bpjrRuLdeX8XSjrp_tL0Woa0Tf8gOlgDV6FHwU' \
--data '{
    "file_path": "/Users/santosh/Library/Application Support/JetBrains/PyCharmCE2024.2/scratches/random_products.csv"
}'
#### Response:-
{ 
    "message": "Csv data successfully loaded to mysql" 
}

### API 4: Summary Report API
curl --location 'http://127.0.0.1:5000/summary' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNhbnRvc2gxMjMiLCJleHAiOjE3MjU3OTA4NDN9.kmMM_2pyqrU584IeIR1e-sAsPIu_hAlkmKeEKEum3K4' \
--data ''

#### Response:-
{
    "data": [
        {
            "category": "American",
            "top_product": "perhaps",
            "top_product_quantity_sold": 352,
            "total_revenue": 468.1
        },
        {
            "category": "history",
            "top_product": "name",
            "top_product_quantity_sold": 398,
            "total_revenue": 118.98
        },
..............................
        {
            "category": "hundred",
            "top_product": "great",
            "top_product_quantity_sold": 504,
            "total_revenue": 61.69
        }
    ],
    "message": "Summary Report successfully generated"
}


## SQL Assessment: 

The desired query is in the **sql_assessment.sql** file


