import time

import numpy
from matplotlib import pyplot as plt


def plot_and_show_matrix(numpy_2d_array, treshhold=0.7):
    t0 = time.time()
    arr = numpy_2d_array
    rowI = 0
    for row in arr:
        colI = 0
        for el in row:
            if colI == rowI:
                row[colI] = 0
            elif el > treshhold:
                row[colI] = 2
            else:
                row[colI] = el / treshhold
            colI += 1
        rowI += 1
    data = numpy.array(
        [numpy.array([numpy.array([0.1, 0.9, 0.5]) if val == 2 else numpy.array([val, val, val]) for val in row]) for
         row in arr]
    )
    print("Converted data for plot_and_show_matrix in %.2f seconds" % (time.time() - t0))
    plt.imshow(data, interpolation='nearest')
    plt.show()
