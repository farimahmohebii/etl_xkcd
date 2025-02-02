# Step 1: Setup Environment & Dependencies
### 1. Create a Virtual Environment (Recommended)
```
python -m venv venv

source venv/bin/activate
```
### 2. Install Dependencies
```
pip install -r requirements.txt
```
### 3. Configure Environment Variables
Create a .env file in scripts/ and add:
```
DB_NAME=xkcd_db
DB_USER=your_database_username
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
```
#### ⚠️ Do not commit or share this file. Ensure .env is in .gitignore.
### 4.1 Ensure a PostgreSQL User Exists (If Not Created)
Before running the setup script, make sure the PostgreSQL user exists. If it doesn't, create one with the following steps:
```
sudo -u postgres psql
```
Once inside the PostgreSQL shell, run:
```
CREATE USER your_database_username WITH PASSWORD 'your_database_password';
ALTER USER your_database_username CREATEDB;
```
Then exit:
```
\q
```
### 4.2 Create the Database and Table
```
python scripts/setup_db.py
```
This sets up the PostgreSQL database and creates the xkcd_comics table.
# Step 2: Data Extraction
### 5. Fetch XKCD Data from API
```
python scripts/fetch_xkcd_first.py
```
This loads comics into PostgreSQL (xkcd_comics) without automation.

### Step 3: Running with Prefect Work Pool
To Automate the XKCD process and run it 3 times a week for Mondays, Wednesdays and Fridays follow these steps:
### 6. Initialize Prefect
Before running Prefect flows, initialize the project with:
```
prefect init
```
This sets up Prefect configurations and ensures deployments run smoothly.
### 7. To start Prefect:
```
Prefect server start
```
### 8. Configure the prefect.yaml File
Before deploying the flow, ensure the working directory in the prefect.yaml file is correctly set to the root of your project.
Update the directory field  to your project’s root directory.
Example:
```
pull:
  - prefect.deployments.steps.set_working_directory:
      directory: "/absolute/path/to/your/project"
```
#### Access UI at: http://127.0.0.1:4200
### 9. Create a Prefect Work Pool
```
prefect work-pool create default-pool --type process
```
### 10. Start a Prefect Worker
```
prefect worker start --pool default-pool
```
### 11. Build and Apply Prefect Deployment
```
prefect deploy scripts/fetch_xkcd.py:process_xkcd_comics --name "XKCD Comic Fetcher" --pool default-pool
```
### 12. Run the Flow (Trigger the Work Pool)
```
prefect deployment run 'process-xkcd-comics/XKCD Comic Fetcher'

```
Now XKCD Data Pipeline is fully automated and ready to run!
# Step 4: Transform & Validate Data with dbt
### 13. Configure dbt Profiles
1. Navigate to the transformation/ folder in the project.
2. Open the profiles.yml file.
3. Complete the configuration
### 14. Navigate to the transformation Directory
```
cd transformation
```
### 15. Install dbt Package Dependencies
Run the following command to install all dependencies listed in packages.yml:
```
dbt deps
```
### 16. Run dbt Models
```
dbt run
```
This will build dim_comics and fact_comic_views tables in the database.
### 17. Validate Data with dbt Tests
```
dbt test
```
# Step 5: Automate DBT Transformations with Prefect
To automate DBT transformations after XKCD data ingestion, follow these steps:
### 18. Initialize Prefect
Before running Prefect flows, navigate into the scripts directory and initialize the project:
```
cd scripts
prefect init

```
### 19. Start Prefect Server
```
prefect server start
```
Access UI at: http://127.0.0.1:4200
### 20. Configure the prefect.yaml File
Before deploying the flow, ensure the working directory in the prefect.yaml file is correctly set to the root of project.
Update the directory field  to your project’s root directory.
Example:
```
pull:
  - prefect.deployments.steps.set_working_directory:
      directory: "/absolute/path/to/your/project"
```
### 21. Create a Prefect Work Pool
```
prefect work-pool create default-pool --type process
```
### 22. Start a Prefect Worker
```
prefect worker start --pool default-pool

```
### 23. Build and Apply DBT Deployment
```
prefect deploy run_dbt_pipeline.py:execute_dbt_pipeline --name "DBT Transformation Runner" --pool default-pool
```
### 24. Run the Flow (Trigger the Work Pool)
```
prefect deployment run "DBT Transformation Runner/DBT Transformation Runner"

```
Now DBT transformations and data quality checks are fully automated!
