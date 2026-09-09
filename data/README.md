# Data

The raw and cleaned datasets are **not stored in this repository**: they are large (GitHub rejects files over 100 MB) and the source datasets are redistributed under their own licences. Running the notebooks in order regenerates every file listed below. Only the two small files created for this project are kept here.

## Sources

| # | Dataset | Kaggle ID | Licence / citation |
|---|---|---|---|
| 1 | Phishing Email Dataset | `naserabdullahalam/phishing-email-dataset` | CC BY-SA 4.0. The dataset page asks that this article be cited: (Al-Subaiey et al., 2024), arXiv:2405.11619 |
| 2 | EduPhish | `tanvirahmed0981/education-targeted-phishing-email-dataset` | LGPL-3.0 derivative compilation; notice in `docs/EduPhish_LICENSE_NOTICE.txt` |
| 3 | Phishing and Legitimate Emails | `kuladeep19/phishing-and-legitimate-emails-dataset` | See dataset page |

# Dataset inventory

Every data file the pipeline reads or produces, and which notebook makes it.

Sizes and row counts are from the run of 2 September 2026.

## Produced by `01_data_download.ipynb` (Drive `Data/`, not in repo)

| File | Rows | Size | Description |
|---|---|---|---|
| `phishing_combined.csv` | 105,353 | 190 MB | All three sources stacked, exact duplicates removed. Columns: `text`, `label`, `source` |
| `phishing_general.csv` | ~88,700 | 145 MB | Combined minus EduPhish. The training pool |
| `phishing_education.csv` | 16,679 | 58 MB | EduPhish only |
| `EduPhish_LICENSE_NOTICE.txt` | – | 1 KB | Copied alongside the data; also in `docs/` |

## Produced by `03_data_clean.ipynb` (Drive `Data/`, not in repo)

All add a `text_clean` column (structural cleaning, 5,000-character cap, give-away words removed) and are de-duplicated on it.

| File | Rows | Size | Description |
|---|---|---|---|
| `phishing_combined_clean.csv` | 99,279 | 289 MB | Everything, cleaned |
| `phishing_general_clean.csv` | 86,809 | 224 MB | **Training data** used by notebooks 04 and 05 |
| `phishing_education_clean.csv` | 16,679 | 92 MB | EduPhish, cleaned |
| `phishing_education_decontaminated_clean.csv` | 12,165 | 63 MB | EduPhish minus 4,514 near-copies of training emails. Reference only |
| `phishing_education_strict_clean.csv` | 3,201 | 22 MB | Decontaminated and mentions an education term. Reference only |

## Created for this project (`data/`, **in repo**)

| File | Rows | Description |
|---|---|---|
| `demo_dataset.csv` | 15 | 7 real university phishing emails (UWE, Bristol, Birmingham awareness pages) and 8 simulated secondary-school emails (5 phishing, 3 legitimate). Illustrative demonstration, not an evaluation set |
| `synthetic_education_emails.csv` | 80 | 40 phishing and 40 legitimate emails, LLM-written, UK school and university settings, all organisations fictional. Indicative test of fluent modern phishing |

## Produced by notebooks 02–05 (`results/`, **in repo**)

Notebooks: `02_data_explore.ipynb`, `03_data_clean.ipynb`, `04_training_models.ipynb`, `05_models_evaluate.ipynb`.

| File | Made by | Description |
|---|---|---|
| `table_label_by_source.csv` | 02 | Phishing/legitimate counts per source |
| `fig_email_lengths.png` | 02 | Histogram of email lengths |
| `table_giveaway_candidates.csv` | 03 | Words concentrated in one source (candidates for removal) |
| `table_removed_giveaway_words.csv` | 03 | Words actually removed, with reasoning in the notebook |
| `table_cv_results.csv` | 04 | 5-fold cross-validation, 3 models × 2 feature sets |
| `fig_cv_feature_sets.png`, `fig_cv_models.png`, `fig_structural_features.png` | 04 | Cross-validation and feature charts |
| `table_leave_one_source_out.csv`, `table_loso_summary.csv`, `fig_leave_one_source_out.png` | 05 | Leave-one-source-out results, both feature sets |
| `fig_calibration.png`, `table_thresholds.csv`, `fig_confusion_matrix.png` | 05 | Calibration and thresholds on a random 20% split (upper bound) |
| `table_thresholds_cross_source.csv`, `loso_pooled_prob.npy`, `loso_pooled_y.npy` | 05 | Thresholds on pooled cross-source predictions; basis for the app's 30% / 70% bands |
| `table_held_out_tests.csv` | 05 | Synthetic education set and EduPhish (reference) scores |
| `table_demo_examples_scored.csv` | 05 | The 15 demonstration emails with model scores |
| `table_feature_weights.csv` | 05 | SVM coefficient for every TF-IDF and structural feature |

## Produced by `04_training_models.ipynb` (`app/model/`, **in repo**)

| File | Description |
|---|---|
| `features.py` | Text cleaning and structural features; imported by notebooks 04–05 and the app |
| `phishing_model.joblib` | Calibrated linear SVM on TF-IDF + structural features (7 MB) |
| `model_info.txt` | Recipe and cross-validation scores of the saved model |

## How to regenerate everything

1. `01_data_download.ipynb` with Kaggle credentials in Colab Secrets → raw and combined files (about 5 minutes).
2. `02_data_explore.ipynb` → exploration tables and the length histogram (about 5 minutes).
3. `03_data_clean.ipynb` → cleaned files and the EduPhish investigation (about 10 minutes).
4. `04_training_models.ipynb` → model and `features.py` (about 90 minutes; Random Forest is the slow part).
5. `05_models_evaluate.ipynb` → evaluation tables and figures (about 90 minutes including the cross-source threshold cell).
