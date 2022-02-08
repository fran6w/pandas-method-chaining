import ast

from pandas_method_chaining import Plugin


def _results(statement):
    tree = ast.parse(statement)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_PMC_006_pass():
    """
    Test that using df.rename({1:'idx1', 2:'idx2'}) does not result in an error.
    """
    statement = "df.rename({1:'idx1', 2:'idx2'})\ndf.rename({1:'col1', 2:'col2'}, axis=1)"
    actual = _results(statement)
    expected = set()
    assert actual == expected


def test_PMC_006_fail():
    """
    Test that using df.index = ['idx1', 'idx2'] results in an error.
    """
    statement = "df.index = ['idx1', 'idx2']\ndf.columns = ['col1', 'col2']"
    actual = _results(statement)
    expected = {f"{i+1}:0 PMC006 assignment of index or columns could be replaced by 'rename()'"
                for i in range(statement.count("\n")+1)}
    assert actual == expected
