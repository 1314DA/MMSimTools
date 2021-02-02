'''
small auxiliary script that uses the lammps log parser to quickly plot data

usage:
plot_thermo.py <thermo_key>
'''


import matplotlib.pyplot as plt
import lammps_log_parser as lmp
import sys

yvar = sys.argv[1]

plt.figure(1)
data = lmp.parse_log_to_pandas_df('*log')
plt.plot(data['Step'], data[yvar])
plt.xlabel('simulation steps')
plt.ylabel(yvar)
plt.savefig('tmp_plot.pdf', bbox_inches="tight")

plt.show()
