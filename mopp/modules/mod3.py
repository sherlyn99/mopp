import click

@click.command()
@click.option("--name", help="enter the name")
def cli3(name):
    """Example script."""
    click.echo('Hello World!3')

def my_func3():
    print('myfunction3')

if __name__ == '__main__':
    my_func3()
    cli3("test")
