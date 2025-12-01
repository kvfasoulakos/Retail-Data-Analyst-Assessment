# Retail-Data-Analyst-Assessment

# Retail Data Analyst - Product Matching System

## Overview
This repository contains a robust Product Matching System designed to link unstructured product descriptions with a structured product catalog. The solution utilizes a **Hybrid Matching Logic** combining TF-IDF (Text Similarity) and Regex Attribute Extraction.

**Author:** Konstantinos Fasoulakos  
**Date:** November 2025

## Repository Structure

* `product_matching_implementation.py`: The main executable script (run this file).
* `Assigment for Retail Data Analyst position.ipynb`: Exploratory analysis and development logic.
* `b_product_catalog.csv`: Source catalog dataset.
* `b_unstructured_descriptions.csv`: Input unstructured dataset.
* `matching_results.csv`: Final output file (generated after running the script).
* `viz1_confidence_distribution.png`: Performance visualization (generated after running the script).
* `Technical_Documentation.md`: Detailed architecture and ROI analysis.

## Setup & Installation

1. **Install Dependencies:**
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt

2. **Run the Matching System: Execute the main script to process the data:**
Run / Execute file python product_matching_implementation.py

3. **Output files**

After running the script, two files are generated:

    a) matching_results.csv: Contains the matched pairs, confidence scores (0-100%), and the Match_Reason (e.g., "Color: Blue | Size: M").

    b) viz1_confidence_distribution.png: A histogram showing the distribution of confidence scores across the dataset.

The logic behind the process is that the model uses a weighted scoring system:

    i) 60% TF-IDF Cosine Similarity: Handles general text overlap.

    ii) 40% Attribute Matching: Rewards exact matches on Brand, Color, Size, Season, and Gender.
