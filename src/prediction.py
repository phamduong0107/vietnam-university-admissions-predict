import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from config import DB_CONNECTION_STRING
from src.model_training import features, get_group_mask

def predict_2026(X_test_raw, df_chitieu_agg, ultimate_brain):
    engine = create_engine(DB_CONNECTION_STRING)
    df_2026 = X_test_raw.copy()
    df_2026['nam_hoc'] = 2026
    df_2026['diem_nam_ngoai'] = df_2026['diem_chuan']
    df_2026['diem_tb_nam_ngoai'] = df_2026['Diem_Trung_Binh']
    df_2026['ti_le_25_nam_ngoai'] = df_2026['ti_le_tren_25']
    df_2026['ti_le_27_nam_ngoai'] = df_2026['ti_le_tren_27']
    df_2026['chi_tieu_thuc_te_nam_ngoai'] = df_2026['chi_tieu_thuc_te']
    df_2026['ratio_diem_pho_diem'] = df_2026['diem_nam_ngoai'] / (df_2026['diem_tb_nam_ngoai'] + 1)
    df_2026['school_avg_score'] = df_2026['diem_nam_ngoai']
    df_2026['major_avg_score'] = df_2026['diem_nam_ngoai']
    df_2026['thi_format_moi'] = 1

    df_pho_2026 = pd.read_sql("SELECT Ma_To_Hop, Diem_Trung_Binh, So_Luong_Tren_25, So_Luong_Tren_27, Tong_So_Thi_Sinh FROM ThongKePhoDiem_Cache WHERE Nam = 2026", engine)
    pho_dict = df_pho_2026.set_index('Ma_To_Hop').to_dict('index')

    def get_2026_pho(row):
        combos = [c.strip() for c in str(row['ma_xet_tuyen']).split(',') if c.strip()]
        valid = [c for c in combos if c in pho_dict]
        if not valid:
            return row['Diem_Trung_Binh'], row['ti_le_tren_25'], row['ti_le_tren_27'], row['Tong_So_Thi_Sinh']
        dtb = max(pho_dict[c]['Diem_Trung_Binh'] for c in valid)
        ts = max(pho_dict[c]['Tong_So_Thi_Sinh'] for c in valid)
        tl25 = max(pho_dict[c]['So_Luong_Tren_25'] for c in valid) / ts if ts > 0 else 0
        tl27 = max(pho_dict[c]['So_Luong_Tren_27'] for c in valid) / ts if ts > 0 else 0
        return dtb, tl25, tl27, ts

    if not df_pho_2026.empty:
        pho_vals = df_2026.apply(get_2026_pho, axis=1, result_type='expand')
        df_2026['Diem_Trung_Binh'] = pho_vals[0]
        df_2026['ti_le_tren_25'] = pho_vals[1]
        df_2026['ti_le_tren_27'] = pho_vals[2]
        df_2026['Tong_So_Thi_Sinh'] = pho_vals[3]
        
    df_chitieu_2026 = df_chitieu_agg[df_chitieu_agg['nam_hoc'] == 2026].copy()
    if not df_chitieu_2026.empty:
        df_2026 = df_2026.drop(columns=['tong_chi_tieu', 'chi_tieu_thuc_te'])
        df_2026 = df_2026.merge(df_chitieu_2026[['ma_truong', 'clean_name', 'tong_chi_tieu', 'chi_tieu_thuc_te']], on=['ma_truong', 'clean_name'], how='left')
        df_2026['tong_chi_tieu'] = df_2026['tong_chi_tieu'].fillna(X_test_raw['tong_chi_tieu'])
        df_2026['chi_tieu_thuc_te'] = df_2026['chi_tieu_thuc_te'].fillna(X_test_raw['chi_tieu_thuc_te'])
        
    df_2026['ti_le_choi_tong'] = np.log1p(df_2026['Tong_So_Thi_Sinh'] / (df_2026['tong_chi_tieu'] + 1))
    
    m1_26, m2_26, m3_26 = get_group_mask(df_2026)

    cb_g1_dir, cb_g1_del, alpha_g1 = ultimate_brain['g1_dir'], ultimate_brain['g1_del'], ultimate_brain['g1_alpha']
    cb_g2_dir, cb_g2_del, alpha_g2 = ultimate_brain['g2_dir'], ultimate_brain['g2_del'], ultimate_brain['g2_alpha']
    cb_g3_dir, cb_g3_del, alpha_g3 = ultimate_brain['g3_dir'], ultimate_brain['g3_del'], ultimate_brain['g3_alpha']

    if m1_26.sum() > 0:
        X1 = df_2026[m1_26][features]
        df_2026.loc[m1_26, 'diem_chuan_du_bao'] = alpha_g1 * cb_g1_dir.predict(X1) + (1 - alpha_g1) * (cb_g1_del.predict(X1) + df_2026.loc[m1_26, 'diem_nam_ngoai'])
    if m2_26.sum() > 0:
        X2 = df_2026[m2_26][features]
        df_2026.loc[m2_26, 'diem_chuan_du_bao'] = alpha_g2 * cb_g2_dir.predict(X2) + (1 - alpha_g2) * (cb_g2_del.predict(X2) + df_2026.loc[m2_26, 'diem_nam_ngoai'])
    if m3_26.sum() > 0:
        X3 = df_2026[m3_26][features]
        df_2026.loc[m3_26, 'diem_chuan_du_bao'] = alpha_g3 * cb_g3_dir.predict(X3) + (1 - alpha_g3) * (cb_g3_del.predict(X3) + df_2026.loc[m3_26, 'diem_nam_ngoai'])
        
    out_df = df_2026[['ma_truong', 'chuong_trinh_dao_tao', 'ma_xet_tuyen', 'diem_chuan_du_bao', 'diem_nam_ngoai']].copy()
    out_df['diem_chuan_du_bao'] = out_df['diem_chuan_du_bao'].round(2)
    out_df['diem_nam_ngoai'] = out_df['diem_nam_ngoai'].round(2)
    out_df.to_csv('results/predictions_2026.csv', index=False, encoding='utf-8')
    print("Da luu ket qua du doan vao: results/predictions_2026.csv")
