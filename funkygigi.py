import numpy as np
from scipy.integrate import quad
from scipy.interpolate import interp1d
from statsmodels.nonparametric.smoothers_lowess import lowess
import random
from pathlib import Path
import subprocess
import os

H0=72  # 65? See section 3.3 vs 4.2
c=299792.458
rng=np.random.default_rng(seed=1)

########### FIT E DATI REALI DI MU, Z DA SDSS. GET_HUBBLE_REAL ############################
def get_hubble_real():
    '''
    Funzione da cui si otterranno mu e z per i dati reali. 
    Per ora sono due array che mi ha generato chat, che non seguono la distribuzione
    dell'altra simulazione dopo.
    Poi sarà un fit fatto su dati veri SDSS da cui si ottiene mu, e si sa anche z fotometrico.
    '''

    mu_data = np.array([
    35.72,36.05,36.18,36.42,36.55,36.80,37.01,37.22,37.38,37.60,
    37.73,37.95,38.12,38.30,38.47,38.66,38.83,39.01,39.16,39.33,
    39.51,39.66,39.83,40.01,40.14,40.33,40.48,40.65,40.80,40.98,
    41.12,41.29,41.45,41.62,41.78,41.94,42.11,42.29,42.44,42.61,
    42.77,42.93,43.08,43.24,43.39,43.55,43.70,43.86,44.01,44.16,
    44.31,44.47,44.61,44.76,44.91,45.05,45.20,45.34,45.48,45.63,
    45.77,45.91,46.05,46.19,46.33,46.47,46.61,46.74,46.88,47.02,
    47.15,47.29,47.42,47.55,47.69,47.82,47.95,48.08,48.21,48.34,
    48.47,48.60,48.73,48.86,48.98,49.11,49.23,49.36,49.48,49.61,
    49.73,49.85,49.98,50.10,50.22,50.34,50.46,50.58,50.70,50.82,
    50.94,51.06,51.18,51.29,51.41,51.53,51.64,51.76,51.87,51.99,
    35.89,36.11,36.50,36.71,37.14,37.41,37.85,38.07,38.36,38.52,
    38.71,39.04,39.21,39.47,39.69,39.90,40.13,40.31,40.57,40.73,
    41.01,41.17,41.42,41.58,41.83,41.99,42.25,42.41,42.67,42.82,
    43.09,43.24,43.50,43.66,43.92,44.07,44.33,44.49,44.75,44.90,
    45.16,45.31,45.57,45.72,45.98,46.13,46.39,46.54,46.80,46.95,
    47.21,47.36,47.62,47.77,48.03,48.18,48.44,48.59,48.85,49.00,
    49.26,49.41,49.67,49.82,50.08,50.23,50.49,50.64,50.90,51.05,
    51.31,51.46,51.72,51.87,52.13,52.27,52.53,52.68,52.94,53.08,
    53.34,53.48,53.74,53.88,54.14,54.28
    ])
    z_data = np.array([
    0.021,0.025,0.028,0.031,0.034,0.037,0.041,0.045,0.048,0.052,
    0.055,0.059,0.063,0.067,0.071,0.075,0.079,0.083,0.087,0.091,
    0.095,0.099,0.103,0.107,0.111,0.115,0.119,0.123,0.127,0.131,
    0.135,0.139,0.143,0.147,0.151,0.155,0.159,0.163,0.167,0.171,
    0.175,0.179,0.183,0.187,0.191,0.195,0.199,0.203,0.207,0.211,
    0.215,0.219,0.223,0.227,0.231,0.235,0.239,0.243,0.247,0.251,
    0.255,0.259,0.263,0.267,0.271,0.275,0.279,0.283,0.287,0.291,
    0.295,0.299,0.303,0.307,0.311,0.315,0.319,0.323,0.327,0.331,
    0.335,0.339,0.343,0.347,0.351,0.355,0.359,0.363,0.367,0.371,
    0.375,0.379,0.383,0.387,0.391,0.395,0.399,0.403,0.407,0.411,
    0.415,0.419,0.423,0.427,0.431,0.435,0.439,0.443,0.447,0.450,
    0.023,0.027,0.032,0.036,0.042,0.047,0.053,0.058,0.064,0.069,
    0.074,0.080,0.084,0.089,0.094,0.100,0.105,0.110,0.116,0.120,
    0.126,0.130,0.136,0.140,0.146,0.150,0.156,0.160,0.166,0.170,
    0.176,0.180,0.186,0.190,0.196,0.200,0.206,0.210,0.216,0.220,
    0.226,0.230,0.236,0.240,0.246,0.250,0.256,0.260,0.266,0.270,
    0.276,0.280,0.286,0.290,0.296,0.300,0.306,0.310,0.316,0.320,
    0.326,0.330,0.336,0.340,0.346,0.350,0.356,0.360,0.366,0.370,
    0.376,0.380,0.386,0.390,0.396,0.400,0.406,0.410,0.416,0.420,
    0.426,0.430,0.436,0.440,0.446,0.449
    ])
    return z_data, mu_data

