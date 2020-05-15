from time import time as clock


def time_of_function(function):
    def wrapped(*args):
        start_time = clock()
        res = function(*args)
        print(clock() - start_time)
        return res
    return wrapped


@time_of_function
def func(number):
    n = 0
    for x in range(10000):
        n += float('{:.2f}'.format(float(number)))


@time_of_function
def func2(number):
    n = 0
    for x in range(10000):
        n += int(number)


for lvl in range(9, 29):
    print(int((lvl - 8) ** 2 * 500))
