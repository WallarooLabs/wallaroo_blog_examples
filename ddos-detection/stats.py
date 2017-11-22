"""
Statistical functions for use in DDoS Detector

http://www.itl.nist.gov/div898/software/dataplot/refman2/ch2/weightsd.pdf
"""


from math import sqrt


def mean(data):
    return sum(data)/float(len(data))


def weighted_mean(data, weights):
    assert(len(data) == len(weights))
    return sum(map(lambda x, w: x*w, data, weights)) / float(sum(weights))


def mu_sigma(data):
    mu = mean(data)
    sigma = sqrt(sum(map(lambda x: (x-mu)**2, data)) / float(len(data)-1))
    return mu, sigma


def weighted_mu_sigma(data, weights):
    wmu = weighted_mean(data, weights)
    N = len(filter(None, weights))
    wsigma = sqrt(sum(map(lambda x, w: w*((x-wmu)**2), data, weights)) /
                  ((N-1)*sum(weights) / N))
    return wmu, wsigma
