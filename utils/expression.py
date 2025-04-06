import signal
import numexpr
import re

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Calculation timed out")

def safe_numexpr_eval(expression, timeout=1):
    """
    Safely evaluates a simple arithmetic expression using numexpr,
    with strict input sanitization (allows parentheses but no decimals) and a timeout
    to prevent denial-of-service.
    """
    # Replace every ^ with **
    expression = expression.replace("^", "**")
    
    # Sanitize input using a regular expression to allow digits, basic arithmetic operators,
    # parentheses, and spaces
    if not re.match(r"^[\d+\-*/\s()]+$", expression):
        return None

    try:
        # Set up a timeout handler to prevent long calculations
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)

        # Evaluate the expression using numexpr.evaluate()
        result = numexpr.evaluate(expression)

        # Clear the alarm after a successful result
        signal.alarm(0)

        return result.item()

    except (TypeError, ZeroDivisionError, NameError, SyntaxError) as e:
        print(f"Error evaluating expression: {e}")
        return None
    except TimeoutException:
        print("Calculation timed out!")
        return None
    except OverflowError:
        print("Number too big, overflowed!")
        return None
    finally:
        signal.alarm(0) 