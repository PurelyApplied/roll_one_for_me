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


def occasional(counter=0, frequency=1):
    """Causes the decorated function to execute only with the specified frequency, immediately returning None otherwise.

     :param counter:  Initial value of the internal counter at this value.
     :param frequency: Decorated function will execute once every.
     :return Decorated function value, or None
     :raise AssertionError: Invalid input.

    Execution occurs when counter % frequency == 0.
    These values can be externally updated via func.counter and func.frequency.
    Updated values are not checked for validity -- use responsibly."""
    assert frequency >= 1, "@occasional only accepts frequency >= 1"
    counter = counter % frequency

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                if wrapped.counter == 0:
                    return func(*args, **kwargs)
            finally:
                wrapped.counter += 1
                if wrapped.counter == wrapped.frequency:
                    wrapped.counter = 0
            return None

        wrapped.counter = counter
        wrapped.frequency = frequency
        return wrapped

    return decorator


@occasional(counter=-1, frequency=5)
def hello_world():
    logging.info("Hello world!")

if __name__ == "__main__":
    logging.getLogger('').setLevel(logging.DEBUG)
    for i in range(20):
        logging.info("i = {}".format(i))
        hello_world()

    logging.info("Resetting statics to 0/1/2")
    hello_world.counter = 0
    hello_world.frequency = 2
    for i in range(20):
        logging.info("i = {}".format(i))
        hello_world()
