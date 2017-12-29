from rofm.classes.rollers.roll import Throw, Roll


def parser_tst(n):
    for i in range(n):
        print("4d6^3 = " + str(Roll("4d6^3")))
    for i in range(n):
        print("d20 = " + str(Roll("d20")))
    for i in range(n):
        print("10d4v7 = " + str(Roll("10d4v7")))
    for i in range(n):
        print(Throw("4d6^3 + d20 - 10d4v7 * (1d3 - 1)"))


if __name__ == '__main__':
    parser_tst(20)

