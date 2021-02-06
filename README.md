# High Throughput Screening Quality Control
The robustness of high-throughput screening (HTS) data is paramount to the identification of high-quality small-molecule candidates for further, more comprehensive investigation. Quality control (QC) is a critical aspect of screening which permits the identification of systematic errors and random artifacts, directly influencing the quality of putative hits.

This script is designed to analyse an absorbance-based screening dataset and output several quality metrics and visualisations which can be used to identify the robustness of the screen and any potential issues.

The example dataset provided is a resazurin-based screen of a Nalm6 B-cell Acute Lymphoblastic Leukaemia (ALL) cell line performed in 384-well format with an FDA-approved compound library of 1971 compounds. The plate data was acquired with a plate reader, and raw results were exported in list format to comma-separated value (CSV) files.

## Analyses
This script will allow visualisation and calculation of key HTS quality control metrics including:
* Experiment-wide raw absorbances
* Experiment-wide column effects
* Experiment-wide row effects
* Control well variability
* Per-plate descriptive statistics (mean, standard deviation, median, median absolute deviation) for compounds, positive controls, and negative controls.
* Per-plate regression model of positive and negative controls
* Per-plate signal-to-background ratio
* Per-plate Z' factor
* Per-plate robust Z' factor
* Heatmaps of each plate for visualisation

Statistical metrics are exported as graphical figures and as a dataframe.

## Getting Started
* ```Requirements``` This contains the required dependencies used throughout the script.
* [QC_analysis.ipynb](QC_analysis.ipynb) Is the easiest way to start. It shows an example of processing a screening dataset derived from an FDA-approved compound library using resazurin fluorescence as the end output.
* [HTS_analysis.py](HTS_analysis.py) Is the script to analyse the data.
* ```Raw Data``` Should contain any raw data files for analysis as list format and saved as a Comma-Separated Values (CSV) file. One datafile corresponds to one plate.
* [control_locations.csv](control_locations.csv) Should contain information about the position of positive and negative controls located on every plate loaded (POS or NEG). For example:
<table>
  <tr><td>Well Row</td><td>Well Col</td><td>COMP_TYPE</td></tr>
  <tr><td>A</td><td>23</td><td>NEG</td></tr>
  <tr><td>A</td><td>24</td><td>NEG</td></tr>
  <tr><td>C</td><td>23</td><td>POS</td></tr>
  <tr><td>C</td><td>24</td><td>POS</td></tr>
  </table>
