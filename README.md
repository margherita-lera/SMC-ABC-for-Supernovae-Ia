<h1 align=center> SMC-ABC-for-Supernovae-Ia </h1>

Repository for the final project of the Information Theory exam.

<h2 align=center> Tree </h2>

`funky.py` is a SNANA wrapping module called in the main scripts and notebooks. Be sure of including it in your `PYTHONPATH` terminal variable, it is our current approach. We know no better yet.

The main files are `abc.py` and `nre_ifi.ipynb` where we respectively run the SMC-ABC and NRE algorithms.


```
.
├── SNInput  # SNANA input files
│   ├── SALT2mu_DES.input         
│   ├── sim_SDSS_custom.input     # actual simulations settings
│   └── sim_SDSS_gigi_wip_dontouch.input  # I would like to kill this, I don't think anyone knows what this is
│   ├── snfit_SDSS_custom.nml     # simulations fit
│   └── snfit_SDSS_real_data.nml  # real data fit
├── scripts
│   ├── abc.py      # SMC-ABC
│   └── runSims.py  # run SNANA simulations on our prior
├── funky.py       # SNANA wrapper and smoothing module
├── nre_ifi.ipynb  # NRE
└── abc_out.ipynb  # SMC-ABC output visualization
```
