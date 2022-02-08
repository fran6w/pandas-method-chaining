import ast

from collections import namedtuple
from functools import partial

import attr

import importlib.metadata as importlib_metadata


@attr.s
class Visitor(ast.NodeVisitor):
    """
    ast.NodeVisitor calls the appropriate method for a given node type

    i.e. calling self.visit on an Import node calls visit_import

    The `check` functions should be called from the `visit_` method that
    would produce a 'fail' condition.
    """

    errors = attr.ib(default=attr.Factory(list))

    def visit_Call(self, node):
        """
        Called for `df.method(inplace=True)` nodes.
        """
        self.generic_visit(node)  # continue checking children
        self.errors.extend(check_inplace_false(node))

    def visit_Assign(self, node):
        """
        Called for `df=df.method()` nodes.
        Called for `df=df[col]` nodes.
        Called for `df[col]=...` nodes.
        Called for `df.col=...` nodes.
        """
        self.generic_visit(node)  # continue checking children
        self.errors.extend(check_reassignment_with_call(node))
        self.errors.extend(check_reassignment_with_subscript(node))
        self.errors.extend(check_assignment_with_subscript(node))
        self.errors.extend(check_assignment_with_attribute(node))
        self.errors.extend(check_assignment_of_index(node))

    def visit_Subscript(self, node):
        """
        Called for `df.loc[df.col==0]` nodes.
        """
        self.generic_visit(node)  # continue checking children
        self.errors.extend(check_selection_without_lambda(node))

    def check(self, node):
        self.errors = []
        self.visit(node)
        return self.errors

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node.

        This also attaches breadcrumbs before visiting a node so we can
        later look up the syntax tree. This way, there's more
        information to decide whether or not to raise.

        The breadcrumb name is `__pandas_method_chaining_parent` (name mangled) to
        avoid all reasonable name collisions.

        .. see also:: `check_for_values`.
        """
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        item.__pandas_method_chaining_parent = node
                        self.visit(item)
            elif isinstance(value, ast.AST):
                value.__pandas_method_chaining_parent = node
                self.visit(value)


class PandasMethodChainingException(Exception):
    pass


class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree):
        self._tree = tree

    def run(self):
        try:
            return Visitor().check(self._tree)
        except Exception as e:
            raise PandasMethodChainingException(e)

    @staticmethod
    def add_options(optmanager):
        """Informs flake8 to ignore PMCXXX by default."""
        optmanager.extend_default_ignore(disabled_by_default)

        optmanager.add_option(
            long_option_name="--annoy",
            action="store_true",
            dest="annoy",
            default=False,
        )

        options, xargs = optmanager.parse_args()
        if options.annoy:
            optmanager.remove_from_default_ignore(disabled_by_default)


def check_inplace_false(node):
    """Check AST for function calls using inplace=True keyword argument.

    Disapproved:
        df.method(inplace=True)

    Approved:
        df.method(inplace=False)

    Error/warning message to recommend avoidance of inplace=True due to inconsistent behavior.

    :param node: an AST node of type Call
    :return errors: list of errors of type PMC001 with line number and column offset
    """
    errors = []
    for kw in node.keywords:
        if kw.arg == "inplace" and kw.value.value is True:
            errors.append(PMC001(node.lineno, node.col_offset))
    return errors


def check_reassignment_with_call(node):
    """Check AST for reassignment with call.

    Disapproved:
        df = df.method()
        df = pd.get_dummies(df, cols)
        df = df.method1().method2()
        ...

    Approved:
        df.method()
        pd.get_dummies(df, cols)
        df.method1().method2()
        ...

    Error/warning message to replace reassignment using call by method chaining.

    :param node: an AST node of type Call
    :return errors: list of errors of type PMC002 with line number and column offset
    """

    errors = []

    if isinstance(node.value, ast.Call):
        targets = {target.id for target in node.targets if hasattr(target, "id")}
        names = {n.id for n in ast.walk(node.value) if isinstance(n, ast.Name)}
        if targets.intersection(names):
            errors.append(PMC002(node.lineno, node.col_offset))

    return errors


def check_reassignment_with_subscript(node):
    """Check AST for reassignment with subscript.

    Disapproved:
        df = df[]
        df = df.loc[]
        df = df.method()[]
        df = df.method().loc[]
        df = df.method1().method2()[]
        ...

    Approved:
        df[]
        df.loc[]
        df.method()[]
        df.method().loc[]
        df.method1().method2()[]
        ...

    Error/warning message to replace reassignment using subscript by method chaining.

    :param node: an AST node of type Call
    :return errors: list of errors of type PMC003 with line number and column offset
    """

    errors = []

    if isinstance(node.value, ast.Subscript):
        targets = {target.id for target in node.targets if hasattr(target, "id")}
        names = {n.id for n in ast.walk(node.value.value) if isinstance(n, ast.Name)}
        if targets.intersection(names):
            errors.append(PMC003(node.lineno, node.col_offset))

    return errors


def check_assignment_with_subscript(node):
    """Check AST for assignment with subscript.

    Disapproved:
        df[col] = 0
        df.loc[col] = 0
        ...

    Approved:
        df.assign(col=0)
        ...

    Error/warning message to replace assignment using subscript by method chaining.

    :param node: an AST node of type Call
    :return errors: list of errors of type PMC004 with line number and column offset
    """

    errors = []
    for target in node.targets:
        if isinstance(target, ast.Subscript):
            errors.append(PMC004(node.lineno, node.col_offset))
    return errors


def check_assignment_with_attribute(node):
    """Check AST for assignment with attribute.

    Disapproved:
        df.col = 0
        ...

    Approved:
        df.assign(col=0)
        ...

    Error/warning message to replace assignment using attribute by method chaining.

    :param node: an AST node of type Call
    :return errors: list of errors of type PMC005 with line number and column offset
    """

    errors = []
    for target in node.targets:
        if isinstance(target, ast.Attribute) and target.attr not in ["index", "columns"]:
            errors.append(PMC005(node.lineno, node.col_offset))
    return errors


def check_assignment_of_index(node):
    """Check AST for assignment of index.

    Disapproved:
        df.index = ['idx1', 'idx2']
        df.columns = ['col1', 'col2']
        ...

    Approved:
        df.rename({1:'idx1', 2:'idx2'})
        df.rename({1:'col1', 2:'col2'}, axis=1)
        ...

    Error/warning message to replace assignment using attribute by method chaining.

    :param node: an AST node of type Call
    :return errors: list of errors of type PMC006 with line number and column offset
    """

    errors = []
    for target in node.targets:
        if isinstance(target, ast.Attribute) and target.attr in ["index", "columns"]:
            errors.append(PMC006(node.lineno, node.col_offset))
    return errors


def check_selection_without_lambda(node):
    """Check AST for selection without lambda.

    Disapproved:
        df.loc[df.col==0]
        ...

    Approved:
        df.loc[lambda df_: df_.col==0]
        ...

    Error/warning message to use selections with lambda.

    :param node: an AST node of type Subscript
    :return errors: list of errors of type PMC007 with line number and column offset
    """

    errors = []
    # case df[df.isna().any(axis=1)]
    if isinstance(node.value, ast.Name):
        names = {n.id for n in ast.walk(node.slice) if isinstance(n, ast.Name)}
        if node.value.id in names:
            errors.append(PMC007(node.lineno, node.col_offset))
    # case df.loc[df.isna().any(axis=1)]
    elif isinstance(node.value, ast.Attribute) and isinstance(node.value.value, ast.Name):
        names = {n.id for n in ast.walk(node.slice) if isinstance(n, ast.Name)}
        if node.value.value.id in names:
            errors.append(PMC007(node.lineno, node.col_offset))
    return errors


error = namedtuple("Error", ["lineno", "col", "message", "type"])
MethodChainingError = partial(partial, error, type=Plugin)

PMC001 = MethodChainingError(
    message="PMC001 usage of 'inplace=True' should be avoided"
)

PMC002 = MethodChainingError(
    message="PMC002 reassignment using call could be replaced by method chaining"
)

PMC003 = MethodChainingError(
    message="PMC003 reassignment using subscript could be replaced by method chaining"
)

PMC004 = MethodChainingError(
    message="PMC004 assignment using subscript could be replaced by 'assign()'"
)

PMC005 = MethodChainingError(
    message="PMC005 assignment using attribute could be replaced by 'assign()'"
)

PMC006 = MethodChainingError(
    message="PMC006 assignment of index or columns could be replaced by 'rename()'"
)

PMC007 = MethodChainingError(
    message="PMC007 selection reusing a variable could be performed with a lambda"
)

# disable PMCXXX MethodChainingError by default
disabled_by_default = [key for key, value in globals().items() if key.startswith("PMC") and isinstance(value, partial)]
