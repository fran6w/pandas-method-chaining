import ast

from pandas_method_chaining import Plugin


def _results(statement):
    tree = ast.parse(statement)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_PMC_005_pass():
    """
    Test that using df.assign(col=0) does not result in an error.
    """
    statement = "df.assign(col=0)"
    actual = _results(statement)
    expected = set()
    assert actual == expected


def test_PMC_005_fail():
    """
    Test that using df.col = 0 results in an error.
    """
    statement = "df.col = 0"
    actual = _results(statement)
    expected = {f"{i+1}:0 PMC005 assignment using attribute could be replaced by 'assign()'"
                for i in range(statement.count("\n")+1)}
    assert actual == expected
