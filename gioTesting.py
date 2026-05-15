import emcee
import corner
import numpy as np
import matplotlib.pyplot as plt
import funky as f
import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
import pickle
rng=np.random.default_rng(seed=1)

def build_mlp(input_dim, hidden_dim, output_dim, layers, activation=nn.GELU()):
    """Create an MLP from the configuration."""
    seq = [nn.Linear(input_dim, hidden_dim), activation]
    for _ in range(layers):
        seq += [nn.Linear(hidden_dim, hidden_dim), activation]
    seq += [nn.Linear(hidden_dim, output_dim)]
    return nn.Sequential(*seq)


class NeuralRatioEstimator(pl.LightningModule):
    """ Simple neural likelihood-to-evidence ratio estimator, using an MLP as a parameterized classifier.
    """
    def __init__(self, x_dim, theta_dim):
        super().__init__()
        self.classifier = build_mlp(input_dim=x_dim + theta_dim, hidden_dim=128, output_dim=1, layers=4)

    def forward(self, x):
        return self.classifier(x)

    def loss(self, x, theta):

        # Repeat x in groups of 2 along batch axis
        x = x.repeat_interleave(2, dim=0)

        # Get a shuffled version of theta
        theta_shuffled = theta[torch.randperm(theta.shape[0])]

        # Interleave theta and shuffled theta
        theta = torch.stack([theta, theta_shuffled], dim=1).reshape(-1, theta.shape[1])

        # Get labels; ones for pairs from joint, zeros for pairs from marginals
        labels = torch.ones(x.shape[0], device=x.device)
        labels[1::2] = 0.0

        # Pass through parameterized classifier to get logits
        logits = self(torch.cat([x, theta], dim=1))
        probs = torch.sigmoid(logits).squeeze()

        return nn.BCELoss(reduction='none')(probs, labels)


    def training_step(self, batch, batch_idx):
        x, theta = batch
        loss = self.loss(x, theta).mean()
        self.log("train_loss", loss, on_step=False, on_epoch=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, theta = batch
        loss = self.loss(x, theta).mean()
        self.log("val_loss", loss)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=3e-4)


def log_prior(thetas):
    if 0 < thetas[0] < 1 and -3 < thetas[1] < 0: return 0
    else: return -np.inf


def log_like(theta, mu, z, theta_mean, theta_std, mu_mean, mu_std, z_mean, z_std, nre):
    thetaTest = torch.tensor((theta - theta_mean) / theta_std).float()
    muTest = torch.tensor((mu - mu_mean) / mu_std).float()
    zTest = torch.tensor((z - z_mean) / z_std).float()
    xTest = torch.concatenate([muTest, zTest])
    with torch.no_grad():
        nre.eval()
        return nre.classifier(torch.cat([xTest, thetaTest], dim=-1))

def log_post(theta, mu, z, theta_mean, theta_std, mu_mean, mu_std, z_mean, z_std, nre):
    lp = log_prior(theta)
    if not np.isfinite(lp): return -np.inf
    else: return lp + log_like(theta, mu, z, theta_mean, theta_std, mu_mean, mu_std, z_mean, z_std, nre)

def test_test_data(theta_mean, theta_std, mu_mean, mu_std, z_mean, z_std, nre):
    muReal, zReal = f.extract_mu_zhd_from_file('/home/ubuntu/SNANA/salt2mus/realdata/SALT2mu_realdata.FITRES')
    muReal, zReal = muReal[:73], zReal[:73]

    ndim, nwalkers = 2, 32
    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_post, args=(muReal, zReal, theta_mean, theta_std, mu_mean, mu_std, z_mean, z_std, nre,))  # Init

    # pos = rng.standard_normal((nwalkers, ndim))  # should be np.random.randn equivalent # starting theta position
    pos = rng.uniform((0, -3), (1, 0), size=(nwalkers, ndim))
    sampler.run_mcmc(pos, 5000, progress=True)  # run
    # flat_samples = sampler.get_chain(discard=1000, flat=True)  # get chain, look for what's flat
    # return corner.corner(flat_samples, range=[(0, 1), (-3,0)], labels=[r"$\Omega_M$", "w"])
    return sampler
    


def main():
    nre = NeuralRatioEstimator.load_from_checkpoint('nrelogs/nre_log_1/version_2/checkpoints/epoch=29-step=1350.ckpt', x_dim=73*2, theta_dim=2)
    with open("nreSims.pickle", "rb") as fin: sims = pickle.load(fin)
    theta = np.empty((len(sims), 2))
    mu = np.empty((len(sims), 73))
    z = np.empty((len(sims), 73)) 
    for i in range(len(sims)):
        theta[i] = (sims[i]['omega'], sims[i]['w'])
        mu[i] = sims[i]['mu'][:73]
        z[i] = sims[i]['zhd'][:73]
    theta_mean, theta_std = theta.mean(axis=0), theta.std(axis=0)
    mu_mean, mu_std = mu.mean(), mu.std()  # non mi convince la media, sul notebook fa dim0
    z_mean, z_std = z.mean(), z.std()

    check = 'yes'
    while not check or check.lower()[0] == 'y':
        # I got lost on what I was doing, I should replace the sims with the real data lol...
#        with open("nreSims.pickle", "rb") as fin: sim = pickle.load(fin)[rng.integers(6320)]
#        thetaTest, muTest, zTest = (sim['omega'], sim['w']), sim['mu'][:73], sim['zhd'][:73]
#        thetaTest = torch.tensor((thetaTest - theta_mean) / theta_std).float()
#        muTest = torch.tensor((muTest - mu_mean) / mu_std).float()
#        zTest = torch.tensor((zTest - z_mean) / z_std).float()
#        xTest = torch.cat([muTest, zTest])

        muReal, zReal = f.extract_mu_zhd_from_file('/home/ubuntu/SNANA/salt2mus/realdata/SALT2mu_realdata.FITRES')
        muReal, zReal = muReal[:73], zReal[:73]

        ndim, nwalkers = 2, 32
        sampler = emcee.EnsembleSampler(nwalkers, ndim, log_post, args=(muReal, zReal, theta_mean, theta_std, mu_mean, mu_std, z_mean, z_std, nre,))  # Init

        pos = rng.standard_normal((nwalkers, ndim))  # should be np.random.randn equivalent # starting position
        sampler.run_mcmc(pos, 5000, progress=True)  # run
        flat_samples = sampler.get_chain(discard=1000, flat=True)  # get chain, look for what's flat
        fig = corner.corner(flat_samples, range=[(0, 1), (-3,0)], labels=[r"$\Omega_M$", "w"])
        plt.savefig("corner.png")
        plt.close()
        

        check = input("continue? ")  # qt if using sim data, or different mu/z

    print("I just wanted to help you, mother.")


if __name__ == "__main__": main()
