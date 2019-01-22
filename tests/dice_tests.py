from rofm.classes.rollers.roll import Throw, Roll


def parser_tst1(n):
    for i in range(n):
        print("4d6^3 = " + str(Roll("4d6^3")))


def parser_tst2(n):
    for i in range(n):
        print("d20 = " + str(Roll("d20")))


def parser_tst3(n):
    for i in range(n):
        print("10d4v7 = " + str(Roll("10d4v7")))


def parser_tst4(n):
    for i in range(n):
        print(Throw("4d6^3 + d20 - 10d4v7 * (1d3 - 1)"))


def rerolls_tst(n):
    r = Roll("3d20")
    for _ in range(n):
        print("{!r} -> {!s}".format(r, r))
        r.reroll()


def throw_rerolls_tst(n):
    t = Throw("3d20 - 2d6 + 1")
    for _ in range(n):
        print("{!r} -> {!s}".format(t, t))
        t.reroll()


if __name__ == '__main__':

    runs = 10
    throw_rerolls_tst(runs)
    parser_tst1(runs)
    parser_tst2(runs)
    parser_tst3(runs)
    parser_tst4(runs)
    rerolls_tst(runs)
