import unittest
import numpy as np
import pandas as pd
from model import load_data, train, predict, validate, FEATURES
class InventoryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=load_data(); cls.model,cls.report=train()
 def test_dataset_rule_and_holdout(self):
  self.assertEqual(self.report['label_rule_agreement'],1.0)
  self.assertEqual(self.report['training_rows'],4000)
  self.assertEqual(self.report['test_rows'],1000)
  self.assertEqual(self.report['direct_rule']['accuracy'],1.0)
 def test_validation(self):
  base=self.data[FEATURES].head(1).copy()
  for col,val in [('current_stock',-1),('avg_daily_demand',np.inf),('season','winter')]:
   bad=base.copy();bad[col]=val
   with self.assertRaises(ValueError):validate(bad)
  with self.assertRaises(ValueError):validate(base.drop(columns='season'))
  with self.assertRaises(ValueError):validate(base.iloc[:0])
 def test_batch_matches_single(self):
  frame=self.data.head(5);batch=predict(self.model,frame)
  singles=pd.concat([predict(self.model,frame.iloc[[i]]) for i in range(5)])
  pd.testing.assert_frame_equal(batch,singles)
  self.assertTrue(batch.model_stockout_probability.between(0,1).all())
 def test_boundary_and_zero_demand(self):
  frame=self.data.head(1).copy();frame['current_stock']=frame['reorder_point'];frame['avg_daily_demand']=0
  result=predict(self.model,frame)
  self.assertEqual(result.stock_rule.iloc[0],'at reorder point')
  self.assertTrue(pd.isna(result.stock_coverage_days.iloc[0]))
 def test_streamlit_pages(self):
  from streamlit.testing.v1 import AppTest
  at=AppTest.from_file('app.py',default_timeout=60).run()
  self.assertEqual(len(at.exception),0)
  for name in ['Single product','Batch predictions','Model evaluation']:
   at.sidebar.radio[0].set_value(name).run()
   self.assertEqual(len(at.exception),0,name)
   if name=='Single product':
    at.button[0].click().run();self.assertEqual(len(at.exception),0);self.assertEqual(len(at.metric),3)
if __name__=='__main__':unittest.main()
