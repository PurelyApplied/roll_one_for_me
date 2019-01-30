#!/usr/bin/env python3


def multimap(iterable, *fs):
    if fs:
        return multimap(map(fs[0], iterable), *fs[1:])
    return iterable


if __name__ == "__main__":
    def square(x):
        return x * x

    def double(x):
        return x + x

    def subtract_one(x):
        return x - 1

    L1 = [1, 2, 3]
    MM1 = list(multimap(L1, square, double, subtract_one))
    print("L1 = {} -> square -> double -> -1 : {}".format(L1, MM1))

    L2 = [5, 4, 3]
    MM2 = list(multimap(L2, subtract_one, square, double))
    print("L2 = {} -> -1 -> square -> double {}".format(L2, MM2))

