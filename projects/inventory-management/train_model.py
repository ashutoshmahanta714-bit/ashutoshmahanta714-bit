"""Recreate the notebook's tuned Logistic Regression deployment artifacts."""
import argparse
import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def train(dataset, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    df = pd.read_excel(dataset)
    x = df.drop(columns='stock_status')
    y = df['stock_status']
    xt, xv, yt, yv = train_test_split(x, y, test_size=0.2, random_state=100, stratify=y)
    cats = ['season', 'item_category', 'supplier_reliability']
    oe, le = OrdinalEncoder(), LabelEncoder()
    xt, xv = xt.copy(), xv.copy()
    xt[cats] = oe.fit_transform(xt[cats])
    xv[cats] = oe.transform(xv[cats])
    yt, yv = le.fit_transform(yt), le.transform(yv)
    pipeline = Pipeline([('scaler', StandardScaler()), ('lr', LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42))])
    search = GridSearchCV(pipeline, {'lr__C': [0.01, 0.1, 1, 10, 100], 'lr__solver': ['lbfgs', 'liblinear']}, cv=5, scoring='f1', n_jobs=2)
    search.fit(xt, yt)
    model = search.best_estimator_
    artifacts = {'best_lr_model.pkl': model, 'ordinal_encoder.pkl': oe, 'label_encoder.pkl': le, 'feature_columns.pkl': x.columns.tolist()}
    for name, obj in artifacts.items():
        with (output / name).open('wb') as f:
            pickle.dump(obj, f)
    pred = model.predict(xv)
    # Check predictions after loading all four exported files from disk.
    loaded = {}
    for name in artifacts:
        with (output / name).open('rb') as f:
            loaded[name] = pickle.load(f)
    raw_test = x.loc[xv.index].copy()[loaded['feature_columns.pkl']]
    raw_test[cats] = loaded['ordinal_encoder.pkl'].transform(raw_test[cats])
    restored = loaded['best_lr_model.pkl'].predict(raw_test)
    assert np.array_equal(restored, pred)
    assert np.array_equal(loaded['label_encoder.pkl'].inverse_transform(restored), le.inverse_transform(pred))
    all_input = x.copy()
    all_input[cats] = oe.transform(all_input[cats])
    all_pred = le.inverse_transform(model.predict(all_input))
    report = {'sklearn_version': sklearn.__version__, 'rows': len(df), 'best_parameters': search.best_params_, 'cv_stockout_f1': search.best_score_, 'test_accuracy': accuracy_score(yv, pred), 'test_report': classification_report(yv, pred, target_names=le.classes_, output_dict=True), 'test_confusion_matrix': confusion_matrix(yv, pred).tolist(), 'actual_class_counts': y.value_counts().to_dict(), 'all_rows_predicted_counts': pd.Series(all_pred).value_counts().to_dict(), 'reload_predictions_match': True, 'label_mapping': {str(i): label for i, label in enumerate(le.classes_)}}
    (output / 'validation_results.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('dataset')
    p.add_argument('--output', default=str(Path(__file__).parent))
    args = p.parse_args()
    train(args.dataset, args.output)
