"""Main CLI application."""

import click


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Python CLI application."""
    pass


@cli.command()
@click.option("--name", default="World", help="Name to greet")
def hello(name: str) -> None:
    """Say hello."""
    click.echo(f"Hello, {name}!")


@cli.command()
def status() -> None:
    """Check application status."""
    click.echo("Application is running!")


if __name__ == "__main__":
    cli()
