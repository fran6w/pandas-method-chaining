import ast

from pandas_method_chaining import Plugin


def _results(statement):
    tree = ast.parse(statement)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_PMC_002_pass():
    """
    Test that using df.sum() does not result in an error.
    """
    statement = "df.sum()\npd.get_dummies(df, col)"
    actual = _results(statement)
    expected = set()
    assert actual == expected


def test_PMC_002_fail():
    """
    Test that using df = df.sum() results in an error.
    """
    statement = "df = df.sum()\ndf = pd.get_dummies(df, col)\ndf = fct(df)\ndf = df.sum().sum()"
    actual = _results(statement)
    expected = {f"{i+1}:0 PMC002 reassignment using call could be replaced by method chaining"
                for i in range(statement.count("\n")+1)}
    assert actual == expected
