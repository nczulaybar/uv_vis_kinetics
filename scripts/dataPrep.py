import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import spectralFunctions as spec
from scipy.optimize import curve_fit

"""
Here we train a collection of gaussian-like functions to UV-Vis absorption 
spectra collected on solutions of known bromine and sodium tribromide concentration
over the wavelength range 360 to 650 nm. 

    *The pure bromine spectrum is represented by a sum of three gaussians.
    *The sodium tribromide spectrum is represented by a sum of two gaussians.

Once the individual spectral shapes are determined, the concentration of both
species in an unknown solution can be determined by finding the optimum intensity contribution of each peakshape to the observed absorption spectrum. 
"""

#load training data as pandas DataFrames
train1 = pd.read_csv('TRAIN1.TXT', encoding='utf-16', skiprows=5, sep='\t')
train2 = pd.read_csv('TRAIN2.TXT', encoding='utf-16', skiprows=5, sep='\t')

#transpose data (for clarity)
train1, train2 = train1.transpose(), train2.transpose()

#Get measurement times from first row
train1_t, train2_t = train1.iloc[[0]].values[0], train2.iloc[[0]].values[0]

#get wavelength values from first column
WLs = train1.index.values[1:].astype(float)


"""#############FIT RAW BROMINE SPECTRUM###############"""

#set upper and lower bounds for first training set
L1 = np.argwhere(WLs > 320.0)[0][0] 
L2 = np.argwhere(WLs > 650.0)[0][0]

xvals, yvals = WLs[L1:L2], train1[0][1:].values[L1:L2]

p0_Br2 = (3.0,280.0,30.0,
          0.7,390.0,20.0,
          0.2,460.0,20.0, 0.02) #Initial values for curve_fit

Br2opt, Br2cov = curve_fit(spec.gaussian3, xvals, yvals, p0_Br2) #optimize parameters

#compute the fitted spectrum
Br2_fit = spec.gaussian3(xvals, Br2opt[0], Br2opt[1], 
                    Br2opt[2], Br2opt[3], Br2opt[4], 
                    Br2opt[5], Br2opt[6], Br2opt[7], 
                    Br2opt[8], Br2opt[9]) 

#show each individual peak
g1, g2, g3 = (spec.gaussian(xvals, Br2opt[0], Br2opt[1], Br2opt[2]),
              spec.gaussian(xvals, Br2opt[3], Br2opt[4], Br2opt[5]),
              spec.gaussian(xvals, Br2opt[6], Br2opt[7], Br2opt[8])) 

#plot results
plt.figure()
plt.title('Pure Br$_2$ in Acetonitrile')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Absorbance (arb.)')
plt.plot(xvals, yvals, 'x', label='data')
plt.plot(xvals, Br2_fit, color='r', label='fit')
plt.plot(xvals, g1, xvals, g2, xvals, g3)
plt.legend()



def gauss5(WL, 
           h1, 
           h2, l2, w2, 
           h3, l3, w3):
    """
    gauss5(x, h1, h2, l2, w2, h3, l3, w3)
    
    computes the predicted absorbance value for given wavelength and Br2 height,
    with two additional Gaussian-like peaks to fit the NaBr3 peak contribtution.
    
    Parameters
    ----------
    WL: scalar
        Wavelength in nm
        
    h1: scalar
        Height of total Br2 spectrum
        
    h2, h3: scalar
        NaBr3 peak heights in absorbance units
        
    w1, w2: scalar
        NaBr3 peak widths in nm
        
    l1, l2: scalar
        NaBr3 peak centers in nm
    
    Returns
    -------
    Predicted Absorbance: float
    """
    return (h1*(Br2opt[0]*np.exp(-((WL-Br2opt[1])**2)/(2*Br2opt[2]**2)) + 
                Br2opt[3]*np.exp(-((WL-Br2opt[4])**2)/(2*Br2opt[5]**2)) +
                Br2opt[6]*np.exp(-((WL-Br2opt[7])**2)/(2*Br2opt[8]**2))) + 
            h2*np.exp(-((WL-l2)**2)/(2*w2**2)) +
            h3*np.exp(-((WL-l3)**2)/(2*w3**2)))
         
           
