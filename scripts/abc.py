#!/usr/bin/env python
"""
This script runs the SMC-ABC algorithm.

The script was not intended to run anywhere else than on our machine. If it needs to be run on other machines, the paths must be changed.
"""
import funky.snanawrap as f
import numpy as np
import scipy
import pickle
rng=np.random.default_rng(seed=1)

def main():
    # REAL DATA
    mu_data,z_data=f.extract_mu_zhd_from_file('/home/ubuntu/SNANA/salt2mus/realdata/SALT2mu_realdata.FITRES')
    z_data,mu_data=(f.smoother(z_data,mu_data))  # summary statistics of real data
    
    N = 150  # simulated 'particles' number

    ## LOAD INITIAL SIMS
    with open("/home/ubuntu/SNANA/nre/nreSims.pickle", "rb") as fin: preSim = pickle.load(fin)
    
    # ABC t=1
    w = np.repeat(1/N,repeats=N)  # weights of params
    distances=np.empty(N)
    theta_t = np.empty((N, 2))  # theta_1
    for n in range(N):
        sim = preSim[n]  # uses the first N sims, but could be chosen at random...
        theta_t[n] = (sim['omega'], sim['w'])  # cosmological w
        # Note: mu and z have same dim, but variable from sim to sim. After smoothing we have 100 points.
        _, mu_1 = f.smoother(sim['zhd'], sim['mu'])
        delta = np.median(np.abs(mu_data - mu_1))
        distances[n] = delta
    del preSim
    tau_square = 2*np.cov(theta_t, rowvar=False)

    # ABC t>1
    ## Defining variables
    eps=[]
    medians=[]
    acc_rates=[]
    theta_history = [theta_t]
    tau_history = [tau_square]  
    
    medians.append(np.median(distances))
    epsilon_t = np.percentile(distances,q=75)
    eps.append(epsilon_t)
    acc_rates.append(1.)
    print('starting epsilon:',epsilon_t)
    k=0
    while epsilon_t > 0.033:
        k+=1
        print('start iteration',k)
        theta_new=[]  # Will become the new theta_t
        weights_new=[]  # Will become the new w
        distances_new=[]
        n_proposals=0
    
        # Updates and accepts N particles. At the end, weights and epsilon will be updated
        for i in range(N):
            print('N =',i)
            while True:
                n_proposals+=1
                # sample particle
                theta_star=rng.choice(theta_t, p=w)
                # perturb particle
                theta_i_t=rng.multivariate_normal(theta_star, tau_square)  # propose a new update for theta
                if not ((0<theta_i_t[0]<1) and (-3<theta_i_t[1]<0)): continue  # check if out of domain
                
                ## simulate z and mu given choice of theta
                mu_i_t, z_i_t= f.sim_wrapper(theta_i_t,'abcTest',speak=False)
                
                ## create summary statistics
                _,mu_i_t=f.smoother(z_i_t,mu_i_t)
    
                ## compute distance from summary stat. of real data
                delta = np.median(np.abs(mu_data - mu_i_t))
                print('delta proposto:',delta)
                if delta<epsilon_t:
                    print('accettato',theta_i_t)
                    break  # if particle accepted
                else: print('rifiutato')
            
            theta_new.append(theta_i_t)
            distances_new.append(delta)
    
            # weight update
            denom = 0.0
            for j in range(N):
                denom += w[j] * scipy.stats.multivariate_normal.pdf(x=theta_i_t,mean=theta_t[j],cov=tau_square)
            weight = 1 / denom
            weights_new.append(weight)
    
    
        # Once found N particles accepted, update the main parameters
        print('new theta done! Iteration',k)
        print('acceptance rate:', N/n_proposals)
        acc_rates.append(N/n_proposals)
    
        print('mean distances:',np.mean(distances_new))
        print('median distances:',np.median(distances_new))
        medians.append(np.median(distances_new))
    
        # w update
        weights_new=np.array(weights_new)
        w = weights_new / np.sum(weights_new)
    
        # theta_t update
        theta_t=np.array(theta_new)
        theta_history.append(theta_t)
        
        # epsilon update
        epsilon_t= np.percentile(distances_new,q=50)
        eps.append(epsilon_t)
        print('epsilon: ',epsilon_t)
        tau_square=2*np.cov(theta_t.T,aweights=w)
        tau_history.append(tau_square)
        
    saveOut = {
        "eps":eps,
        "medians":medians,
        "acc_rates":acc_rates,
        "theta_history":theta_history,
        "tau_history":tau_history
    }
    with open("/home/ubuntu/gioAbc/outLists.pickle", "wb") as fout: pickle.dump(saveOut, fout, protocol=5)

    print("I'm done here boss. Can I go home now?")

    return 0


if __name__ == "__main__": main()
