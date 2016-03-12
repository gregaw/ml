# ML for Machine Learning

Exploring the machine learning models.

Have a look at the attached `jupyter python` notebooks.

Here are some installation instructions for jupyter if you need them: http://jupyter.readthedocs.org/en/latest/install.html 

## Anomaly detection with GMM

### Motivation

Imagine we are running a financial platform where investors can trade things.

Most of the transactions are fine, but some are strange like trying to sell something for close to nothing; or sudden spike in activity frequency to machine level 10 transactions per second for instance; or client's IP address trading from Lagos one minute and from Buenos Aires the next.

We want to be notified of such strange transactions. We could obviously come up with a set of rules and grow them as we go, but we will try and use machine learning for this.
