import time
forked=time.time()

import decimal
import json
import logging
import threading

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

logger.debug("initializing module")

def pi(digits):
    """
    Compute Pi to the current precision.

    Examples
    --------
    >>> print(pi())
    3.141592653589793238462643383

    Notes
    -----
    Taken from https://docs.python.org/3/library/decimal.html#recipes
    """
    decimal.getcontext().prec = digits
    decimal.getcontext().prec += 2  # extra digits for intermediate steps
    three = decimal.Decimal(3)      # substitute "three=3.0" for regular floats
    lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
    while s != lasts:
        lasts = s
        n, na = n + na, na + 8
        d, da = d + da, da + 32
        t = (t * n) / d
        s += t
    decimal.getcontext().prec -= 2
    return +s               # unary plus applies the new precision

def handle(req, context):
    """handle a request to the function
    Args:
        req (str): request body
    """


    try:
        digits = int(json.loads(req.body)['digits'])
    except TypeError:
        digits = 100
    except json.decoder.JSONDecodeError:
        digits = 100


    logger.debug('%s calculating pi to %d digits', threading.current_thread().name, digits)
    then = time.time()

    result = str(pi(digits))

    now = time.time()

    out = {
        'total_duration': now - then,
        'start_ts': then,
        'end_ts': now
    }


    return {
        "statusCode": 200,
        "body": json.dumps(out)
    }

