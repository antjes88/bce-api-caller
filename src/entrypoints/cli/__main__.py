import click
from src.entrypoints.cli.get_ecb_rates import get_ecb_rates
import warnings
from src.utils.env_var_loader import env_var_loader


warnings.filterwarnings("ignore", category=UserWarning)


@click.group()
def cli():
    pass


cli.add_command(get_ecb_rates)

if __name__ == "__main__":
    env_var_loader(".env")
    cli()