################ SIMULAZIONE DI MU, Z. VEDI GET_HUBBLE_SIM #######################################
def E(z,omega_m):
    '''
    Per calcolo di distanza di luminosità. H(z).
    '''
    return np.sqrt(omega_m*(1+z)**3 + 1-omega_m)
            # Calcolo distanza luminosa con integrazione numerica
def luminosity_distance(z, o):
    '''
    distanza di luminosità dato z e omega_m. Serve per calcolare manualmente mu.
    '''
    integral = quad(lambda zp: 1.0/E(zp, o), 0, z)[0]
    dL = (c/H0) * (1+z) * integral  # in Mpc
    return dL

def sample_redshift(N, z_min=0.02, z_max=0.45, beta=1.5, seed=42):
    '''
    Sample di redshift che segue una pdf esponenziale.
    Sto facendo una finta simulazione di z. Poi questo sampling
    sarà già presente in automatico dentro sim.exe.
    '''
    u = rng.uniform(0, 1, N)
    A = (1 + z_max)**(beta + 1) - (1 + z_min)**(beta + 1)
    B = (1 + z_min)**(beta + 1)
    z = (u * A + B)**(1 / (beta + 1)) - 1
    return z

def get_hubble_sim(theta_t):
    '''
    Fa uso delle funzioni sopra per ottenere 200 sample di mu e di z. 
    Questa funzione dopo dovrà fare simulazione di 200 sample dato theta,
    fit, e ricavo mu e z. 
    '''
    z_t = sample_redshift(200) # questo va sostituito da simulazione snana.
        # Calcolo mu
    mu_t = np.array([5*np.log10(luminosity_distance(zi,theta_t[0])) + 25 for zi in z_t])  # questo va sostituito da fit snana.
    mu_t +=rng.normal(0,0.2,size=len(mu_t))
        #ora ho la coppia (z,mu) per il diagramma di Hubble.
    z_t=np.sort(z_t)
    return z_t, mu_t
#################################################################################


########## SMOOTHING NON PARAMETRICO PER OTTENERE LA SUMMARY STATISTICS ###################################à
def smoother(z,mu):
    window=0.52
    # per i dati osservati aggiungono un peso extra basato su sigma_mu, DA PROVARE A IMPLEMENTARE
    smoothed = lowess(mu, z, frac=window, it=3)

    z_grid = np.linspace(0.02, 0.45, 100)
    f_obs=interp1d(smoothed[:,0],smoothed[:,1],bounds_error=False, fill_value='extrapolate')
    mu_grid = f_obs(z_grid)

    return z_grid,mu_grid


################## wrapper ###############################

