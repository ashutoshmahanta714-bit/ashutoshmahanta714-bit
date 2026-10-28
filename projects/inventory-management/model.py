"""Deployable adaptation of Ashutosh's Colab inventory classification workflow."""
from pathlib import Path
import numpy as np
import pandas as pd

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

class DeploymentModel:
    """Apply the notebook's saved encoder before its scaling/model pipeline."""
    def __init__(self, pipeline, encoder, labels, columns):
        self.pipeline = pipeline
        self.encoder = encoder
        self.labels = labels
        self.columns = columns
        self.classes_ = pipeline.classes_

    def _encode(self, frame):
        features = validate(frame).loc[:, self.columns].copy()
        cat_cols = self.encoder.feature_names_in_.tolist()
        features[cat_cols] = self.encoder.transform(features[cat_cols])
        return features

    def predict(self, frame):
        return self.pipeline.predict(self._encode(frame))

    def predict_proba(self, frame):
        return self.pipeline.predict_proba(self._encode(frame))


def load_deployment():
    """Load fitted artifacts and their held-out evaluation; never train at startup."""
    import json
    import pickle
    objects = []
    for name in ['best_lr_model.pkl', 'ordinal_encoder.pkl', 'label_encoder.pkl', 'feature_columns.pkl']:
        with (ROOT / name).open('rb') as stream:
            objects.append(pickle.load(stream))
    pipeline, encoder, labels, columns = objects
    if columns != FEATURES or labels.classes_.tolist() != ['overstock', 'stockout']:
        raise ValueError('Model artifact schema or label mapping is incompatible.')
    for field, categories in zip(encoder.feature_names_in_, encoder.categories_):
        if categories.tolist() != CATEGORIES[field]:
            raise ValueError(f'Category mapping mismatch for {field}.')
    report = json.loads((ROOT / 'evaluation.json').read_text())
    return DeploymentModel(pipeline, encoder, labels, columns), report

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
    _, report = load_deployment()
    print(json.dumps(report, indent=2))

