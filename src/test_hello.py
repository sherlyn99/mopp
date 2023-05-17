from click.testing import CliRunner
from hello import cli

def test_trim_subcommand():
    runner = CliRunner()
    result = runner.invoke(cli, ['trim','Chloe'])
    assert result.exit_code == 0
    assert result.output == 'Hello Chloe!\n'



