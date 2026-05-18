"""This module provides the NN and functions to run NRE."""
import pytorch_lightning as pl
import torch
import torch.nn as nn
import numpy as np
rng = np.random.default_rng(42)



def build_mlp(input_dim, hidden_dim, output_dim, layers,dropout=0.45, activation=nn.GELU()):
    """Create an MLP from the configuration."""
    seq = [nn.Linear(input_dim, hidden_dim), activation]
    for _ in range(layers):
        seq += [nn.Linear(hidden_dim, hidden_dim), activation, nn.Dropout(p=dropout)]
    seq += [nn.Linear(hidden_dim, output_dim)]
    return nn.Sequential(*seq)


class NeuralRatioEstimator(pl.LightningModule):
    """Simple neural likelihood-to-evidence ratio estimator, using an MLP as a parameterized classifier."""
    def __init__(self, x_dim, theta_dim, hidden_dim=256, layers=4):
        super().__init__()
        self.lc_inp = x_dim // 2
        self.classifier = build_mlp(input_dim=x_dim + theta_dim, hidden_dim=hidden_dim, output_dim=1, layers=layers)

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
    if z is None: xTest = muTest
    else:
        zTest = torch.tensor((z - z_mean) / z_std).float()
        xTest = torch.concatenate([muTest, zTest])
    with torch.no_grad():
        nre.eval()
        return nre.classifier(torch.cat([xTest, thetaTest], dim=-1))


def log_post(theta, mu, z, theta_mean, theta_std, mu_mean, mu_std, z_mean, z_std, nre, sort):
    """
    Log-posterior given theta and data.

    If the data has been f.smoothered the parameter z should be None, otherwise nothing will work.

    Parameters
    ----------
    theta : np.array
        Omega and w.
    mu : np.array
        Distance modulus.
    z : np.array or None
        Redshifts.
    *_mean : np.array
        Parameter mean array from training set.
    *_std : np.array
        Parameter std array from training set.
    nre : NeuralRatioEstimator
        Trained model.
    sort : bool
        Apply sorting to input data.
    """
    lp = log_prior(theta)
    if not np.isfinite(lp): return -np.inf
    if z is None: lk = log_like(theta, mu, z, theta_mean, theta_std, mu_mean, mu_std, z_mean, z_std, nre)  # In case of smoother case
    else:
        new_z = np.empty(nre.lc_inp)
        new_mu = np.empty(nre.lc_inp)
        idxes = np.arange(len(mu))
        lk = 0
        its = len(mu) // nre.lc_inp 
        for i in range(its):
            new_idxes = rng.choice(len(idxes), nre.lc_inp, replace=False, shuffle=False)
            new_mu = mu[new_idxes].copy()
            new_z = z[new_idxes].copy()
            if sort:
                sorting = np.argsort(new_z)
                new_mu = new_mu[sorting]
                new_z = new_z[sorting]
            idxes = np.delete(idxes, new_idxes)
            lk += log_like(theta, new_mu, new_z, theta_mean, theta_std, mu_mean, mu_std, z_mean, z_std, nre)
    return lp + lk