"""Deployable adaptation of Ashutosh's Colab inventory classification workflow."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

ROOT = Path(__file__).resolve().parent
NUMERIC = ['current_stock', 'avg_daily_demand', 'lead_time_days', 'reorder_point',
           'sales_last_30_days', 'stock_turnover_ratio', 'forecast_error']
CATEGORIES = {'season': ['off-peak', 'peak'], 'item_category': ['essential', 'non-essential'],
              'supplier_reliability': ['high', 'low']}
FEATURES = NUMERIC + list(CATEGORIES)

def load_data():
    return pd.read_csv(ROOT / 'data' / 'stock_risk.csv')

def validate(frame):
    if frame.empty:
        raise ValueError('Provide at least one product row.')
    if len(frame) > 10000:
        raise ValueError('Upload at most 10,000 products at a time.')
    missing = set(FEATURES) - set(frame.columns)
    if missing:
        raise ValueError('Missing columns: ' + ', '.join(sorted(missing)))
    x = frame[FEATURES].copy()
    for col in NUMERIC:
        x[col] = pd.to_numeric(x[col], errors='coerce')
        if not np.isfinite(x[col]).all():
            raise ValueError(f'{col}: every value must be a finite number.')
        if col != 'forecast_error' and (x[col] < 0).any():
            raise ValueError(f'{col}: values cannot be negative.')
    for col, allowed in CATEGORIES.items():
        x[col] = x[col].astype(str).str.strip().str.lower()
        if not x[col].isin(allowed).all():
            raise ValueError(f'{col}: allowed values are {", ".join(allowed)}.')
    return x

def preprocessing():
    # Fixed category order matches OrdinalEncoder's alphabetical order in Colab.
    return ColumnTransformer([
        ('numeric', 'passthrough', NUMERIC),
        ('category', OrdinalEncoder(categories=list(CATEGORIES.values())), list(CATEGORIES))
    ])

def make_pipeline(estimator, scale=True):
    steps = [('encoding', preprocessing())]
    if scale:
        steps.append(('scaling', StandardScaler()))
    return Pipeline(steps + [('model', estimator)])

def metrics(y, pred):
    return {'accuracy': float(accuracy_score(y, pred)),
            'stockout_precision': float(precision_score(y, pred, zero_division=0)),
            'stockout_recall': float(recall_score(y, pred, zero_division=0)),
            'stockout_f1': float(f1_score(y, pred, zero_division=0)),
            'confusion_matrix': confusion_matrix(y, pred, labels=[0,1]).tolist()}

def train():
    data = load_data()
    x = validate(data)
    y = (data.stock_status == 'stockout').astype(int)
    xtr, xte, ytr, yte = train_test_split(x, y, test_size=.2, random_state=100, stratify=y)
    cv = StratifiedKFold(n_splits=5, shuffle=False)
    search = GridSearchCV(make_pipeline(LogisticRegression(class_weight='balanced',
                            max_iter=1000, random_state=42)),
                          {'model__C': [.01,.1,1,10,100], 'model__solver': ['lbfgs','liblinear']},
                          scoring='f1', cv=cv, n_jobs=1)
    search.fit(xtr,ytr)
    model = search.best_estimator_
    pred = model.predict(xte)
    rule = (xte.current_stock < xte.reorder_point).astype(int)
    report = {'rows':len(data), 'training_rows':len(xtr), 'test_rows':len(xte),
              'seed':100, 'selected_model':'Tuned Logistic Regression',
              'selection_reason':'Retains the model preferred in the source Colab notebook; hyperparameters selected using training-only cross-validation.',
              'best_parameters':search.best_params_, 'cv_stockout_f1':float(search.best_score_),
              'heldout_test':metrics(yte,pred), 'direct_rule':metrics(yte,rule),
              'majority_baseline':metrics(yte,np.full(len(yte),int(ytr.mode().iloc[0]))),
              'label_rule_agreement':float(((x.current_stock < x.reorder_point).astype(int)==y).mean()),
              'test_labels':{'overstock':int((yte==0).sum()),'stockout':int((yte==1).sum())}}
    return model, report

def predict(model, frame):
    x = validate(frame)
    result = x.copy()
    result['model_prediction'] = np.where(model.predict(x)==1,'stockout','overstock')
    idx = list(model.classes_).index(1)
    result['model_stockout_probability'] = model.predict_proba(x)[:,idx]
    result['stock_rule'] = np.select([x.current_stock < x.reorder_point,
                                    x.current_stock > x.reorder_point],
                                   ['stockout','overstock'], default='at reorder point')
    result['units_vs_reorder_point'] = x.current_stock - x.reorder_point
    result['stock_coverage_days'] = np.divide(x.current_stock,x.avg_daily_demand,
                                           out=np.full(len(x),np.nan),where=x.avg_daily_demand.to_numpy()!=0)
    return result

if __name__ == '__main__':
    import json
    _, report = train()
    print(json.dumps(report, indent=2))
