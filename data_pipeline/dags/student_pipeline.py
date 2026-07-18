from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import os

# Add the project root to the path so we can import modules
import sys
sys.path.insert(0, '/opt/airflow')

from data_pipeline.data_generator import generate_synthetic_data

def run_data_generation():
    """Generate synthetic student data."""
    generate_synthetic_data(n_students=1000, output_path='/opt/airflow/data/synthetic_students.csv')

def run_dbt_transform():
    """Run dbt transformations."""
    os.system('cd /opt/airflow/dbt && dbt run')

def run_model_training():
    """Trigger ML model training via DVC."""
    os.system('cd /opt/airflow && dvc repro train')

def run_dbt_tests():
    """Run dbt data quality tests."""
    os.system('cd /opt/airflow/dbt && dbt test')

with DAG(
    dag_id='campusiq_student_pipeline',
    default_args={
        'owner': 'campusiq',
        'depends_on_past': False,
        'email_on_failure': False,
        'retries': 1,
    },
    description='End-to-end data pipeline for CampusIQ student data',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['campusiq', 'etl', 'students'],
) as dag:
    
    generate_data = PythonOperator(
        task_id='generate_synthetic_data',
        python_callable=run_data_generation,
    )
    
    dbt_transform = BashOperator(
        task_id='dbt_transform',
        bash_command='cd /opt/airflow/dbt && dbt run',
    )
    
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/dbt && dbt test',
    )
    
    train_model = BashOperator(
        task_id='train_model',
        bash_command='cd /opt/airflow && python ml/models/train.py',
    )
    
    # Task dependencies
    generate_data >> dbt_transform >> dbt_test >> train_model
