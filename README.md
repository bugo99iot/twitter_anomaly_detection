# twitter_anomaly_detection
This codes retrieves average number of retweets for all tweets of a given Twitter actor in the last n minutes.
The average retweets is plotted in real time against the convolutional (moving) average over the last m steps and statistical 
anomalies are detected (e.g. a sharp increase/decrease in the tweets).

# The plot
Demonstratively, we applied the algorithm to the [Reuters] twitter page on a short 3-hours time window. No anomaly was detected (no "big news" was issued in the window). Results are in the plot.


# License
Released under version 2.0 of the [Apache License].

[Apache license]: http://www.apache.org/licenses/LICENSE-2.0
[Reuters]: https://twitter.com/reuters