"""##########FIT SODIUM TRIBROMIDE SPECTRUM############"""

L1 = np.argwhere(WLs > 360.0)[0][0] #set upper and lower bounds
L2 = np.argwhere(WLs > 650.0)[0][0]

xvals, yvals = WLs[L1:L2], train1[len(train1_t)-1][1:].values[L1:L2]

NaBr3_p0 = (0.3, 
            1.0, 400, 20, 
            2.5, 340, 20) #Initial values for curve_fit

#optimize NaBr3 parameters
g5opt, g5cov = curve_fit(gauss5, xvals, yvals, NaBr3_p0) 

NaBr3_fit = gauss5(xvals, 
                   g5opt[0], 
                   g5opt[1], g5opt[2], g5opt[3], 
                   g5opt[4], g5opt[5], g5opt[6])

g1 = (spec.gaussian(xvals, g5opt[1], g5opt[2], g5opt[3])) #show each individual peak
g2 = (spec.gaussian(xvals, g5opt[4], g5opt[5], g5opt[6]))

#plot results
plt.figure()
plt.title('xBr$_2$ + yNaBr3 in Acetonitrile')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Absorbance (arb.)')
plt.plot(xvals, yvals, 'x', label='data')
plt.plot(xvals, NaBr3_fit, color='r', label='fit')
plt.plot(xvals, g1, xvals, g2)
plt.legend()


def gauss5_scale(WL, hBr2, hNaBr3):
    """
    gauss5_scale(x, h1, h2, l2, w2, h3, l3, w3)
    
    computes the predicted absorbance value for given 
    wavelength, Br2 height, and NaBr3 height.
    
    Parameters
    ----------
    WL: scalar
        Wavelength in nm
        
    hBr2: scalar
        height of Br2 absorption spectrum
    
    hNaBr3: scalar:
        height of NaBr3 absorption spectrum
    
    Returns
    -------
    Predicted Absorbance: float
    """
    return (hBr2*(Br2opt[0]*np.exp(-((WL-Br2opt[1])**2)/(2*Br2opt[2]**2)) + 
                  Br2opt[3]*np.exp(-((WL-Br2opt[4])**2)/(2*Br2opt[5]**2)) +
                  Br2opt[6]*np.exp(-((WL-Br2opt[7])**2)/(2*Br2opt[8]**2))) + 
            hNaBr3*(g5opt[1]*np.exp(-((WL-g5opt[2])**2)/(2*g5opt[3]**2)) +
                    g5opt[4]*np.exp(-((WL-g5opt[5])**2)/(2*g5opt[6]**2))))
                
"""###########TRAIN###############"""

L1 = np.argwhere(WLs > 360.0)[0][0] #set upper and lower bounds
L2 = np.argwhere(WLs > 650.0)[0][0]

Br2_conc_i = 0.00342 #Initial Br2 concentration in Mol/L.

(hBr2, hNaBr3) = np.zeros((2, len(train2_t)))

f, (ax1, ax2) = plt.subplots(1,2)
ax1.set_xlabel('Wavelength (nm)')
ax1.set_ylabel('Absorbance (arb.)')
ax2.set_xlabel('[NaBr$_3$] (M)')
ax2.set_ylabel('hNaBr$_3$ (arb.)')

for i in range(len(train2_t)):
    xvals, yvals = WLs[L1:L2], train2[i][1:].values[L1:L2]
    
    #optimize parameters
    train2_opt, train2_cov = curve_fit(gauss5_scale, xvals, yvals) 
    
    #add values to appropriate arrays
    (hBr2[i], hNaBr3[i]) = train2_opt
    
    #compute the fitted spectrum
    fit = gauss5_scale(xvals, train2_opt[0], train2_opt[1]) 
    
    #plot data and fit for each spectrum
    ax1.plot(xvals, yvals, 'x')
    ax1.plot(xvals, fit, color='r')
    
#compute [NaBr3] for all spectra
NaBr3_conc = Br2_conc_i * (1.0 - hBr2)

#fit calibration line to data
line, cov = curve_fit(spec.linear, NaBr3_conc, hNaBr3)

