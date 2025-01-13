# Image Text Generator and Data Cleaning Process

This project automates the process of cleaning a dataset, validating records, and generating images with dynamic text overlays based on cleaned data. Below, I document the process, hurdles encountered, and how I resolved them.

## Overview

The goal was to create a pipeline that:

- Reads an Excel file containing records.
- Cleans the dataset, ensuring all column headers are standardized and missing data is handled.
- Generates images for valid rows using specified columns for text overlays.

### Key Features:

#### Data Cleaning:
- Standardizes column headers.
- Removes rows with completely missing data.
- Skips rows with incomplete or invalid values during image generation.

#### Image Generation:
- Dynamically overlays text from specific columns onto images.
- Text is styled and positioned based on hierarchy:
  - **New Text Column:** Centered, bold, and largest.
  - **Custom Text Column:** Big and positioned just below the new text.
  - **Award Title Column:** Smaller and positioned below the custom text.

## Process and Hurdles

### 1. Data Cleaning
Initially, the dataset had issues with inconsistent headers, such as "Unnamed" columns caused by improperly structured Excel sheets. The solution involved:

- Stripping whitespace from column headers.
- Replacing unnamed columns with generic names like `Column_1`, `Column_2`, etc.
- Dropping rows where all values were missing.

**Hurdle:**
During this stage, the code kept throwing the ambiguous error: `The truth value of a Series is ambiguous.` This happened because I was unintentionally trying to apply conditions to entire DataFrame columns instead of individual cells. To resolve this, I used `df.at[i, col]` to work with individual cell values.

### 2. Image Generation
The text overlay on images posed several challenges:

- Aligning multiple text elements dynamically based on their sizes.
- Ensuring the hierarchy of text was visually appealing.

**Hurdle:**
At first, the images were empty or contained the word "MISSING" due to rows with incomplete data. The fix was straightforward:

- I added a condition to skip rows where required columns had missing values or invalid content.

**Additional Improvement:**
I later expanded the functionality to include three tiers of text, each styled and positioned differently:
- A new column added to the dataset for bold, centered text.
- The custom text was displayed larger but secondary.
- The award title was styled smaller and displayed below all.

## How It Works

### 1. Loading and Cleaning Data
The `load_and_clean_data` function:
- Reads the Excel file into a pandas DataFrame.
- Cleans the column headers and ensures no empty rows remain.
- Logs the process at every step.

### 2. Generating Images
The `create_images_with_text` function:
- Dynamically overlays text onto images using columns from the cleaned dataset.
- Skips rows with missing or invalid values.
- Saves the generated images in the specified output directory.
