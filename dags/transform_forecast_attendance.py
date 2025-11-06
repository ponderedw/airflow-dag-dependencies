from airflow.decorators import dag, task
from pendulum import datetime
from airflow.datasets import Dataset
import time


@dag(
    dag_id="transform_forecast_attendance",
    max_active_runs=1,
    start_date=datetime(2023, 1, 1),
    is_paused_upon_creation=False,
    catchup=False,
    schedule=(
        Dataset("transform_sales_aggregator") & Dataset("transform_customer_sentiment")
    ),
)
def dag_test():
    @task(outlets=[Dataset("transform_forecast_attendance")])
    def end_task():
        time.sleep(25)
        a = 1 / 0
        return a

    end_task()


dag_test()
