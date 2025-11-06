from airflow.decorators import dag, task
from pendulum import datetime
from airflow.datasets import Dataset
import time
from airflow.timetables.datasets import DatasetOrTimeSchedule
from airflow.timetables.trigger import CronTriggerTimetable


@dag(
    dag_id="transform_ad_campaign_effectiveness",
    max_active_runs=1,
    start_date=datetime(2023, 1, 1),
    is_paused_upon_creation=False,
    catchup=False,
    schedule=DatasetOrTimeSchedule(
        timetable=CronTriggerTimetable("*/40 * * * *", timezone="UTC"),
        datasets=(Dataset("transform_inventory_optimization")),
    ),
)
def dag_test():
    @task(outlets=[Dataset("transform_ad_campaign_effectiveness")])
    def end_task():
        time.sleep(25)

    end_task()


dag_test()
