''' take ovito 3D vtk spatial binning grid
    calculate correlation of grid points along specified direction
    allows to define distance of cells that will be correlated
'''
import numpy as np

vtkgridfile = 'grid_Pz.vtk'
corrdir = [0,1,2] # correlation direction
dist = [1,2,3,4,5] # distance of correlation


# parse values and dimesions from vtkfile to dimi and griddata
griddata = ''

with open(vtkgridfile, 'r') as f:
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


print('using file: {}'.format(vtkgridfile))
print('axis distance correlation')
for a in np.array(corrdir, dtype=int):
    for b in np.array(dist, dtype=int):
        c = correlation_coeff(griddata, size, x, y, z, dimx, dimy, dimz, a, b)
        print('{} {} {}'.format(a, b, c[0,1]))