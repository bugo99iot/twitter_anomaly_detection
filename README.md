# twitter_anomaly_detection
This codes retrieves average number of retweets for all tweets of a target Twitter actor in the last n minutes.
The average number of retweets is plotted in real time against the convolutional (moving) average over the last m measurements and statistical anomalies are detected (e.g. a sharp increase/decrease in retweets).
Positive anomailes are emailed to a target user with the headline: "BIG NEWS!".

# Test run
Demonstratively, we applied the algorithm to [Reuters]' twitter page on a short 3-hours time window. At 2 sigma level, no anomaly was detected (no "big news" was issued in the window). Results may be visualised in the png file attached.
UPDATE: on a 12 hours test run performed on the 6th of October 2017, the algorithm was able to detect anomalies related to the 6.3 magnitude earthquake recorded off eastern Japan and the anti-nuclear campaign 2017 Peace Nobel Peace.

# License
Released under version 2.0 of the [Apache License].

[Apache license]: http://www.apache.org/licenses/LICENSE-2.0
[Reuters]: https://twitter.com/reuters
