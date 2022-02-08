import ast

from pandas_method_chaining import Plugin


def _results(statement):
    tree = ast.parse(statement)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_PMC_001_pass():
    """
    Test that using df.set_index('col') does not result in an error.
    """
    statement = "df.set_index('col')"
    actual = _results(statement)
    expected = set()
    assert actual == expected


def test_PMC_001_fail():
    """
    Test that using df.set_index('col', inplace=True) results in an error.
    """
    statement = "df.set_index('col', inplace=True)"
    actual = _results(statement)
    expected = {f"{i+1}:0 PMC001 usage of 'inplace=True' should be avoided"
                for i in range(statement.count("\n")+1)}
    assert actual == expected
