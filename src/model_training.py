import pandas as pd
import numpy as np
import optuna
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

optuna.logging.set_verbosity(optuna.logging.WARNING)

features = [
    'ma_truong_cat', 'ma_nganh_chuan_cat',
    'Diem_Trung_Binh', 'ti_le_tren_25', 'ti_le_tren_27', 'Tong_So_Thi_Sinh', 
    'chi_tieu_thuc_te', 
    'diem_nam_ngoai', 'diem_tb_nam_ngoai', 'ti_le_25_nam_ngoai', 'ti_le_27_nam_ngoai',
    'ratio_diem_pho_diem', 'ti_le_choi_tong',
    'tier_score', 'trend_score',
    'school_avg_score', 'major_avg_score',
    'thi_format_moi'
]

def get_group_mask(df):
    mask_group1 = df['ma_nganh_chuan'].isin(['IT', 'ENG', 'SCI'])
    mask_group2 = df['ma_nganh_chuan'].isin(['BIZ', 'LAW', 'LANG_SOC', 'EDU', 'ART'])
    mask_group3 = df['ma_nganh_chuan'].isin(['MED', 'AGRI', 'OTHER'])
    return mask_group1, mask_group2, mask_group3

def prepare_group_data(df_train, df_test):
    X_train = df_train[features].copy()
    y_train_direct = df_train['diem_chuan']
    y_train_delta = df_train['delta_diem_chuan_thuc_te']
    weight_train = df_train['tier_score'].map({3: 3.0, 2: 1.5, 1: 1.0}).fillna(1.0).values 
    
    X_test = df_test[features].copy()
    y_test = df_test['diem_chuan']
    diem_lag_test = df_test['diem_nam_ngoai'].values
    
    for col in ['ma_truong_cat', 'ma_nganh_chuan_cat']:
        X_train[col] = X_train[col].astype(str)
        X_test[col] = X_test[col].astype(str)
        
    return X_train, y_train_direct, y_train_delta, weight_train, X_test, y_test, diem_lag_test

def optimize_catboost(X, y, w, year_col):
    if len(X) < 10:
        return {'iterations': 500, 'learning_rate': 0.1, 'depth': 4}
        
    def objective(trial):
        params = {
            'iterations': trial.suggest_int('iterations', 500, 3000),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.2, log=True),
            'depth': trial.suggest_int('depth', 3, 6),
            'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 10, 40),
            'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 5.0, 30.0),
            'loss_function': 'MAE',
            'verbose': 0,
            'cat_features': ['ma_truong_cat', 'ma_nganh_chuan_cat'],
            'random_seed': 42,
            'feature_weights': 'trend_score:3.0'
        }
        
        mask_val = year_col == year_col.max()
        if mask_val.sum() == 0 or mask_val.sum() == len(year_col):
            X_train, X_val, y_train, y_val, weight_train, weight_val = train_test_split(X, y, w, test_size=0.2, random_state=42)
        else:
            X_train, y_train, weight_train = X[~mask_val], y[~mask_val], w[~mask_val]
            X_val, y_val, weight_val = X[mask_val], y[mask_val], w[mask_val]
            
        model = CatBoostRegressor(**params)
        model.fit(X_train, y_train, sample_weight=weight_train, eval_set=(X_val, y_val), early_stopping_rounds=50, verbose=0)
        preds = model.predict(X_val)
        return mean_absolute_error(y_val, preds)
        
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=10) 
    return study.best_params

def train_best_catboost(X, y_direct, y_delta, weight, best_params):
    if len(X) == 0: return None, None
    best_params['loss_function'] = 'MAE'
    best_params['verbose'] = 0
    best_params['cat_features'] = ['ma_truong_cat', 'ma_nganh_chuan_cat']
    best_params['random_seed'] = 42
    if 'feature_weights' not in best_params:
        best_params['feature_weights'] = 'trend_score:3.0'
        
    catboost_direct = CatBoostRegressor(**best_params)
    catboost_direct.fit(X, y_direct, sample_weight=weight)
    
    catboost_delta = CatBoostRegressor(**best_params)
    catboost_delta.fit(X, y_delta, sample_weight=weight)
    return catboost_direct, catboost_delta

def find_best_alpha(y_true, preds_direct, preds_delta, diem_lag):
    best_alpha, best_mae = 0.5, 999
    for alpha_blend in np.arange(0.0, 1.01, 0.01):
        blend = alpha_blend * preds_direct + (1 - alpha_blend) * (preds_delta + diem_lag)
        mae = mean_absolute_error(y_true, blend)
        if mae < best_mae:
            best_mae, best_alpha = mae, alpha_blend
    return best_alpha, best_mae

