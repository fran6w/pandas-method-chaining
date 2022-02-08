import ast

from pandas_method_chaining import Plugin


def _results(statement):
    tree = ast.parse(statement)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_PMC_003_pass():
    """
    Test that using df[col] does not result in an error.
    """
    statement = "df[col]\ndf.loc[col]\ndf.sum().loc[col]"
    actual = _results(statement)
    expected = set()
    assert actual == expected


def test_PMC_003_fail():
    """
    Test that using df = df[col] results in an error.
    """
    statement = "df = df[col]\ndf = df.loc[col]\ndf = df.sum()[col]\ndf = df.sum().loc[col]"
    actual = _results(statement)
    expected = {f"{i+1}:0 PMC003 reassignment using subscript could be replaced by method chaining"
                for i in range(statement.count("\n")+1)}
    assert actual == expected
