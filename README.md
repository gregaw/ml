# ML for Machine Learning playground

Exploring the machine learning models and data in general.

Have a look at the attached `jupyter python` notebooks.

Here are some installation instructions for jupyter if you need them: http://jupyter.readthedocs.org/en/latest/install.html 

## Anomaly detection with GMM

### Motivation

Imagine we are running a financial platform where investors can trade things.

Most of the transactions are fine, but some are strange like trying to sell something for close to nothing; or sudden spike in activity frequency to machine level 10 transactions per second for instance; or client's IP address trading from Lagos one minute and from Buenos Aires the next.

We want to be notified of such strange transactions. We could obviously come up with a set of rules and grow them as we go, but we will try and use machine learning for this.

## Tweeterator - Generating tweet posts with neural networks in Keras

### Motivation

Would RNN-char networks be strong enough to generate completely made up, but plausible looking tweets?

An excellent Andrej Karpathy's blog post: http://karpathy.github.io/2015/05/21/rnn-effectiveness/ led to posing the following question:

Can we train a simple 'off-the-shelf' neural network to talk like a specific person?

The main idea is:
- get a lot of tweets from the given person and the people they retweet most often
- train the model (char-LSTM RNN) on those tweets
- generate new tweets using the model

Read more in the Tweeterator folder.
- [Introduction and Trump vs Clinton](Tweeterator/Tweeterator.md)
- [Gov vs Opposition (in Polish)](Tweeterator/pl.md)
- and yes, Tweeterator speaks italian too: [Italian Tweets (La Repubblica, etc)](Tweeterator/it.md)

### Update: improvements with significant terms analysis 

What if we took the most significant terms for each text set and used tweets that contain top N of those words?

Tried it [here](Tweeterator/pl-significant-terms.md)

## Most Significant Adjectives - NLP

What are the most significant adjectives used with the word 'X' as opposed to the word 'Y'?

How about using an elasticsearch-like 'significant terms' concept to answer that question. Check out some results [here](MostSignificant/TheMostSignificantAdjectives.ipynb).

## Open Pollution - Time Series Analysis

Analysing the Krakow historical pollution data to discern trends over time (in cigarettes per day equivalent drops from 8 to 6 over few years sic!) and data-test strategies for minimum pollution intake (see [here](OpenPollution/open_pollution.ipynb)) or to simply interactively play with historical data (eg [here](OpenPollution/pm10-2016-krasinskiego.html)).