def sample_lightcurve(input_file):
    '''
    Takes in input the file of a lightcurve. 
    Rewrites into the file only 7 observation, pooled with a specific selection criteria.
    '''
    
    with open(input_file, 'r') as f: # ONLY ONE FILE
        lines = f.readlines()

    t0 = None
    header = []
    obs_lines = []
    footer = []

    # 1. Parse the file
    for line in lines:
        if line.startswith('PEAKMJD:'):
            t0 = float(line.split()[1]) # peak of lightcurve
        
        if line.startswith('OBS:'):
            obs_lines.append(line)          # entire measure, also with time
        elif line.startswith('END_PHOTOMETRY:'):
            footer.append(line)
        elif not line.startswith('TRIGGER:'): 
            header.append(line)

    if t0 is None:
        raise ValueError("Could not find PEAKMJD in the header.")

    # 2. Categorize observations into pools
    pool_less_0 = []
    pool_greater_10 = []
    
    for line in obs_lines:
        t1 = float(line.split()[1])
        delta = t1 - t0
        if delta < 0:
            pool_less_0.append(line)
        if delta > 10:
            pool_greater_10.append(line)

    # Make sure we have enough data to satisfy the bounds
    if not pool_less_0:
        raise ValueError("No observations found where t1 - t0 < 0.")
    if not pool_greater_10:
        raise ValueError("No observations found where t1 - t0 > 10.")

    # 3. Randomly select the first two required rows
    selected_less_0 = random.choice(pool_less_0)
    selected_greater_10 = random.choice(pool_greater_10)
    
    # Keep track of what we've already picked so we don't duplicate
    already_selected = {selected_less_0, selected_greater_10}

    # 4. Create a pool for the remaining 5 rows, excluding the ones we just picked
    pool_in_range = []
    for line in obs_lines:
        if line in already_selected:
            continue  # Skip rows we already chose
            
        t1 = float(line.split()[1])
        delta = t1 - t0
        
        if -15 <= delta <= 60:
            pool_in_range.append(line) # remaining observations in time range of interest

    if len(pool_in_range) < 5:
        raise ValueError(f"Not enough unique observations in the [-15, 60] range. Found {len(pool_in_range)}, need 5.")

    # Randomly sample exactly 5 unique rows from this range
    selected_in_range = random.sample(pool_in_range, 5)

    # 5. Combine and sort chronologically
    final_selection = [selected_less_0, selected_greater_10] + selected_in_range
    final_selection.sort(key=lambda x: float(x.split()[1]))
    os.makedirs('sampled_lightcurves', exist_ok=True)
    output_file = 'sampled_lightcurves/'+os.path.basename(input_file) #overwriting original file

    # 6. Write out the new file
    with open(output_file, 'w') as f:
        for line in header:
            if line.startswith('NOBS:'):
                f.write(f"NOBS: {len(final_selection)}\n")
            else:
                f.write(line)
        
        for line in final_selection:
            f.write(line)
            
        for line in footer:
            f.write(line)



