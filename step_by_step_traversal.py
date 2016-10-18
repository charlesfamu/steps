from sympy import *
from sympy.parsing.sympy_parser import parse_expr

def step_by_step_solve(str_expr):
    """
    Returns a list of the mathematical steps involved in solving the problem
    represented by str_expr (A string).
    The steps are strings in chronological order.
    """
    expr = parse_expr(str_expr, evaluate=False)
    steps = []
    # If the parsed expr is somehow different from the original
    # expr due to trivial simplifications, mention that step too
    str_expr_2 = str(expr)
    if str_expr != str_expr_2:
        steps.append(str_expr + ' = ' + str_expr_2)
    steps.extend([step for step in post_order_evaluate(expr)])
    return steps

def post_order_evaluate(expr, level=0):
    """
    Yields all the str'ed steps involved in solving a SymPy-expr.
    Acts recursively, so that steps/sub-steps come in order.
    The first call has to be made with level=0.
    """
    if simplify(expr) == expr:
        # If its a simple expr, yield its string form directly
        # Deals with the trivial case
        rhs = str(expr)
        yield str(expr)
    else:
        evaluated_steps = []
        # Iterate over every argument making up the overall expression
        for step in expr.args:
            if simplify(step) == step:
                # Base case of simple argument
                evaluated_steps.append(step)
                continue
            else:
                evaluated_steps.append(simplify(step))
                # Make recursive call for an argument that is a complex
                # expr in itself
                for sub_step in post_order_evaluate(step, level + 1):
                    yield sub_step
        # Represent current step in the form LHS = RHS
        # LHS is the complex expression
        # RHS is the simplified version

        lhs = str(expr.func(*evaluated_steps, evaluate=False))
        rhs = str(simplify(expr.func(*evaluated_steps, evaluate=True)))

        if isinstance(expr, Mul):
            if lhs != rhs:
                divides = [type(n) is Rational for n in evaluated_steps]
                size = len(divides) - 1
                for k, bl in enumerate(divides):
                    if bl:
                        frac = fraction(evaluated_steps[k])
                        if k == 0:
                            expression = 'Divide '
                        else:
                            expression += 'divide by '
                        expression += str(frac[1])
                    else:
                        if k == 0:
                            expression = 'Take '
                        else:
                            expression += 'multiply by '
                        expression += str(evaluated_steps[k])
                    if k < size:
                        expression += ' and then '
                    else:
                        expression += '.'
                yield expression
                yield 'Result equals ' + rhs
        if isinstance(expr, Add):
            if lhs != rhs:
                terms = " and ".join([str(term) for term in evaluated_steps] )
                expression = 'Add ' + terms
                yield expression
                yield 'Result equals ' + rhs
        if isinstance(expr, Pow):
            if lhs != rhs:
                expression = 'Evaluate ' + str(evaluated_steps[0]) + ' to the power of ' + str(evaluated_steps[1])
                yield expression
                yield 'Result equals ' + rhs
        # if lhs != rhs:
            # yield (lhs + ' = ' + rhs)
    if level == 0:
        # If we are back to the first expression after recursion,
        # show the completed last step

        final_expr = parse_expr(rhs).evalf()
        if str(final_expr) != rhs:
            yield (rhs + ' = ' + str(final_expr))
        else:
            yield (str(expr) + ' = ' + rhs)

# example = "5 + 2*(3 + 9)**3/5"
#
# for x in step_by_step_solve(example):
#     print(x)
