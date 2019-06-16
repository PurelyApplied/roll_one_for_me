#!/usr/bin/env python3


import logging
import unittest
from functools import wraps

logging.getLogger().setLevel(logging.DEBUG)


def with_class_logger(cls):
    cls.logger = logging.getLogger(f"{cls.__name__}")
    return cls


def static_vars(**kwargs):
    # Credit: https://stackoverflow.com/questions/279561/
    #   what-is-the-python-equivalent-of-static-variables-inside-a-function/279586#comment41067162_279586
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


def occasional(counter=0, frequency=1, off_cycle=None, off_args=None, off_kwargs=None, off_mirror_input=False):
    """Causes the decorated function to execute only with the specified frequency, immediately returning None otherwise.

     :param counter:  Initial value of the internal counter at this value.
     :param frequency: Decorated function will execute once every.
     :param off_cycle: A function that is called when the wrapped function is skipped
     :param off_args: *args to @off_cycle.
     :param off_kwargs: **kwargs to @off_cycle
     :param off_mirror_input: If True, pass *args and *kwargs to @off_cycle.  Overrides @off_args and @off_kwargs
     :return Decorated function value, or None
     :raise AssertionError: Invalid input.

    Execution occurs when counter % frequency == 0.
    These values can be externally updated via func.counter and func.frequency.
    Updated values are not checked for validity -- use responsibly."""
    assert frequency >= 1, "@occasional only accepts frequency >= 1"
    counter = counter % frequency

    def decorator(func):
        @wraps(func)
        @static_vars(counter=counter, frequency=frequency)
        def wrapped(*args, **kwargs):
            try:
                if wrapped.counter == 0:
                    return func(*args, **kwargs)
                elif off_cycle and callable(off_cycle):
                    if off_mirror_input:
                        off_cycle(*args, **kwargs)
                    else:
                        off_cycle(*(off_args or ()), **(off_kwargs or {}))
            finally:
                wrapped.counter = (wrapped.counter + 1) % wrapped.frequency
            return None
        return wrapped
    return decorator


# For a less application-specific decorator, see retrying.retry
def retry(maximum_count=1,
          execute_between_attempts: "A no-argument callable that executes on failure." = None,
          permissible_exceptions: "default: all Exceptions are permissible." = ()):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            for attempts_made in range(1, maximum_count + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.exception("Exception occurred in attempt {} of {} in function: {}".format(attempts_made,
                                                                                                      maximum_count,
                                                                                                      func))
                    if permissible_exceptions and not any(
                            isinstance(e, exception_type) for exception_type in permissible_exceptions):
                        logging.error("Exception experienced is not specified as a permissible exception."
                                      "  Rethrowing exception.")
                        raise e

                    if attempts_made < maximum_count:
                        if execute_between_attempts:
                            execute_between_attempts()
                        continue
                    logging.error("Maximum retries reached.  Rethrowing exception.")
                    raise e
        return wrapped
    return decorator


class DecoratorTests(unittest.TestCase):
    def setUp(self):
        logging.getLogger().setLevel(logging.DEBUG)

    def test_occasional(self):
        @occasional(frequency=5)
        def returns_one():
            return 1

        for _i in range(100):
            if _i % 5 == 0:
                self.assertEqual(returns_one(), 1, "Expected returns_one() to return 1")
            else:
                self.assertEqual(returns_one(), None, "Expected returns_one() to, ironically, return None")

    def test_occasional_2(self):
        @occasional(frequency=3, counter=-1)
        def returns_one():
            return 1

        for _i in range(100):
            if _i % 3 == 1:
                self.assertEqual(returns_one(), 1, "Expected returns_one() to return 1")
            else:
                self.assertEqual(returns_one(), None, "Expected returns_one() to, ironically, return None")

    def test_retry_eventually_succeeds(self):
        @occasional(counter=1, frequency=5)
        def return_one():
            return 1

        @retry(maximum_count=5)
        def four_exceptions_then_return_one():
            if return_one():
                return 1
            raise Exception("Constructed exception to test @retry.")

        self.assertEqual(four_exceptions_then_return_one(), 1)

    def test_retry_percolates_errors(self):
        @occasional(counter=1, frequency=10)
        def return_one():
            return 1

        @retry(maximum_count=5)
        def four_exceptions_then_return_one():
            if return_one():
                return 1
            raise Exception("Constructed exception to test @retry.")

        with self.assertRaises(Exception):
            four_exceptions_then_return_one()

    def test_retry_only_catches_specified(self):
        @occasional(counter=0, frequency=1)
        def return_one():
            return 1

        @retry(maximum_count=5, execute_between_attempts=None, permissible_exceptions=(UnboundLocalError,))
        def four_exceptions_then_return_one():
            if return_one():
                return 1
            raise KeyError("Constructed KeyError exception to test @retry.")

        with self.assertRaises(Exception):
            four_exceptions_then_return_one()


if __name__ == "__main__":
    unittest.main()
