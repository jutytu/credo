# credo

This analysis was performed during my three-week long internship at the Institute of Nuclear Physics of the Polish Academy of Sciences. Its main goal
was to examine the correlations between secondary cosmic ray detection rates and seismic effects. The idea of the whole project, which the internship was
part of, is to improve a global early warning system against eartquakes. The methodology and further explanation can be found in the article:
[https://arxiv.org/ftp/arxiv/papers/2204/2204.12310.pdf](https://arxiv.org/ftp/arxiv/papers/2204/2204.12310.pdf).

### Data

The original .root files used for this analysis were created using Monte Carlo simulations. They contain records of the Higgs boson decaying into two tau leptons, and 
subsequently the leptons decaying into other charged/neutral products. The data includes information like: four-momenta of the decay products, decay modes of the tau leptons,
generated event weights for different CP scenarios (CP-even - 0&deg;, CP-odd - 90&deg; and combinations of those two for other angle values). The original data is only available for CERN users. The theory of this decay channel can be found in the article: [https://arxiv.org/pdf/2212.05833](https://arxiv.org/pdf/2212.05833).

### Files

| File                                          | Description                                                                                                                           |
|-----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| prepare.py <br> preselection.py <br> mc_to_csv.py       | Files meant for data preparation from .root files into data frames or .csv files as well as filtering the data.                        |
| plots.py <br> distr.py                             | Various plots illustrating the data inside the files.                                                                                 |
| boost_rotation.py                             | Relativistic boost of the four-momenta of the leptons into the CoM frame + rotation so that the momenta are along the z-axis.                                                           |
| boost_rotation_categories.py <br> nn_categories.py | Non-relativistic boost of the four-momenta into the CoM frame and a neural network learning to predict most probable CP angle for a given event.                                 |
| C123.py                                       | Calculating coefficients describing the relation between the weight and the CP angle using systems of linear equations for each event. |

### References

This analysis was based on a similar, more expanded analysis from the article: [https://arxiv.org/pdf/2001.00455](https://arxiv.org/pdf/2001.00455).
