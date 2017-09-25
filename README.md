This python code is used to evaluate coherence of topics from a topic model.
This code first runs an API server using a pre-train word embedding model (*app.py*).
Then use *cm.py* to evaluate the coherence metrics, average coherence or C@N (see Fang et al. 2016)


### 1. Run an api server###
------------------------------------------------------------------------

`python app.py words.txt vectors.txt [port]`

*app.py* takes 3 arguements:  
*words.txt* is the vocabulary, corresponding to their word embedding *vectors.txt*.  
*[port]* will be te port of this api server.

### 2. calculate the coherence ###
------------------------------------------------------------------------
In a topic model, *K* topics are represented by the top 10 woprds, e.g. *topics_exmaple.txt*.   
To evalute a single topic model:  
`python cm.py -f topic_exmaple.txt`  
To evaluate several topic models using the same configuration (e.g. K), put all topics file in a folder *[topics_folders]* and use the command:  
`python cm.py -f *[topics_folders]* -models`  


### References ###
------------------------------------------------------------------------
1. Using Word Embedding to Evaluate the Coherence of Topics from Twitter Data, Anjie Fang, Craig Macdonald, Iadh Ounis and Philip Habel. In Proc of SIGIR, 2016. [pdf](https://anjiefang.github.io/papers/fang_sigir_2016_we.pdf)
2. Examining the Coherence of the Top Ranked Tweet Topics, Anjie Fang, Craig Macdonald, Iadh Ounis and Philip Habel. In Procs of SIGIR, 2016. [pdf](https://anjiefang.github.io/papers/fang_sigir_2016_examine.pdf)
