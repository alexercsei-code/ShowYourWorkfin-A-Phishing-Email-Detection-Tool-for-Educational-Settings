# A-Phishing-Email-Detection-Tool-for-Educational-Settings
An explainable machine-learning tool that estimates the phishing risk of an email and explains the signals behind the result, designed for non-technical staff in schools and colleges. MSc Data Science Masters Project, UWE Bristol, 2026.

# A Phishing Email Detection Tool for Educational Settings

MSc Data Science – Masters Project (UFCF9Y-60-M)
School of Computing and Creative Technologies, UWE Bristol
Author: Estera-Alexandra Ercsei · Supervisor: Alireza Bolhari · September 2026

## What this project is

Schools and colleges are frequent phishing targets but rarely have specialist cyber-security staff, and repeated awareness training shows limited lasting effect. This project builds and evaluates a lightweight, explainable phishing email classifier aimed at non-technical school staff. A user pastes the body text of a suspicious email and receives an estimated phishing-risk percentage together with a plain-language explanation of the signals behind it (for example urgent language, credential or payment requests, or mismatched links).

The tool is decision support, not a guarantee. It complements existing email filtering, reporting processes and staff judgement rather than replacing them.

## Objectives

1. Develop a machine-learning phishing email classifier using features identified in the literature.
2. Build a functional tool that analyses and flags suspicious emails in an educational context.
3. Evaluate model performance using recall, precision, F1-score, AUC and calibration, including cross-source generalisation to education-targeted emails.
4. Design a simple interface for non-technical staff and assess its suitability through structured usability testing.

## Approach

- **Data:** three public Kaggle datasets combined into one corpus, with a separate education-only set held out for cross-source testing. See `data/README.md` for sources and licences. No data is stored in this repository.
- **Cleaning:** structural cleaning, de-duplication, and removal of source-identifying artefacts to reduce data leakage.
- **Features:** TF-IDF text representation plus structural features such as URL count, urgency terms and capitalisation.
- **Models:** Logistic Regression (baseline), Random Forest and SVM, compared with k-fold cross-validation and probability calibration for the percentage output.
- **Explainability:** model outputs are mapped to recognisable phishing indicators so the explanation is meaningful to a non-specialist.

Classical models and TF-IDF were chosen over transformer models for interpretability, low compute requirements and reproducibility, which suit a school deployment context.

## Repository layout

```
notebooks/   Colab notebooks, numbered in pipeline order (download → explore → preprocess → train → evaluate)
data/        Not stored here. README explains where the data comes from and how to regenerate it.
results/     Figures and metric tables produced during evaluation
docs/        Licence notices, ethics notes and other supporting material
```

## How to reproduce

1. Open `notebooks/01_download_data.ipynb` in Google Colab.
2. Add your Kaggle username and API key to Colab Secrets as `KAGGLE_USERNAME` and `KAGGLE_KEY`.
3. Run the notebook top to bottom. It downloads the three datasets, cleans them, and saves `phishing_combined.csv` and `phishing_education.csv` to your Google Drive.
4. Run the remaining notebooks in numerical order.

Libraries used are listed in `requirements.txt`.

## Ethics

All data comes from publicly available, research-licensed datasets; no personal data was collected by the author. The prototype does not permanently store any email text submitted for analysis. Usability testing follows UWE ethical approval, with informed consent and anonymised feedback. Details are in the dissertation, Chapter 5.
