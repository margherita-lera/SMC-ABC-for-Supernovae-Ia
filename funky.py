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
snana_dir = Path("/home/ubuntu/SNANA")
custom_inputs = snana_dir/"custom_input_files"


def smoother(z,mu):
    '''
    Smoothing non parametrico per fare la summary statistics
    '''
    window=0.52
    # per i dati osservati aggiungono un peso extra basato su sigma_mu, DA PROVARE A IMPLEMENTARE
    smoothed = lowess(mu, z, frac=window, it=3)

    z_grid = np.linspace(0.02, 0.45, 100)
    f_obs=interp1d(smoothed[:,0],smoothed[:,1],bounds_error=False, fill_value='extrapolate')
    mu_grid = f_obs(z_grid)

    return z_grid,mu_grid

def path_check(path):
    "Check if the path exists. Asks for overwrite permission."
    if Path.exists(Path(path)):
            while True:
                choice = input('This file already exists, are you sure you want to overwrite it?(y/n)\n').lower()
                if choice == '' or choice[0] == 'y': break
                elif choice[0] == 'n': raise FileExistsError("Then change 'run_name' you stoopid sandwich!")
                else:
                    print('INVALID OPTION\n')
                    continue

def snana_do(program, run_name, input_file=None, target_dir=None, SPEAK=True, check_path=False, **snana):
    """
    Ok, hear me out: you can run anything from SNANA (we have seen) with this thing!

    Parameters
    ----------
    program : str
        SNANA program to run.
    run_name : str
        Name of the run to work on.
    input_file : str
        Name of the input file.
    target_dir : str
        Where to output stuff.
    SPEAK : bool
        Wheter to print the stdout or not.
    check_path : bool
        Whether to check for the existence of the target_dir.
    **snana : kwargs(?)
        I love this sh!t. You can add whatever SNANA keyword! IMPORTANT: for snlc_sim.exe you possibly want to input OMEGA_MATTER and w0_LAMBDA.
        
    Examples
    --------
    snana_do('snlc_sim.exe',run_name='directory_of_work', SPEAK=False, OMEGA_MATTER=0.34, w0_LAMBDA=-1)
    In this case the default directories are used.
    snana_do('snlc_fit.exe', 'hehehehe')
    Simply runs the fit, gets stored in fits/hehehe. Outputs a .FITRES.TEXT and a SNANA.TEXT.
    snana_do('SALT2mu.exe',run_name=run_name,SPEAK=False)
    Obtains mu, gets stored as .FITRES file in salt2mus/run_name.

    """
    # Ero tentato di non mettere i defaults, ma ho avuto pietà di voi, voglio 14 birre
    defaults = {
        'snlc_sim.exe': {
            'Dir': snana_dir/"SNROOT/SIM"/run_name,
            'input_file': "sim_SDSS_custom.input",
            'extra_comm': ["GENVERSION", run_name]
        },
        'snlc_fit.exe': {
            'Dir': snana_dir/"fits"/run_name,
            'input_file': "snfit_SDSS_custom.nml",
            'extra_comm': ["VERSION_PHOTOMETRY", run_name, "TEXTFILE_PREFIX", f"{run_name}_fits"]
        },
        'SALT2mu.exe': {
            'Dir': snana_dir/"salt2mus"/run_name,
            'input_file': "SALT2mu_DES.input",
            'extra_comm': [f'file={str(snana_dir/"fits"/run_name/run_name)}_fits.FITRES.TEXT', f'prefix=SALT2mu_{run_name}']
        }
    }
    config = defaults.get(program)
    if config is not None:
        Dir = config['Dir']
        command = [program, str(custom_inputs/config['input_file'])] + config['extra_comm']  # program and input file to be run later
    else:
        Dir = snana_dir/target_dir/run_name
        command = [program, str(custom_inputs/input_file)]
    if check_path: path_check(Dir)
    Path.mkdir(Dir, exist_ok=True)  # snlc_sim.exe already creates its own dir, I hope it doesn't break lol
    # Add possible kwargs (OMEGA_MATTER w0_LAMBDA!!!!)
    for key, value in snana.items():
        command.append(key)
        command.append(str(value))
    result = subprocess.run(command, cwd=Dir, capture_output=True, text=True, check=True)
    if SPEAK: print(result.stdout)


def reality_check(input_file):
    '''
    Takes in input the file of a lightcurve. 
    Checks if there are at least 7 observations in the file that satisfy specific time constraints relative to the peak of the lightcurve (t0).
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
        os.remove(input_file)
        print(f"Removed {input_file} bc no valid PEAKMJD line.")
        return

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
        os.remove(input_file)
        print(f"Removed {input_file} bc no obs that t1 - t0 < 0.")
        return
    if not pool_greater_10:
        os.remove(input_file)
        print(f"Removed {input_file} bc no obs that t1 - t0 > 10.")
        return

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
        os.remove(input_file)
        print(f"Removed {input_file} because not enough obs in [-15,60].")
        return



def extract_mu_zhd_from_file(file_path):
    """
    Reads a file and extracts the arrays of values mu and z.
    The file should be the result of a fit process.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} was not found.")

    zhd_idx = -1
    mu_idx = -1
    
    zhd_vals = []
    mu_vals = []
    
    # Using 'with open' ensures the file is safely closed after reading
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Identify column indices from the VARNAMES line
            if line.startswith('VARNAMES:'):
                tokens = line.split()
                zhd_idx = tokens.index('zHD')
                mu_idx = tokens.index('MU')
                
            # Extract data from the SN rows
            elif line.startswith('SN:'):
                if zhd_idx == -1 or mu_idx == -1:
                    raise ValueError("Encountered data rows before finding VARNAMES header.")
                    
                tokens = line.split()
                
                # Extract and convert to float
                zhd_vals.append(float(tokens[zhd_idx]))
                mu_vals.append(float(tokens[mu_idx]))
                
    return np.array(mu_vals), np.array(zhd_vals)


def sim_wrapper(theta_t_i, run_name, mus= snana_dir/"salt2mus", speak=False):
    """
    Launches simulation, fitting, and mu calculation. 
    Returns the arrays of z and mu, ready for improper future usage. 

    Parameters
    ----------
    theta_t_i : list
        Omega_M and w, additional parameters will require additional coding.
    run_name : str
        Name of the simulation. Everything will be stored in directories with this name.
    speak : bool
        Set to True if you're trying to understand what's going on inside.
    mus: str
        The path leading to the directory which contains all the SALT2mu results.
        I know it's ugly but if you don't touch the state of the art of the directories this will never bother you, I swear.

    Returns
    -------
    mu : np.array
        mu.
    zhd : np.array
        The TRUE, ULTIMATE REDSHIFT?
    """
    
    # eventuali selection cuts


    # far partire la simulazione con theta i t
    snana_do('snlc_sim.exe',run_name=run_name, SPEAK=speak, OMEGA_MATTER=theta_t_i[0], w0_LAMBDA=theta_t_i[1])
    
    # Check that the curves are complete enough
    checked_dir=snana_dir/'SNROOT/SIM'/run_name

    for file_path in checked_dir.glob('*.DAT'):
        reality_check(file_path)

    #prendere i dati di output e farci fit
    snana_do('snlc_fit.exe', run_name=run_name,SPEAK=speak)

    # ricava MU!
    snana_do('SALT2mu.exe',run_name=run_name,SPEAK=speak)

    mu_dir=mus/run_name
    salt2mu_output = f"{str(mu_dir)}/SALT2mu_{run_name}.FITRES"

    mu, zhd = extract_mu_zhd_from_file(salt2mu_output)
    
    return mu, zhd