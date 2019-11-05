from os import path
import gzip
import pandas as pd


def parse_log_to_pandas_df(logfile, concat=True, check=False, 
                           del_duplicates=True, print_df=False):
    '''
    read thermo data from lammps log-file

    Parameters
    ----------
    logfile : str
        address of the log file
    concat : bool
        should different parts of thermo output be concatenated into a single 
        dataframe or should do you want a list of dataframes instead
    check  :  bool
        check if all runs in the log file have been completed
    del_duplicates  :  bool
        removes duplicates from concatenated dataframe based on Step
    print_df  :  bool
        print the parsed dataframe

    Raises
    ------
    NameError
        logfile not found

    Returns
    -------
    thermodata
        pandas dataframe of list of dataframes
    '''

    # check if logfile exists
    def check_existance(logfile):
        if not path.exists(logfile) == True:
            raise ValueError('could not find {}'.format(logfile))


    # unpack logfile if it is .gz
    def read_textfile(logfile):
        if logfile.endswith('.gz'):
            return gzip.open(logfile, 'r')
        else:
            return open(logfile, 'r')


    # check completeness of simulation
    def get_number_of_runs(f):
        nstarthermo = 0
        nendthermo = 0

        for line in f:
            if (line.startswith('Memory usage') 
                or line.startswith('Per MPI rank')):
                nstarthermo += 1
            elif line.startswith('Loop time'):
                nendthermo += 1
        
        nruns = max(nstarthermo, nendthermo)
        print('there are {} runs in your log-file'.format(nruns))

        if nstarthermo != nendthermo:
            print('BUT: there are unfinished runs in your log-file')
        else: 
            print('AND: they seem be complete')


    # cast the sections with thermo data in a list
    def isolate_thermo_passages(f):
        datasets = []
        mode = None

        for line in f:
            if (line.startswith('Memory usage') 
                or line.startswith('Per MPI rank')):
                mode = 'thermo'
                data = []
            elif line.startswith('Loop time'):
                mode = None
                datasets.append(data)
            elif mode == 'thermo':
                data.append(line)
        
        return datasets
        

    # convert a list of log-file lines to a pandas dataframe
    def convert_dataset_to_dataframe(dataset):
        df = pd.DataFrame([l.split() for l in dataset[1:]], 
            columns = dataset[0].split())
        df = df.astype(float)
        try:
            df = df.astype({'Step':int})
        except:
            pass
        return df



    ### main procedure ###

    # first check if log-file exists
    check_existance(logfile)

    # if desired, check if all runs have been completed
    if check:
        f = read_textfile(logfile)
        nruns = get_number_of_runs(f)

    # parse log-file to pandas dataframe
    f = read_textfile(logfile)
    datasets = isolate_thermo_passages(f)
    thermodata = []
    for dataset in datasets:
        df = convert_dataset_to_dataframe(dataset)
        thermodata.append(df)

    # if desired, concat dataframes
    if concat:
        thermodata_concatenated = pd.concat(thermodata)
        thermodata = thermodata_concatenated

        # if desired delete duplicates in concatenated datafame
        if del_duplicates:
            thermodata = thermodata.drop_duplicates(subset='Step')

    # if desired, print thermodata
    if print_df:
        print(thermodata)

    return thermodata