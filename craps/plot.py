from typing import List
from matplotlib import pyplot  # type: ignore

# fname = get_sample_data('percent_bachelors_degrees_women_usa.csv',
#                         asfileobj=False)
# craps_data = np.genfromtxt(fname, delimiter=',', names=True)


COLORS = ['red', 'green', 'blue']


def plot(craps_data: List[List[List[int]]]):
    for i, strategy in enumerate(craps_data):
        for history in strategy:
            # pyplot.plot(history, color=COLORS[i % len(COLORS)])
            pyplot.plot(history)
    pyplot.show()
