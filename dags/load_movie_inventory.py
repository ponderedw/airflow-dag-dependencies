from airflow.decorators import dag, task
from pendulum import datetime


@dag(
    dag_id="load_movie_inventory",
    max_active_runs=1,
    start_date=datetime(2023, 1, 1),
    is_paused_upon_creation=False,
    catchup=False,
    schedule=None,
)
def dag_test():
    @task
    def try_task():
        pass

    try_task()


dag_test()
