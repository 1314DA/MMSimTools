from os import path
import gzip
import pandas as pd
from glob import glob

def parse_log_to_pandas_df(logfiles, concat=True, del_duplicates=True, 
                           check=False, print_df=False):
    '''
    read thermo data from lammps log-file

    Parameters
    ----------
    logfiles : str
        address of the log file or pattern which will be interpreted by glob
    concat : bool
        should different parts of thermo output be concatenated into a single 
        dataframe or should do you want a list of dataframes instead
    del_duplicates  :  bool
        removes duplicates from concatenated dataframe based on Step
    check  :  bool
        warns each time a run in a log-file is not completed
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

    # check if logfiles exists
    def check_existance(logfiles):
        if len(glob(logfiles)) == 0:
            raise ValueError('file(s) matching {} not found'.format(logfiles))


    # unpack logfile if it is .gz
    def read_textfile(logfile):
        if logfile.endswith('.gz'):
            return gzip.open(logfile, 'r')
        else:
            return open(logfile, 'r')


    # cast the sections with thermo data in a list
    def isolate_thermo_passages(f):
        datasets = []
        data = []
        mode = None

        for line in f:
            if (line.startswith('Memory usage') 
                or line.startswith('Per MPI rank')):
                mode = 'thermo'
                data = []
            elif line.startswith('Loop time'):
                mode = None
                datasets.append(data)
                data = []
            elif mode == 'thermo':
                data.append(line)
            
        if not data == []:
            if check == True:
                print('the last run in your log-file has not finished!')
            datasets.append(data)

        if datasets == []:
            raise SystemExit('cannot find data in your log-file')

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

    # first check if log-file(s) exists
    check_existance(logfiles)
    
    thermodata = []

    for logfile in sorted(glob(logfiles)):

        # parse log-file to pandas dataframe
        with read_textfile(logfile) as f:
            datasets = isolate_thermo_passages(f)
    
        for dataset in datasets:
            df = convert_dataset_to_dataframe(dataset)
            thermodata.append(df)

    # if desired, concat dataframes
    if concat:
        thermodata_concatenated = pd.concat(thermodata, sort=False)
        thermodata = thermodata_concatenated
        thermodata.reset_index(drop=True, inplace=True)
        
        # if desired delete duplicates in concatenated datafame
        if del_duplicates:
            thermodata = thermodata.drop_duplicates(subset='Step')
            thermodata.reset_index(drop=True, inplace=True)

    # if desired, print thermodata
    if print_df:
        print(thermodata)

    return thermodata