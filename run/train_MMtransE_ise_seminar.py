import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/MMTransE'))

from MMTransE import MMTransE

model = MMTransE(dim=75, save_dir=os.path.join(os.path.dirname(__file__), 'model_MMtransE_person_ISE.bin'))
model.Train_MT(epochs=10, save_every_epochs=100, languages=['en', 'en'], graphs=[os.path.join(os.path.dirname(__file__), '../data/P_db.csv'), os.path.join(os.path.dirname(__file__), '../data/P_y.csv')], intersect_graph=os.path.join(os.path.dirname(__file__), '../data/P_db2y.csv'), save_dirs = ['model_en.bin','model_en.bin'], rate=0.01, split_rate=True, L1_flag=False)
model.save(os.path.join(os.path.dirname(__file__), 'model_MMtransE_person_ISE.bin'))
