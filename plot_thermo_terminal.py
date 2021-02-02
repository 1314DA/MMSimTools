'''
small auxiliary script that uses the lammps log parser to quickly plot data
to terminal

usage:
plot_thermo.py <thermo_key>
'''


import lammps_log_parser as lmp
import plotext as pt
import sys

yvar = sys.argv[1]

data = lmp.parse_log_to_pandas_df('*log')
pt.plot(data['Step'], data[yvar])

pt.xlabel('simulation steps')
pt.ylabel(yvar)
pt.nocolor()
pt.figsize(160, 40)

pt.show()
