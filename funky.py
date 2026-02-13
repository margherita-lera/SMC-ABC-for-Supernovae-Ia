import numpy as np
from scipy.integrate import quad
from scipy.interpolate import interp1d
from statsmodels.nonparametric.smoothers_lowess import lowess

H0=72
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
    rng = np.random.default_rng(seed)
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