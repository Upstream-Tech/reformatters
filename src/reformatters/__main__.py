import sentry_sdk
import typer
from sentry_sdk.integrations.typer import TyperIntegration

from reformatters.common import deploy
from reformatters.common.config import Config
from reformatters.common.dynamical_dataset import DynamicalDatasetStorageConfig
from reformatters.contrib.uarizona.swann.analysis import UarizonaSwannAnalysisDataset
from reformatters.example.new_dataset import initialize_new_integration


class GCSStorageConfig(DynamicalDatasetStorageConfig):
    """Configuration for the storage of a GCS dataset."""

    base_path: str = "gs://upstream-gridded-zarrs"


# In this fork, we (currently) are only using and deploying the SWANN dataset.
DYNAMICAL_DATASETS = [
    UarizonaSwannAnalysisDataset(
        storage_config=GCSStorageConfig(),
    ),
]

if Config.is_sentry_enabled:
    sentry_sdk.init(
        dsn=Config.sentry_dsn,
        environment=Config.env.value,
        project_root="src/",
        in_app_include=["reformatters"],
        default_integrations=True,
        integrations=[
            TyperIntegration(),
        ],
    )


app = typer.Typer(pretty_exceptions_show_locals=False)
app.command()(initialize_new_integration)

for dataset in DYNAMICAL_DATASETS:
    app.add_typer(dataset.get_cli(), name=dataset.dataset_id)


@app.command()
def deploy_operational_updates(
    docker_image: str | None = None,
) -> None:
    deploy.deploy_operational_updates(DYNAMICAL_DATASETS, docker_image)


if __name__ == "__main__":
    app()
