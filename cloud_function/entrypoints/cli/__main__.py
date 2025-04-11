import click
from cloud_function.entrypoints.cli.dummy import dummy
import warnings
from cloud_function.utils.env_var_loader import env_var_loader


warnings.filterwarnings("ignore", category=UserWarning)


@click.group()
def cli():
    pass


cli.add_command(dummy)

if __name__ == "__main__":
    env_var_loader(".env")
    cli()
