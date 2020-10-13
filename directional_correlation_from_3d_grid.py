import numpy as np
import pandas as pd

def directional_correlation(vtkfile, corrdir, dist):
    '''
    read vtkfile with 3D grid and correlate values along direction corrdir
    with distance dist

    Parameters
    ----------
    vtkfile  :  str
        address of the 3D grid stored in a file formated as vtk ASCII file
    corrdir  :  list
        axis for the correlation calculation; may be 0=x, 1=y, 2=z
    dist  :  list
        correlation length in unit cells used in calculation

    Raises
    ------

    Returns
    -------
    corr  :  pandas.DataFrame
        Pearson's correlation coefficient of input quatity
        along axes corrdir and with correlation lengths dist
    '''

    # parse values and dimensions from vtkfile to dim* and griddata
    griddata = ''

    with open(vtkfile, 'r') as f:
        data = False
        for l in f.readlines():
            if l.startswith('DIMENSIONS'):
                dimx, dimy, dimz = l.split()[1:]
                dimx, dimy, dimz = int(dimx), int(dimy), int(dimz)
            elif l.startswith('LOOKUP_TABLE'):
                data = True
            elif data:
                griddata += l
            else:
                pass   

    # cast griddata to numpy array
    griddata = griddata.split()
    griddata = np.array(griddata, dtype=float)
    size = len(griddata)

    # create grid indices based on convention in vtkfile
    x = np.zeros(len(griddata), dtype=int)
    y = np.zeros(len(griddata), dtype=int)
    z = np.zeros(len(griddata), dtype=int)

    d = 0
    for k in range(dimz):
        for j in range(dimy):
            for i in range(dimx):
                x[d] = i
                y[d] = j
                z[d] = k
                d += 1

    # function to calculate correlation coefficient
    def correlation_coeff(
        griddata, size, x, y, z, dimx, dimy, dimz, corrdir, dist):
        # initialize griddata for correlation calculation
        X = griddata
        Y = np.zeros(len(X))

        if corrdir == 0: # correlation along first (x) dimension
            # fill array Y with data for neighboring cells
            for xi, yi, zi in zip(x,y,z):
                index      = xi + dimx*yi + dimx*dimy*zi
                neighindex = (xi+dist) + dimx*yi + dimx*dimy*zi
                # take care of periodic boundaries (needs to be checked)
                if neighindex >= size:
                    neighindex -= size
                Y[index] = X[neighindex]
            # calculate Pearson correlation coefficient
            corrcoeff = np.corrcoef(X, y=Y)

        elif corrdir == 1: # correlation along first (x) dimension
            # fill array Y with data for neighboring cells
            for xi, yi, zi in zip(x,y,z):
                index      = xi + dimx*yi + dimx*dimy*zi
                neighindex = xi + dimx*(yi+dist) + dimx*dimy*zi
                # take care of periodic boundaries (needs to be checked)
                if neighindex >= size:
                    neighindex -= size
                Y[index] = X[neighindex]
            # calculate Pearson correlation coefficient
            corrcoeff = np.corrcoef(X, y=Y)

        elif corrdir == 2: # correlation along first (x) dimension
            # fill array Y with data for neighboring cells
            for xi, yi, zi in zip(x,y,z):
                index      = xi + dimx*yi + dimx*dimy*zi
                neighindex = xi + dimx*yi + dimx*dimy*(zi+dist)
                # take care of periodic boundaries (needs to be checked)
                if neighindex >= size:
                    neighindex -= size
                Y[index] = X[neighindex]
            # calculate Pearson correlation coefficient
            corrcoeff = np.corrcoef(X, y=Y)

        return(corrcoeff)


    # do the actual calulation
    alist = []
    blist = []
    clist = []
    for a in np.array(corrdir, dtype=int):
        for b in np.array(dist, dtype=int):
            c = correlation_coeff(griddata, size, x, y, z, 
                dimx, dimy, dimz, a, b)
            alist.append(a)
            blist.append(b)
            clist.append(c[0,1])

    # output results
    corr = pd.DataFrame({'axis':alist, 'distance':blist, 'correlation':clist})

    return corr