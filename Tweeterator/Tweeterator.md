
# Tweeterator (WIP)

An excellent Andrej Karpathy's blog post: http://karpathy.github.io/2015/05/21/rnn-effectiveness/ led to posing the following question:

Can we train a simple 'off-the-shelf' neural network to talk like a specific person?

The main idea is:
- get a lot of tweets from the given person and the people they retweet most often
- train the model (char-LSTM RNN) on those tweets
- generate new tweets using the model

Main takeaway points, before we go further: 
- generated text looks like a valid tweet only if someone doesn't speak the language (more samples, tweaking parameters might help here)
- 'looks like' doesn't mean that the generated text makes any sense - it doesn't (word-LSTM might help, but needs to be run on a bigger machine)
- part of fun - as in the original blog - was seeing how the model improves from just throwing a lump of random letters in first iterations to improving later on

# Training Trump vs Clinton model with a simple char based RNN

## Trump Model

So, let's create a TRUMP model: with 


	TRUMP = ["realDonaldTrump", "TeamTrump"]
	...
    download_with_retweeters(TRUMP, latest=True)


You will see that it will download all the available @realDonaldTrump and @TeamTrump tweets, but also accounts that were retweeted most often: @TeamTrump, @EricTrump, @DanScavino, @mike_pence.


We're ready to train the model now:

	train(maxlens=[40], steps=[2], dropouts=[0.1], dataset=filter(lambda x: x[0]=='trump', datasets.iteritems()))

Depending on the parameters used it might take quite some time. 
For the above arguments: 3hrs on a recent macbook pro, ie 6 iterations with 30mins per iteration).

You will see something like: 

	=========== TRAINING on: maxlen=40, step=2, lstm_size=128, dropout=0.1, text=../../data/trainset-trumpstradamus.pkl.gz



Now the fun part begins - seeing what the have to say.


## Clinton Model

Doing the above training steps on CLINTON = ["HillaryClinton", "TheBriefing2016"] will give us the clinton model to use.

# Generating Trump-like speech, Clinton-like speech

And now the fun part - the generated bits:

## Trump:
- model=11,trump,tweets-40-2-128-0.1_5_1.57.hdf5, div=0.4

> rt @danscavino: ready at incestling can't the state to support and the #trumptrain https://t.co/wliequloxjain
> thank you here: https://t.co/tatas2gnpmbheljoininbinfif: he is the crooked hillary clinton https://t.co/jarssavufh
> .@realdonaldtrump #trumptrain #maga #trump2016 #trump2016 https://t.co/bpfarn2vorh
> rt @govpencein: thank you
> thank you to the commansion to see our a https://t.co/33gvhlvycm
> rt @danscavino: head beat https://t.co/jbeckolukbp
> rt @jasonmillerindc: .@realdonaldtrump will americans to see you state for the movement and and our commitmer the in our corruption to republican for @trumptr
> rt @govpencein: thank you to the election of #trumptrain https://t.co/umocqv1cbqh
> rt @govpencein: thank you @trumptraining to the bead was @hillaryclinton as the country the country #trumptrain https://t.co/wpjochagfbbs
> rt @danscavino: thank you to the donald j. trump to this jobs for the with for the corruption watching in the #americagreatagain https://t.co/qtaogwykqsj

## Clinton:


# Tools used

## Keras

As the AI engine giving a nice abstraction over the inner workings of the NN modeling and execution.

## Tweepy

For tweeter REST API access python abstraction.

## numpy, pandas

For data heavy lifting.

## Sqlite

Used for a twitter 'cache' - so as to just download tweets once. But also as a query engine to browse / join the feeds as we please

