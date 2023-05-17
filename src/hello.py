import click

@click.group()
@click.option('--verbose', is_flag=True)
def cli(verbose):
    if verbose:
        click.echo('We are in verbose mode.')

@cli.command()
@click.argument('name')
def trim(name):
    click.echo(f'Hello {name}!')
