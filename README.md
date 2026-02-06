# cs4412-Plotting_Plots-Success

The Adobe Creative Jam for North America focuses on project creation utilizing Adobe’s Premiere Rush. The final product for submission in the contest is a short film utilizing Rush, to be submitted and judged by Adobe. The target of this proposal is to collect successful film projects, compare these projects, and discover patterns that help propel projects to success, then using these patterns determine a strategy and structured plan for the project’s submission. Specifically searching for what successful films contain, that less successful films do not, or at least contain less of, essentially the disjunction of the set of success and the set of non-successful. The final output, or result for this pattern searching should be the attributes and aspects of cinema that affect the outcome the most significantly. In this way, we should be able to create a rough ‘script’/outline for the contest, or a very abstracted prediction of what the most potentially successful project we could build.

The project requires two data sets, one from Kaggle, and another custom scraped set from source material in ImDb. The Kaggle set contains budgets, years of release, titles, cast, director, box office revenue, and audience scores. While the custom ImDb set contains roughly 1000 frames per film, enough to determine patterns in the visual style of each film, as well as synopsis' for each individual project, which will be used to find similiarity between successful narratives and plots.

The architecture relies on the aft-fore mentioned sets, where the main script will initialize the agent to begin scraping for data, that data is then combined, the plots and frames, the frames are processed into visual histogram vectors, and summations are embedded using NLP techniques.
(Frames):
- Color grading: HSV / Lab color histograms
- Brightness: average luminance statistics
- Contrast: intensity distribution metrics
- Framing: rule-of-thirds saliency measures
(Plots):
- Film synopses embedded using sentence-level NLP models
- Similarity measured using cosine distance

(Proposed Strategm and algorithms):
- Normalization
- Euclidean / Mahalanobis for visual features
- Cosine similarity
- Dimensionality reduction
-Apriori on discretized attributes

(Running the Script):
Download and install Python 3.1, as well as the PlayWright library, BeautifulSoup dependicy, json library, os library, sys library.
Set the playwright object variable to 'headless,'
Run the script
