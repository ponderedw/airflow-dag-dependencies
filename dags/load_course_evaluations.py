from airflow.decorators import dag, task
from pendulum import datetime
from airflow.datasets import Dataset
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import time


@dag(
    dag_id="load_course_evaluations",
    max_active_runs=1,
    start_date=datetime(2023, 1, 1),
    is_paused_upon_creation=False,
    catchup=False,
    schedule="*/25 * * * *",
)
def dag_test():
    @task(outlets=[Dataset("load_course_evaluations")])
    def end_task():
        time.sleep(120)

    TriggerDagRunOperator(
        task_id="trigger_secondary_dag",
        trigger_dag_id="transform_academic_performance",
        wait_for_completion=False,
    )

    end_task()


dag_test()
