#!/usr/bin/env python
"""
This script runs the SMC-ABC algorithm.

The script was not intended to run anywhere else than on our machine. Hopefully by just tinkering with the paths you should be able to port it.
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
        theta_t[n] = (sim['omega'], sim['w'])  # cosmological w not the above weights ofc
        # Note: mu and z have same dim, but variable from sim to sim. After smoothing we have 100 points.
        _, mu_1 = f.smoother(sim['zhd'], sim['mu'])
        delta = np.median(np.abs(mu_data - mu_1))
        distances[n] = delta  # I keep the delta because of readability with old code, but I despise the middle passage
    del preSim  # just because
    tau_square = 2*np.cov(theta_t, rowvar=False)

    # ABC t>1
    ## STUFF TO SAVE
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
        theta_new=[]  # diventerà il nuovo theta_t
        weights_new=[]  # diventeranno il nuovo w
        distances_new=[]
        n_proposals=0
    
        # Voglio N particles che mi piacciono. Alla fine aggiornerò pesi e epsilon. # innanzitutto l'erba voglio non cresce neanche nel giardino del re.
        for i in range(N):
            print('N =',i)
            while True:
                n_proposals+=1
                # sample particle
                idx=rng.choice(range(N), p=w)  # You could directly theta_star = rng.choice(theta_t, p=w) but I won't judge (I will)
                theta_star=theta_t[idx]
                #perturb particle!
                theta_i_t=rng.multivariate_normal(theta_star, tau_square)  # propongo un aggiornamento di un theta. # Sì, dai, lo accetto.
                if not ((0<theta_i_t[0]<1) and (-3<theta_i_t[1]<0)): continue  # scarto se sono fuori dal dominio
                #print(theta_i_t)
                ## simulate z and mu given choice of theta
                # try:
                mu_i_t, z_i_t= f.sim_wrapper(theta_i_t,'abcTest',speak=False)
                # except: 
                #     print('ERROR: simulation process failed')  # Only weaklings do not believe in their code. I am not a weakling. I will annihilate any error dares attack me.
                #     continue
    
                ## create summary statistics
                _,mu_i_t=f.smoother(z_i_t,mu_i_t)
    
                ## compute distance from summary stat. of real data
                delta = np.median(np.abs(mu_data - mu_i_t))
                print('delta proposto:',delta)
                if delta<epsilon_t:
                    print('accettato',theta_i_t)
                    break  #Ho trovato una particle che mi piace. # contenta tu...
                else: print('rifiutato')
            
            theta_new.append(theta_i_t)
            distances_new.append(delta)
    
            # aggiorna pesi ---- DA RICONTROLLARE ---- FORSE NO, È GIÀ STATO RICONTROLLATO(?) ---- FORSE MEGLIO RICONTROLLARE DAI ---- BE', VA IN ERRORE PERCHÉ TAU NON È SEMIDEFINITA POSITIVA
            denom = 0.0
            for j in range(N):
                denom += w[j] * scipy.stats.multivariate_normal.pdf(x=theta_i_t,mean=theta_t[j],cov=tau_square)
            weight = 1 / denom
            weights_new.append(weight)
    
    
        # Ora ho N particles che mi piacciono. Aggiorno tutto
        print('new theta done! Iteration',k)
        print('acceptance rate:', N/n_proposals)
        acc_rates.append(N/n_proposals)
    
        # se media e mediana salgono, tau troppo largo. # no bodyshaming.
        print('mean distances:',np.mean(distances_new))
        print('median distances:',np.median(distances_new))
        medians.append(np.median(distances_new))
    
        # w update
        weights_new=np.array(weights_new)
        w = weights_new / np.sum(weights_new)
    
        # theta_t update
        theta_t=np.array(theta_new)
        theta_history.append(theta_t)
        
        #epsilon update
        epsilon_t= np.percentile(distances_new,q=50)
        eps.append(epsilon_t)
        print('epsilon: ',epsilon_t)
        tau_square=2*np.cov(theta_t.T,aweights=w,bias=False)  # WOW, FORSE, ti odio. Potevi usare rowvars anche qui eh. E soprattutto perché c'è bias=False e su no? Comunque è False di default...
        tau_history.append(tau_square)
        # è finita. # No, perché?! Non sono pronto a questa cosa # Ho il mio vettore theta di 500 particelle che seguono la posterior.
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
