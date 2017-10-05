# twitter_anomaly_detection
This codes retrieves average number of retweets for all tweets tweeted by a given Twitter actor in the last n minutes.
The average retweets is plotted in real time against the convolutional (moving) average over the last m measurements and statistical anomalies are detected (e.g. a sharp increase/decrease in retweets).

# Test run
Demonstratively, we applied the algorithm to the [Reuters] twitter page on a short 3-hours time window. No anomaly was detected (no "big news" was issued in the window). Results may be visualised in the png file attached.

# License
Released under version 2.0 of the [Apache License].

[Apache license]: http://www.apache.org/licenses/LICENSE-2.0
[Reuters]: https://twitter.com/reuters
