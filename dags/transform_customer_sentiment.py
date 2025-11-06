from airflow.decorators import dag, task
from pendulum import datetime
from airflow.datasets import Dataset
import time


@dag(
    dag_id="transform_customer_sentiment",
    max_active_runs=1,
    start_date=datetime(2023, 1, 1),
    is_paused_upon_creation=False,
    catchup=False,
    schedule=(
        (Dataset("transform_sales_aggregator") & Dataset("load_customer_feedback"))
        | Dataset("load_ticket_sales")
    ),
)
def dag_test():
    @task(outlets=[Dataset("transform_customer_sentiment")])
    def end_task():
        time.sleep(60)

    end_task()


dag_test()
