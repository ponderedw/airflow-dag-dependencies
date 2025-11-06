from airflow.decorators import dag, task
from pendulum import datetime
from airflow.datasets import Dataset
import time


@dag(
    dag_id="transform_student_retention_analysis",
    max_active_runs=1,
    start_date=datetime(2023, 1, 1),
    is_paused_upon_creation=False,
    catchup=False,
    schedule=(
        Dataset("transform_resource_optimization")
        & Dataset("transform_course_performance")
    ),
)
def dag_test():
    @task(outlets=[Dataset("transform_student_retention_analysis")])
    def end_task():
        time.sleep(25)

    end_task()


dag_test()
