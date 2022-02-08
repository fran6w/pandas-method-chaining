import ast

from pandas_method_chaining import Plugin


def _results(statement):
    tree = ast.parse(statement)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_PMC_007_pass():
    """
    Test that using df.loc[lambda df_: df_.isna().any(axis=1)] does not result in an error.
    """
    statement = "df.loc[lambda df_: df_.isna().any(axis=1)]"
    actual = _results(statement)
    expected = set()
    assert actual == expected


def test_PMC_007_fail():
    """
    Test that using df.loc[df.isna().any(axis=1)] results in an error.
    """
    statement = "df[df.isna().any(axis=1)]\ndf.loc[df.isna().any(axis=1)]"
    actual = _results(statement)
    expected = {f"{i+1}:0 PMC007 selection reusing a variable could be performed with a lambda"
                for i in range(statement.count("\n")+1)}
    assert actual == expected
