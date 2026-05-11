#!/usr/bin/env python
import funky as f
import numpy as np
from pathlib import Path
import pickle
import sys


def main(argv):
    if len(argv) != 4: raise RuntimeError("""
    Listen pal, I need:
    1. A name for a new SIM directory.
    2. The number of simulations.
    3. The name of the output file.

    I could add more error handling, but you should know what you're doing.
                                          """)

    # will die if starting sim already exists
    (Path("~/SNANA/SNROOT/SIM")/argv[1]).expanduser().mkdir()

    rng = np.random.default_rng(seed=1)
    
    save = {}
    # Sample from prior: uniform over 0 < omega < 1, -3 < w < 0.
    theta_samples = rng.uniform(low=[0, -3], high=[1, 0], size=(int(argv[2]), 2))
    try:
            for i in range(theta_samples.shape[0]):
                print(f"I'm on {i}/{argv[2]}")
                mu, zhd = f.sim_wrapper(theta_samples[i], argv[1])
                save[i] = {"omega":theta_samples[i][0], 'w':theta_samples[i][1], "mu":mu, "zhd":zhd}
    except KeyboardInterrupt:
        print("\nWHY FATHER?")
        pass

    with (Path("~/SNANA/nre").expanduser()/argv[3]).open("wb") as fout: pickle.dump(save, fout, protocol=5)



if __name__ == "__main__": main(sys.argv)
