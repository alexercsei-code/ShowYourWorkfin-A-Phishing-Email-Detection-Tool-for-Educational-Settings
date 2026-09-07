# Notebooks

Google Colab notebooks, run in order. Each reads from and writes to the `Data/`, `Model/` and `Results/`
folders in Google Drive (`Colab Notebooks/Master's project/`).

| Notebook | What it does |
|---|---|
| `01_data_download.ipynb` | Downloads the three Kaggle datasets, combines them, saves combined / general / education files |
| `02_data_explore.ipynb` | Label balance per source, email lengths, sample emails, give-away words, source-attribution probe (87.8%) |
| `03_data_clean.ipynb` | Structural cleaning, length cap, give-away word removal, de-duplication; investigation of EduPhish (Cells 11–13) |
| `04_training_models.ipynb` | Writes `features.py`; 5-fold comparison of LR / RF / SVM on two feature sets; fits, calibrates and saves the best |
| `05_models_evaluate.ipynb` | Leave-one-source-out, calibration, thresholds (random and cross-source), held-out tests, feature weights, demonstration |

Kaggle credentials are read from Colab Secrets (`KAGGLE_USERNAME`, `KAGGLE_KEY`) and never appear in the notebooks.
