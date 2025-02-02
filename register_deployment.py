from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from scripts.fetch_xkcd import process_xkcd_comics  # Import your flow

# Define and register the deployment
deployment = Deployment.build_from_flow(
    flow=process_xkcd_comics,
    name="XKCD_Comics_Fetcher",
    schedule=(CronSchedule(cron="0 6 * * 1,3,5", timezone="UTC")),  # Mon/Wed/Fri at 6 AM UTC
    work_pool_name="default-agent-pool",
)

if __name__ == "__main__":
    deployment.apply()
