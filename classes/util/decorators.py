#!/usr/bin/env python3


from functools import wraps

import logging


def static_vars(**kwargs):
    # Credit: https://stackoverflow.com/questions/279561/
    #   what-is-the-python-equivalent-of-static-variables-inside-a-function/279586#comment41067162_279586
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


def occasional(counter=0, trigger=0, frequency=1, log=False):
    """Causes the decorated function to execute only with frequency @frequency.
    Initial counter set to @counter, iterating each time the wrapped function is called.
    Execution occurs whenever @counter % @frequency = @trigger.

    These values can be externally updated by altering func.counter, func.trigger, or func.frequency.
    Updated values are not checked for validity."""
    assert 0 <= counter <= trigger < frequency, "@occasional arguments must satisfy 0 < counter <= trigger < frequency"

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if log:
                logging.debug("In function '{}', counter={}, frequency={}, trigger={}".format(
                    func, wrapped.counter, wrapped.frequency, wrapped.trigger))
            try:
                if wrapped.counter == wrapped.trigger:
                    if log:
                        logging.debug("Executing wrapped function.")
                    return func(*args, **kwargs)
                else:
                    logging.debug("Skipping wrapped function.")
            finally:
                logging.debug("Iterating counters...")
                wrapped.counter += 1
                if wrapped.counter == wrapped.frequency:
                    logging.debug("Resetting counter to zero.")
                    wrapped.counter = 0
            return None

        wrapped.counter = counter
        wrapped.trigger = trigger
        wrapped.frequency = frequency
        return wrapped

    return decorator


@occasional(counter=0, trigger=3, frequency=5)
def hello_world():
    logging.info("Hello world!")

if __name__ == "__main__":
    logging.getLogger('').setLevel(logging.DEBUG)
    for i in range(20):
        logging.info("i = {}".format(i))
        hello_world()

    logging.info("Resetting statics to 0/1/2")
    hello_world.counter = 0
    hello_world.trigger = 1
    hello_world.frequency = 2
    for i in range(20):
        logging.info("i = {}".format(i))
        hello_world()
