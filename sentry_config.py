import os
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


def init_sentry():
    load_dotenv()
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[SqlalchemyIntegration()],
        traces_sample_rate=1.0
    )
