"""Calculator tool for financial projections."""


def calculator(operation: str, x: float, y: float) -> float:
    """Perform arithmetic calculations for financial projections and analysis.
    Use this tool whenever you need to compute numbers such as revenue,
    costs, margins, growth rates, or market size estimates.

    :param operation: The arithmetic operation to perform. Must be one of: add, subtract, multiply, divide, percentage
    :param x: The first number in the calculation
    :param y: The second number in the calculation
    :returns: The numeric result of the calculation
    """
    x = float(x)
    y = float(y)
    ops = {
        "add": lambda a, b: a + b,
        "subtract": lambda a, b: a - b,
        "multiply": lambda a, b: a * b,
        "divide": lambda a, b: a / b if b != 0 else float("inf"),
        "percentage": lambda a, b: (a / b) * 100 if b != 0 else float("inf"),
    }
    if operation not in ops:
        return f"Unknown operation '{operation}'. Use: add, subtract, multiply, divide, percentage"
    return ops[operation](x, y)
