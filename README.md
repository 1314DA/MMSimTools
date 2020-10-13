# MMSimTools

This repository contains some small scripts to aid my simulation work.

* lammps_log_parser
    * read lammps log files and parses them to a pandas DataFrame
    * can check for simulation completion and number of atoms
    * multiple log files can optionally be concatenated
    * can delete duplicate timesteps

* directional_correlation_from_3d_grid
    * read 3d grid of values in vtk-format as e.g. exported by Ovito's spatial binning
    * calculate Pearson's auto-cross-correlation coefficient along spatial directions (x,y,z) and for different distances (nearest, next-nearest, ...)