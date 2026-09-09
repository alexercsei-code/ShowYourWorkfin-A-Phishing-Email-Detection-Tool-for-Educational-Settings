# Show Your Workfin 🐟
### A phishing email detection tool for educational settings

MSc Data Science – Masters Project (UFCF9Y-60-M)
School of Computing and Creative Technologies, UWE Bristol
Author: Estera-Alexandra Ercsei · September 2026

https://33t7wppx5bfucdmdz9uhmz.streamlit.app/

## What it is

Schools and colleges are frequent phishing targets but rarely have specialist cyber-security staff. Show Your Workfin is a lightweight, explainable phishing checker for non-technical school staff: paste the text of a suspicious email and get an estimated phishing-risk percentage plus a plain-language list of the warning signs it found (urgent language, requests for passwords or payment, links, and so on). Optionally, pasting the full message source also reports the sender's SPF/DKIM/DMARC authentication results.

It is decision support, not a filter. It sits alongside a school's existing email security and reporting process, and it stores nothing that is pasted into it.

## Objectives

1. Develop a machine-learning phishing email classifier using features identified in the literature.
2. Build a functional tool that analyses and explains suspicious emails for an educational audience.
3. Evaluate the classifier with recall, precision, F1, AUC and calibration, using leave-one-source-out validation to measure generalisation to unseen sources.
4. Design and deploy a browser interface for non-technical staff, built around documented user needs.

## Approach

- **Data.** Three public Kaggle corpora (see `data/README.md`). The combined training set holds ~87,000 emails from seven sources. The raw datasets are not stored in this repository; notebook 01 regenerates them.
- **Cleaning.** HTML and header removal, placeholder tokens for links, addresses and numbers, a 5,000-character cap, de-duplication, and removal of dataset-identifying "give-away" words. A source-attribution probe showed the corpora remain distinguishable by topic and style after cleaning (87.8% vs 12.5% chance), so evaluation design, not scrubbing, is the main safeguard against leakage.
- **The EduPhish finding.** The one public "education-targeted" dataset turned out to be a keyword-filtered subset of the same corpora used for training, with ≥27% near-duplicates of training emails and little genuine education content. It was dropped as a test set. The investigation is in notebook 03.
- **Features.** TF-IDF (1–2 grams) plus 13 structural features (link count, urgency/credential/money terms, capitalisation, punctuation) grounded in NCSC phishing guidance. The structural features also drive the app's explanations.
- **Models.** Logistic Regression, Random Forest and linear SVM compared under 5-fold cross-validation; linear SVM with TF-IDF + structural features selected and isotonically calibrated.
- **Evaluation.** 5-fold CV (upper bound, F1 0.99) versus leave-one-source-out (F1 0.85, AUC 0.97), an 80-email synthetic AI-written education test set (F1 0.76), and a 15-email illustrative demonstration on real university phishing and simulated school emails. Warning thresholds (30% / 70%) were chosen from cross-source predictions.

## Repository layout

```
app/            Streamlit app (app.py) and the trained model (app/model/)
notebooks/      Colab notebooks in pipeline order: download → explore → clean → train → evaluate
data/           Sources and licences (README); the two small test files created for this project
results/        Figures and metric tables used in the dissertation
docs/           Licence notices and others
```

## Running the app

```
pip install -r requirements.txt
cd app
streamlit run app.py
```

Requires Python 3.11+ and scikit-learn 1.6.1 (the version the model was saved with).

## Reproducing the model

1. Open `notebooks/01_data_download.ipynb` in Google Colab.
2. Add your Kaggle username and API key to Colab Secrets as `KAGGLE_USERNAME` and `KAGGLE_KEY`.
3. Run the notebooks in order. Notebook 04 writes `features.py` and `phishing_model.joblib`, which the app uses.

## Ethics

All training data comes from publicly available, research-licensed datasets; no personal data was collected. The app analyses pasted text in memory and does not store it. The demonstration set uses phishing examples published by UWE Bristol, the University of Bristol and the University of Birmingham for awareness purposes, already redacted by those institutions, plus simulated school emails written for this project. Usability testing follows UWE ethical approval with informed consent and anonymised feedback.

## Citing the data

This project uses three public datasets, listed with their licences in `data/README.md`. If you use this pipeline, please cite them as their publishers request. The primary corpus asks for:

Al-Subaiey, A., Al-Thani, M., Alam, N.A., Antora, K.F., Khandakar, A. and Zaman, S.A.U. (2024). Novel interpretable and robust web-based AI platform for phishing email detection. [online] arXiv.org. Available at: https://arxiv.org/abs/2405.11619 [Accessed 9 Sept. 2026].
