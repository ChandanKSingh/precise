import numpy as np
import pandas as pd
from pprint import pprint
from precise.skatertools.m6.covarianceforecasting import m6_cov
from precise.skaters.covarianceutil.covfunctions import affine_shrink, nearest_pos_def
from precise.skaters.portfolioutil.allstaticport import PRC_PORT, random_port
from precise.skaters.covariance.allcovskaters import ALL_D0_SKATERS, random_cov_skater, cov_skater_manifest
import random

# Demonstrates the creation of an entry in the M6 contest
#   1. Pick a cov estimator (i.e. a "cov skater")
#   2. Pick a portfolio generator
#   3. Pick extra shrinkage params if you wish


def m6_competition_entry(interval='d', f=None, port=None, n_dim=100, n_samples=5000, n_obs=200, extra_shrink=True, phi=1.1, lmbd=0.03, verbose=True):
    """
           Example of generating an M6 Entry
           pip install PyPortfolioOpt

           interval - sampling interval to use for cov estimation
           n_obs    - number of time points to use in cov estimation (max 60 if interval='m')
           n_dim    - Set at 100 for actual contest, but lower to test
           port     - A portfolio creator (see /portfolioutil )
           f        - A cov skater
           extra_shrink - If True, will perform additional shrinkage over and above the skater or portfolio method using
               phi      - (Additional) Ridge parameter, suggest (1,1.5)
               lmbd     - (Additional) Shrinkage parameter, suggest (0,0.5)

    """
    if port is None:
        if verbose:
            print('Choosing a cov estimator from the following list ')
            pprint([p.__name__ for p in PRC_PORT])
        port = random_port()

    if f is None:
        print('Choosing a cov estimator from the following list ')
        pprint(cov_skater_manifest())
        f = random_cov_skater()

    df_prob, df_cov = m6_probabilities(f=f, interval=interval, n_dim=n_dim, n_samples=n_samples, n_obs=n_obs)
    cov = df_cov.values
    if extra_shrink:
        cov = affine_shrink(cov, phi=phi, lmbd=lmbd)
        cov = nearest_pos_def(cov)
    w = port(cov=cov)
    w_rounded = [round(wi, 5) for wi in w]
    entry = df_prob.copy()
    entry['Decision'] = w_rounded
    entry.rename(inplace=True, columns={'0': 'Rank1', '1': 'Rank2', '2': 'Rank3', '3': 'Rank4', '4': 'Rank5'})
    return entry


def what_pctl_number_of(x, a, pctls=[20,40,60,80]):
    return np.argmax(np.sign(np.append(np.percentile(x, pctls), np.inf) - a))


def mvn_quintile_probabilities(sgma, n_samples):
    n_dim = np.shape(sgma)[0]
    mu = np.zeros(n_dim)
    x =  np.random.multivariate_normal(mu, sgma, size=n_samples, check_valid='warn', tol=1e-8)
    y = scores_to_quintiles(x)
    p = list()
    for i in range(5):
        pi = np.mean(y==i,axis=0)
        p.append(pi)
    return p


def scores_to_quintiles(x):
    ys = list()
    for xi in x:
        q = np.quantile(x,[0.2,0.4,0.6,0.8])
        y = np.searchsorted(q, xi)
        ys.append(y)
    return np.array(ys)


def m6_probabilities(f, interval='d',n_dim=100, n_samples=5000, n_obs=200):
    covdf = m6_cov(f=f, interval=interval, n_dim=n_dim, n_obs=n_obs)
    tickers = list(covdf.columns)
    sgma = covdf.values
    p = mvn_quintile_probabilities(sgma=sgma, n_samples=n_samples)
    df = pd.DataFrame(columns=tickers, data=p).transpose()
    df_cov = pd.DataFrame(columns=tickers, index=tickers, data=sgma)
    return df, df_cov


if __name__=='__main__':
    df = m6_competition_entry(n_dim=5)




