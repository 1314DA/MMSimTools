from os import path
import gzip
import pandas as pd
from glob import glob

def parse_log_to_pandas_df(logfiles, concat=True, del_duplicates=True, 
                           check=False, print_df=False, natoms=False,
                           extend=None):
    '''
    read thermo data from lammps log-file

    Parameters
    ----------
    logfiles  :  str
        address of the log file or pattern which will be interpreted by glob
    concat  :  bool
        should different parts of thermo output be concatenated into a single 
        dataframe or should do you want a list of dataframes instead
    del_duplicates  :  bool
        removes duplicates from concatenated dataframe based on Step
    check  :  bool
        warns each time a run in a log-file is not completed
    print_df  :  bool
        print the parsed dataframe
    natoms  :  bool
        additionally return number of atoms for completed runs
    extend  :  list
        list of column keys with values to be additively extended over 
        multiple log segments

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
                N = int(line.split()[-2]) # last line has natoms
            elif mode == 'thermo':
                data.append(line)
            
        if not data == []:
            if check == True:
                print('the last run in your log-file has not finished!')
            datasets.append(data)
            N = 0

        if datasets == []:
            raise SystemExit('cannot find data in your log-file')

        return datasets, N
        

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


    # additively extend columns over all logs that are read
    def extend_log_columns(thermodata, extend):
        if extend == None:
            pass
        else:
            try:
                for k in extend:
                    for i in range(len(thermodata)-1):
                        final_val = thermodata[i][k].iloc[-1]
                        thermodata[i+1][k] += final_val
            except:
                print('something is wrong with the way you want to extend')
        return thermodata

    ### main procedure ###

    # first check if log-file(s) exists
    check_existance(logfiles)
    
    thermodata = []

    for logfile in sorted(glob(logfiles)):

        # parse log-file to pandas dataframe
        with read_textfile(logfile) as f:
            datasets, N = isolate_thermo_passages(f)
    
        for dataset in datasets:
            df = convert_dataset_to_dataframe(dataset)
            thermodata.append(df)

    # if desired additively continue columns over several log segments
    thermodata = extend_log_columns(thermodata, extend)

    # if desired, concat dataframes
    if concat:
        # do the concatenation
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

    # if desired, return natoms as well
    if natoms == True:
        thermodata = (thermodata, N)

    return thermodata