#plot calibration points ad line of best fit
ax2.plot(NaBr3_conc, hNaBr3, 'x')
ax2.plot(NaBr3_conc, spec.linear(NaBr3_conc, line[0], line[1]))


"""##############PREDICT##################"""

def get_concs(dataset):
    """
    get_concs(dataset)
    
    Computes the concentrations of Br2 and NaBr3 in acetonitrile from trained peak
    profiles and calibration spectra.
    
    Parameters
    ----------
    dataset: Pandas DataFrame containing wavelengths in the index column,
                time values in the first row, and absorbance readings in all cells.
    
    Returns
    _______
    time, Br2 concentration (M), NaBr3 concentration (M) (tuple of three NumPy arrays)
    """
    #get time values from datafile
    time = dataset.iloc[[0]].values[0]/60 
    
    low, high = 360, 650 #lower and upper wavelengths for fit
    
    #set upper and lower bounds
    L1 = np.argwhere(WLs > low)[0][0] 
    L2 = np.argwhere(WLs > high)[0][0]

    hbr2, hnabr3 = np.zeros((2, len(time))) #empty arrays for fitted parameters
    
    plt.figure()
    plt.axis([low, high, 0, 2])
    plt.title('All spectra + fits')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Absorbance (arb.)')

    for i in range(len(time)):
        xvals, yvals = WLs[L1:L2], dataset[i][1:].values[L1:L2]
        
        #optimize parameters
        g5Sopt, g5Scov = curve_fit(gauss5_scale, xvals, yvals) 
        
        #compute the fitted spectrum
        fit = gauss5_scale(xvals, g5Sopt[0], g5Sopt[1]) 
        
        #add values to appropriate arrays
        (hbr2[i], hnabr3[i]) = g5Sopt
        
        #plot data and fit for each spectrum
        plt.plot(xvals, yvals, 'x', color='black', alpha=0.4)
        plt.plot(xvals, fit, color='r')
        

    return (time, Br2_conc_i*hbr2, hnabr3/line[0])


#Predict Br2 and NaBr3 concentrations for all spectra in calibration
(time, cBr2, cNaBr3) = get_concs(train1)

#plot Conc. vs Time for the calibration run
plt.figure()
plt.title(r'Predicted Br$_{\rm 2}$ and NaBr$_{\rm 3}$ Concentrations')
plt.xlabel('Time (min)')
plt.ylabel('[X] (M)')
plt.plot(time, cBr2, 'x', color='red', label = r'[Br$_{\rm 2}$]')
plt.plot(time, cNaBr3, 'x', color='blue', label = r'[NaBr$_{\rm 3}$]')
plt.legend()

#SHOW ALL RESULT$
plt.show()


def write_concs(run_concs, name):
    """
    write_concs(run_concs, name)
	
	Write time, [Br2], [NaBr3] as space-separated values to a file ('name.txt')
	
	Parameters
	----------
	run_concs: a tuple containing three NumPy arrays: time, [Br2], [NaBr3]
	
	name: a string in quotes. This is the prefix of the file to be written. 
			'.txt' will be appended to the end of the prefix.
	"""
    with open(name+'.txt', 'w') as outfile:
		for i in range(len(run_concs[0])):
		    outfile.write(str(run_concs[0][i])+' '+
		                  str(run_concs[1][i])+' '+
		                  str(run_concs[2][i])+'\n')
		                  




if __name__ == '__main__':
    #Predict concentrations from other datasets
    run1_17C = pd.read_csv('run1_17C.TXT', encoding='utf-16', skiprows=5, sep='\t')
    run2_25C = pd.read_csv('run2_25C.TXT', encoding='utf-16', skiprows=5, sep='\t')
    run3_35C = pd.read_csv('run3_35C.TXT', encoding='utf-16', skiprows=5, sep='\t')


    run1_17C_concs = get_concs(run1_17C.transpose())
    run2_25C_concs = get_concs(run2_25C.transpose())
    run3_35C_concs = get_concs(run3_35C.transpose())

    write_concs(run1_17C_concs, '17C_concs')
    write_concs(run2_25C_concs, '25C_concs')
    write_concs(run3_35C_concs, '35C_concs')
    