def predict_group(catboost_direct, catboost_delta, X_test, y_test, diem_lag_test):
    if len(X_test) == 0: return 0.5, np.array([])
    preds_direct = catboost_direct.predict(X_test)
    preds_delta = catboost_delta.predict(X_test)
    alpha_blend, mae = find_best_alpha(y_test, preds_direct, preds_delta, diem_lag_test)
    return alpha_blend, (alpha_blend * preds_direct + (1 - alpha_blend) * (preds_delta + diem_lag_test))

def train_all_groups(df_full, X_train_raw, X_test_raw):
    mask_g1_train, mask_g2_train, mask_g3_train = get_group_mask(X_train_raw)
    mask_g1_test, mask_g2_test, mask_g3_test = get_group_mask(X_test_raw)

    print("Prepare Data...")
    X_g1_train, y_g1_train_direct, y_g1_train_delta, weight_g1, X_g1_test, y_g1_test, diem_lag_g1_test = prepare_group_data(X_train_raw[mask_g1_train], X_test_raw[mask_g1_test])
    X_g2_train, y_g2_train_direct, y_g2_train_delta, weight_g2, X_g2_test, y_g2_test, diem_lag_g2_test = prepare_group_data(X_train_raw[mask_g2_train], X_test_raw[mask_g2_test])
    X_g3_train, y_g3_train_direct, y_g3_train_delta, weight_g3, X_g3_test, y_g3_test, diem_lag_g3_test = prepare_group_data(X_train_raw[mask_g3_train], X_test_raw[mask_g3_test])

    print("Training G1...")
    best_params_g1 = optimize_catboost(X_g1_train, y_g1_train_direct, weight_g1, X_train_raw.loc[mask_g1_train, 'nam_hoc'])
    catboost_g1_direct, catboost_g1_delta = train_best_catboost(X_g1_train, y_g1_train_direct, y_g1_train_delta, weight_g1, best_params_g1)

    print("Training G2...")
    best_params_g2 = optimize_catboost(X_g2_train, y_g2_train_direct, weight_g2, X_train_raw.loc[mask_g2_train, 'nam_hoc'])
    catboost_g2_direct, catboost_g2_delta = train_best_catboost(X_g2_train, y_g2_train_direct, y_g2_train_delta, weight_g2, best_params_g2)

    print("Training G3...")
    best_params_g3 = optimize_catboost(X_g3_train, y_g3_train_direct, weight_g3, X_train_raw.loc[mask_g3_train, 'nam_hoc'])
    catboost_g3_direct, catboost_g3_delta = train_best_catboost(X_g3_train, y_g3_train_direct, y_g3_train_delta, weight_g3, best_params_g3)

    print("Evaluating...")
    alpha_g1, final_preds_g1 = predict_group(catboost_g1_direct, catboost_g1_delta, X_g1_test, y_g1_test, diem_lag_g1_test)
    alpha_g2, final_preds_g2 = predict_group(catboost_g2_direct, catboost_g2_delta, X_g2_test, y_g2_test, diem_lag_g2_test)
    alpha_g3, final_preds_g3 = predict_group(catboost_g3_direct, catboost_g3_delta, X_g3_test, y_g3_test, diem_lag_g3_test)

    y_test_final = pd.concat([y for y in [y_g1_test, y_g2_test, y_g3_test] if len(y) > 0])
    preds_final = np.concatenate([p for p in [final_preds_g1, final_preds_g2, final_preds_g3] if len(p) > 0])
    
    final_mae = mean_absolute_error(y_test_final, preds_final)
    final_r2 = r2_score(y_test_final, preds_final)
    
    print("==========================================")
    print("KET QUA HUAN LUYEN MO HINH:")
    print(f"MAE (Sai so trung binh): {final_mae:.4f} diem")
    print(f"R2 Score (Do chinh xac): {final_r2:.4f}")
    print("==========================================")

    ultimate_brain = {
        'g1_dir': catboost_g1_direct, 'g1_del': catboost_g1_delta, 'g1_alpha': alpha_g1,
        'g2_dir': catboost_g2_direct, 'g2_del': catboost_g2_delta, 'g2_alpha': alpha_g2,
        'g3_dir': catboost_g3_direct, 'g3_del': catboost_g3_delta, 'g3_alpha': alpha_g3
    }
    
    import os
    if not os.path.exists('models'):
        os.makedirs('models')
    joblib.dump(ultimate_brain, 'models/ultimate_model.pkl')
    
    return ultimate_brain