def extract_mu_zhel_from_file(file_path):
    """
    Reads a file and extracts the arrays of values mu and z.
    The file should be the result of a fit process.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} was not found.")

    zhel_idx = -1
    mu_idx = -1
    
    zhel_vals = []
    mu_vals = []
    
    # Using 'with open' ensures the file is safely closed after reading
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Identify column indices from the VARNAMES line
            if line.startswith('VARNAMES:'):
                tokens = line.split()
                zhel_idx = tokens.index('zHEL')
                mu_idx = tokens.index('MU')
                
            # Extract data from the SN rows
            elif line.startswith('SN:'):
                if zhel_idx == -1 or mu_idx == -1:
                    raise ValueError("Encountered data rows before finding VARNAMES header.")
                    
                tokens = line.split()
                
                # Extract and convert to float
                zhel_vals.append(float(tokens[zhel_idx]))
                mu_vals.append(float(tokens[mu_idx]))
                
    return np.array(mu_vals), np.array(zhel_vals)



def process_dat_files(directory_path, action_func):
    """
    Maps the function action_func into all the files of a directory.
    """
    # Create a Path object for the target directory
    directory = Path(directory_path)
    
    # Check if the directory actually exists to avoid errors
    if not directory.is_dir():
        print(f"Error: The directory '{directory_path}' does not exist.")
        return

    # Use .glob() to find all files ending in .dat
    for file_path in directory.glob('*.DAT'):
        # Pass the file path to your custom action function
        action_func(file_path)



def sim_wrapper_hubble(theta_t_i):
    """
    Launches an executable with arguments, waits for it to finish, 
    and then executes the next steps.
    omega_w is a list of strings, e.g. ["OMEGA_MATTER", "0.3", "w", 0.7"]

    """
    theta= ['OMEGA_MATTER', str(theta_t_i[0]), 'w0_LAMBDA', str(theta_t_i[1])]

    ## nomi dei files
    nome_run = "TEST1" ## it is like this in the three input files, watch out for it!
    nome_file_input = "sim_SDSS_custom.input"
    nome_file_nml = "snfit_SDSS_custom.nml"
    nome_file_salt2mu = "SALT2mu_DES.input"
    ## paths
    snana_dir = Path("/home/ubuntu/SNANA")
    ## dir where we save snlc_sim.exe output .dat files 
    sim_dir_path = snana_dir/"SNROOT/SIM"/nome_run  # Sì, il mio autismo è esploso quando ho scoperto questa cosa disgustosa eheheheh
    ## check for existing simulation
    if Path.exists(sim_dir_path):
        while True:
            choice = input('This SIM already exists, are you sure you want to overwrite it?(y/n)\n').lower()
            if choice == '' or choice[0] == 'y': break
            elif choice[0] == 'n': raise FileExistsError('too bad')
            else:
                print('INVALID OPTION\n')
                continue
    Path.mkdir((fit_dir := snana_dir/"fits"/nome_run), exist_okay=True)
    ## dir of the input files
    snlc_sim_input = (custdir := snana_dir/"custom_input_files")/nome_file_input
    snlc_fit_input = custdir/nome_file_nml
    salt2mu_input = custdir/nome_file_salt2mu
    ## fix input file and prefix of salt2mu
    with salt2mu_input.open('r') as fin: mulines = fin.readlines()
    mulines[0] = f'file={str(fit_dir)}.FITRES.TEXT\n'
    mulines[1] = f'prefix=SALT2mu_{nome_run}\n'
    with salt2mu_input.open('w') as fout: fout.writelines(mulines)

    sim_command = ["snlc_sim.exe", str(snlc_sim_input)] + theta
    fit_command = ["snlc_fit.exe", str(snlc_fit_input)]
    salt2mu_command = ["SALT2mu.exe", str(salt2mu_input)]

    # simulation of tot lightcurves
    result = subprocess.run(sim_command, capture_output=True, text=True, check=True)
    
    print("The .exe finished running successfully!")
    print(f"Here is what the .exe output: {result.stdout}")
    print("cleaning")

    # extracts points for all the resulting files
    process_dat_files(sim_dir_path, sample_lightcurve) 
    print("extracted 7 points from dat files")

    # fit points
    print("Launching fit: snlc_fit.exe")
    result = subprocess.run(fit_command, cwd=fit_dir, capture_output=True, text=True, check=True)
    print(result.stdout)
    print("fit done, output should be in where you launched this script")
    result = subprocess.run(salt2mu_command, cwd=fit_dir, capture_output=True, text=True, check=True)
    salt2mu_output = f"{str(fit_dir)}/SALT2mu_{nome_run}.FITRES"
    print(f"Salt2mu output: {result.stdout}")

    # extract mu and z
    mu, zhel = extract_mu_zhel_from_file(salt2mu_output)
    return mu, zhel




#def real_wrapper_hubble():
