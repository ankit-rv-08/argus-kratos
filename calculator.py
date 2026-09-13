"""Small, deliberately constrained ratio calculator used by the dossier."""

from ast import BinOp, Constant, Expression, Load, Name, NodeVisitor, parse


class SafeCalculator(NodeVisitor):
    allowed = (BinOp, Constant, Expression, Load, Name)

    def __init__(self, values: dict[str, float]) -> None:
        self.values = values

    def visit_Expression(self, node: Expression) -> float:
        return self.visit(node.body)

    def visit_BinOp(self, node: BinOp) -> float:
        left = self.visit(node.left)
        right = self.visit(node.right)
        operator = type(node.op)
        if operator is __import__("ast").Add:
            return left + right
        if operator is __import__("ast").Sub:
            return left - right
        if operator is __import__("ast").Mult:
            return left * right
        if operator is __import__("ast").Div:
            return left / right
        raise ValueError("operator not allowed")

    def visit_Constant(self, node: Constant) -> float:
        if not isinstance(node.value, (int, float)):
            raise ValueError("constant not allowed")
        return float(node.value)

    def visit_Name(self, node: Name) -> float:
        return self.values[node.id]

    def generic_visit(self, node: object) -> float:
        if not isinstance(node, self.allowed):
            raise ValueError("expression not allowed")
        return super().generic_visit(node)


def calculate(expression: str, values: dict[str, float]) -> float:
    tree = parse(expression, mode="eval")
    return SafeCalculator(values).visit(tree)
