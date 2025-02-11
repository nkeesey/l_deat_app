# Learning Dynamics Exploratory Analysis Tool (L-DEAT) 

A Flask/Dash app using AIND open-source Dynamic Foraging Task data.
The data used in this tool is demonstrated in this paper:
https://www.sciencedirect.com/science/article/pii/S089662731930529X?via%3Dihub

## Current state

This app is still in development, incoming updates will be posted. Current capabilities include:
- Filtering for specific dimensionality reduction methods (PCA, LDA, t-SNE, UMAP)
- Filtering (multi-selectable) subjects
- Filtering for experiment parameters including:
    - Task
    - Stage

## The GUI
<img src="https://github.com/nkeesey/dynamic_forager_app/blob/master/app/assets/README.png" width=500>
 
## To Use:

Create a copy of this repo and run locally, you will need to pull a CSV for the data source
- Up to date CSVs can be found from the AIND streamlit app:
https://foraging-behavior-browser.allenneuraldynamics-test.org/
