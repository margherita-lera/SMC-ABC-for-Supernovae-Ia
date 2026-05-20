<h1 align=center> SBI-for-Supernovae-Ia </h1>

Final project of the Information Theory and Inference course.

We compare Sequential Monte Carlo Approximate Bayesian Computation to Neural likelihood-Ratio Estimation in a cosmological context.

<h2 align=center> Tree </h2>

`funky` is the main package containing a `snanawrap.py` module to run SNANA from python, and `nreblocks.py` module defining the NRE class and functions. Be sure of including the package in your `PYTHONPATH` terminal variable, it is our current approach. We know no better yet.

The main files are `scripts/abc.py` and `nre_ifi.ipynb` where we respectively run the SMC-ABC and NRE algorithms.


```
.
├── funky  # main repo package
│   ├── nreblocks.py  # NRE class and bayesian functions
│   └── snanawrap.py  # SNANA wrapper and smoothing module
├── SNInput  # SNANA input files
│   ├── SALT2mu_DES.input         # SALT2mu
│   ├── sim_SDSS_custom.input     # simulations
│   ├── snfit_SDSS_custom.nml     # fit on simulations
│   └── snfit_SDSS_real_data.nml  # fit on real data
├── scripts
│   ├── abc.py      # SMC-ABC
│   └── runSims.py  # run SNANA simulations on our prior
├── nre.ipynb      # NRE
└── abc_out.ipynb  # SMC-ABC output visualization
```
