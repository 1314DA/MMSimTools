# MMSimTools

This repository contains some small scripts to aid my simulation work.

* lammps_log_parser
    * read lammps log files and parses them to a pandas DataFrame
    * can check for simulation completion and number of atoms
    * multiple log files can optionally be concatenated
    * can delete duplicate timesteps