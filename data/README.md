# Data Directory

This directory contains all data files for the project.

## Structure

- **raw/** - Original, immutable data dump. Never edit these files.
- **processed/** - Cleaned, transformed data ready for analysis.
- **external/** - Data from third-party sources.

## Guidelines

- Keep raw data immutable
- Document data sources and transformation steps
- Use version control for small datasets or scripts that generate data
- For large datasets, use data versioning tools like DVC
- Add data file extensions to .gitignore if files are large
