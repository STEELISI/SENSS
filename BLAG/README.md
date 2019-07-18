<h2> BLAG </h2>

Blacklists contain identities of known offenders and can be used to preventively filter unwanted traffic. Yet, any single blacklist may only be effective for a given type of attack and only over certain portions of address space. Further, each blacklist is compiled and updated using proprietary methods, and thus may have stale information or it may be slow to include new offenders, leading to false positives or false negatives. Finally, blacklists contain addresses of offenders, which lowers their accuracy in networks where there is dynamic addressing. BLAG is a sophisticated approach to select and aggregate only the accurate pieces of information from multiple blacklists. BLAG calculates information about accuracy of each blacklist over regions of address space, and uses recommender systems to select most reputable and accurate pieces of information to aggregate into its master blacklist.

![Output sample](https://github.com/STEELISI/SENSS/raw/master/doc/blag_main.png)

<h2> Download blacklists </h2>

``` python download.py```

The script will prompt for location to store the blacklists. 

<h2> Running recommendation system </h2>

``` python run_recommender.py ```

<h2> Poster </h2>

#### Blacklists Assemble - Aggregating Blacklists for Accuracy   
*Sivaramakrishnan Ramanathan, Jelena Mirkovic and Minlan Yu *    
The Network and Distributed System Security Symposium (NDSS 2019)  
[Poster](https://www.ndss-symposium.org/wp-content/uploads/2019/02/ndss2019posters_paper_34.pdf) 
