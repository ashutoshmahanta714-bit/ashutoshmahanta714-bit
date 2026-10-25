# StockSense — Inventory Risk Classification

A deployable Streamlit adaptation of Ashutosh Mahanta's existing Google Colab inventory-management project.

## Run locally

Use Python 3.12. From this directory:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

From the repository root, use `python -m streamlit run projects/inventory-management/app.py`.

## Deploy on Streamlit Community Cloud

1. Open https://share.streamlit.io and sign in with GitHub.
2. Create an app from repository `ashutoshmahanta714-bit/ashutoshmahanta714-bit`.
3. Select branch `main`.
4. Set entrypoint to `projects/inventory-management/app.py`.
5. Under Advanced settings, select Python 3.12, then deploy.

Dependencies are declared beside the entrypoint. No secrets or external APIs are required. Training is small and cached per server process; the first visit may take a few seconds. Cloud deployment has not been performed or verified by this repository upload.

## Features

- Dataset overview and season filter.
- Single-product classification with an explicit stock-rule comparison.
- CSV/XLSX batch uploads, validated inputs, and prediction downloads.
- Five-fold training-only Logistic Regression tuning.
- Held-out confusion matrix, stockout recall/F1, majority baseline, and direct-rule benchmark.
- Original Colab notebook with outputs cleared, preserving source code and analysis narrative.

## Source and changes

Source: `Inventory_Management_Previous_Code.ipynb`, modified 20 October 2026, in the user's Colab Notebooks folder. Also inspected Inventory_Management_1 and Inventory_Management_2. The source compares Logistic Regression, Decision Tree, Random Forest, and SVC and prefers tuned Logistic Regression. The app retains that model, balanced class weights, C/solver grid, five-fold stockout-F1 scoring, and the 80/20 stratified split with seed 100.

Encoding and scaling are now inside one sklearn pipeline so validation folds and inference use the same transformations without preprocessing leakage. The app does not repeat the source's large tree/forest/SVC searches at startup. The source notebook retains those experiments. Notebook plotting requires matplotlib and seaborn in addition to app requirements.

## Dataset and interpretation

The supplied training dataset has 5,000 records and 10 features, with 4,543 overstock labels and 457 stockout labels. Source provenance and redistribution licence were not supplied; no licence to the underlying dataset is asserted here.

Every supplied label follows `current_stock < reorder_point` -> stockout, otherwise overstock. No equality cases exist in training. The app identifies equality separately in the direct-rule output and asks for manual review. Above the reorder point is not sufficient evidence of excess stock in an actual business.

This is a current-state classification learning project, not validated future-risk forecasting. It contains no healthy-stock class, product/time identifiers, independently observed future outcomes, or validated cost-saving model. Class-weighted probability scores are not calibrated business probabilities. Recommendations are review prompts, not automatic purchase decisions.

## Reproduced evaluation

The 1,000-row holdout gives Logistic Regression 99.60% accuracy, 100% stockout recall, and 97.85% stockout F1 (91 stockouts detected, four false alerts). The explicit stock rule gives 100% accuracy. These results primarily demonstrate learning of the dataset's label rule and do not establish real-world forecasting performance. Full results: `evaluation.json`.

## Verify

```bash
python -m unittest test_app -v
python model.py
```

Tests cover held-out sample sizes, the label-rule check, invalid uploads, finite numeric values, matching batch/single inference, equality and zero-demand handling, all four Streamlit pages, and form submission. Uploaded rows are processed in server memory and not saved to disk by the app. Do not upload confidential inventory to an untrusted hosted instance.
