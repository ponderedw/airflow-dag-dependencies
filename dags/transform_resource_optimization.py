from airflow.decorators import dag, task
from pendulum import datetime
from airflow.datasets import Dataset
import time


@dag(
    dag_id="transform_resource_optimization",
    max_active_runs=1,
    start_date=datetime(2023, 1, 1),
    is_paused_upon_creation=True,
    catchup=False,
    schedule=(
        Dataset("transform_academic_performance") & Dataset("transform_student_feedback_analysis")
    ),
)
def dag_test():
    @task(outlets=[Dataset("transform_resource_optimization")])
    def end_task():
        time.sleep(25)

    end_task()


dag_test()
