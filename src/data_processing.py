import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import re
import unicodedata
from config import DB_CONNECTION_STRING

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'\(.*?\)', '', text)
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    return text.strip()

def clean_number(val):
    try:
        val = str(val).replace(',', '.')
        return float(val)
    except:
        return np.nan

def map_standard_major(name):
    name = str(name).lower()
    if re.search(r'(công nghệ thông tin|máy tính|phần mềm|trí tuệ nhân tạo|ai|khoa học dữ liệu|an toàn thông tin|mạng|hệ thống thông tin|iot|robot)', name): return 'IT'
    if re.search(r'(kinh doanh|kinh tế|quản trị|marketing|kế toán|kiểm toán|tài chính|ngân hàng|thương mại|logistics|chuỗi cung ứng|khách sạn|du lịch|bất động sản|nhân lực)', name): return 'BIZ'
    if re.search(r'(cơ điện tử|ô tô|tự động hóa|điện|viễn thông|xây dựng|kiến trúc|cơ kỹ thuật|cơ khí|vật liệu|chế tạo|hàng không|công nghệ kỹ thuật|giao thông|môi trường|sinh học|hóa học)', name): return 'ENG'
    if re.search(r'(y khoa|răng hàm mặt|dược|điều dưỡng|y tế|phục hồi chức năng|y học|thú y)', name): return 'MED'
    if re.search(r'(ngôn ngữ|tiếng anh|tiếng trung|tiếng hàn|tiếng nhật|tiếng pháp|văn học|đông phương học|quốc tế học|ngữ văn|truyền thông|báo chí|quan hệ công chúng)', name): return 'LANG_SOC'
    if re.search(r'(sư phạm|giáo dục|mầm non|tiểu học)', name): return 'EDU'
    if re.search(r'(luật|pháp lý|pháp luật)', name): return 'LAW'
    if re.search(r'(nông nghiệp|lâm nghiệp|thủy sản|cây trồng|vật nuôi|đất|thực phẩm)', name): return 'AGRI'
    if re.search(r'(toán|lý|hóa|sinh|khoa học|thống kê)', name): return 'SCI'
    if re.search(r'(nghệ thuật|thiết kế|đồ họa|kiến trúc|mỹ thuật|thời trang|âm nhạc)', name): return 'ART'
    return 'OTHER'

def load_and_preprocess_data():
    engine = create_engine(DB_CONNECTION_STRING)
    
    # 1. Load History Data
    query_history = "SELECT nam_hoc, ma_truong, chuong_trinh_dao_tao, ma_xet_tuyen, diem_chuan FROM DiemChuanTruong WHERE diem_chuan IS NOT NULL"
    df_history_raw = pd.read_sql(query_history, engine)
    df_history_raw['clean_name'] = df_history_raw['chuong_trinh_dao_tao'].apply(clean_text)
    df_history = df_history_raw.groupby(['nam_hoc', 'ma_truong', 'clean_name']).agg({
        'diem_chuan': 'first'
    }).reset_index()
    df_lag1 = df_history.copy()
    df_lag1['nam_hoc'] += 1
    df_lag1 = df_lag1.rename(columns={'diem_chuan': 'diem_nam_ngoai'})
    
    # 2. Load Current Data & Pho Diem
    query_sql = """
    SELECT d.nam_hoc, d.ma_truong, d.chuong_trinh_dao_tao, d.ma_xet_tuyen, 
           p.Diem_Trung_Binh, p.So_Luong_Tren_25, p.So_Luong_Tren_27, p.Tong_So_Thi_Sinh, d.diem_chuan
    FROM DiemChuanTruong d
    JOIN ThongKePhoDiem_Cache p ON d.nam_hoc = p.Nam AND d.ma_xet_tuyen = p.Ma_To_Hop
    WHERE d.diem_chuan IS NOT NULL
    """
    df_diem_raw = pd.read_sql(query_sql, engine)
    df_diem_raw['clean_name'] = df_diem_raw['chuong_trinh_dao_tao'].apply(clean_text)
    df_diem = df_diem_raw.groupby(['nam_hoc', 'ma_truong', 'clean_name']).agg({
        'diem_chuan': 'first',
        'chuong_trinh_dao_tao': 'first',
        'ma_xet_tuyen': lambda x: ','.join(x.unique()),
        'Diem_Trung_Binh': 'max', 
        'So_Luong_Tren_25': 'max',
        'So_Luong_Tren_27': 'max',
        'Tong_So_Thi_Sinh': 'max'
    }).reset_index()
    
    df_diem['ti_le_tren_25'] = (df_diem['So_Luong_Tren_25'] / df_diem['Tong_So_Thi_Sinh']).fillna(0)
    df_diem['ti_le_tren_27'] = (df_diem['So_Luong_Tren_27'] / df_diem['Tong_So_Thi_Sinh']).fillna(0)
    
    # Merge history
    df_diem = df_diem.merge(df_lag1[['nam_hoc', 'ma_truong', 'clean_name', 'diem_nam_ngoai']], 
                            on=['nam_hoc', 'ma_truong', 'clean_name'], how='left')
    df_diem = df_diem.dropna(subset=['diem_nam_ngoai'])
    
    df_diem_lag_pho = df_diem[['nam_hoc', 'ma_truong', 'clean_name', 'Diem_Trung_Binh', 'ti_le_tren_25', 'ti_le_tren_27']].copy()
    df_diem_lag_pho['nam_hoc'] += 1
    df_diem_lag_pho = df_diem_lag_pho.rename(columns={'Diem_Trung_Binh': 'diem_tb_nam_ngoai', 'ti_le_tren_25': 'ti_le_25_nam_ngoai', 'ti_le_tren_27': 'ti_le_27_nam_ngoai'})
    df_diem = df_diem.merge(df_diem_lag_pho, on=['nam_hoc', 'ma_truong', 'clean_name'], how='left')
    df_diem['diem_tb_nam_ngoai'] = df_diem['diem_tb_nam_ngoai'].fillna(df_diem['Diem_Trung_Binh'])
    df_diem['ti_le_25_nam_ngoai'] = df_diem['ti_le_25_nam_ngoai'].fillna(df_diem['ti_le_tren_25'])
    df_diem['ti_le_27_nam_ngoai'] = df_diem['ti_le_27_nam_ngoai'].fillna(df_diem['ti_le_tren_27'])
    
    # 3. Load Chi Tieu
    df_chitieu = pd.read_sql("SELECT nam_hoc, ma_truong, chuong_trinh_dao_tao, chi_tieu as tong_chi_tieu, ty_le_chi_tieu_thpt FROM ChiTieuTruong", engine)
    df_chitieu['tong_chi_tieu'] = df_chitieu['tong_chi_tieu'].apply(clean_number)
    df_chitieu['ty_le_chi_tieu_thpt'] = df_chitieu['ty_le_chi_tieu_thpt'].fillna(0.5)
    df_chitieu['chi_tieu_thuc_te'] = df_chitieu['tong_chi_tieu'] * df_chitieu['ty_le_chi_tieu_thpt']
    df_chitieu['clean_name'] = df_chitieu['chuong_trinh_dao_tao'].apply(clean_text)
    
    df_chitieu_agg = df_chitieu.groupby(['nam_hoc', 'ma_truong', 'clean_name']).agg({
        'tong_chi_tieu': 'sum',
        'chi_tieu_thuc_te': 'sum'
    }).reset_index()
    
    df_chitieu_lag1 = df_chitieu_agg.copy()
    df_chitieu_lag1['nam_hoc'] += 1
    df_chitieu_lag1 = df_chitieu_lag1.rename(columns={'chi_tieu_thuc_te': 'chi_tieu_thuc_te_nam_ngoai'})[['nam_hoc', 'ma_truong', 'clean_name', 'chi_tieu_thuc_te_nam_ngoai']]
    
    df_chitieu_agg = df_chitieu_agg.merge(df_chitieu_lag1, on=['nam_hoc', 'ma_truong', 'clean_name'], how='left')
    df_chitieu_agg['chi_tieu_thuc_te_nam_ngoai'] = df_chitieu_agg['chi_tieu_thuc_te_nam_ngoai'].fillna(df_chitieu_agg['chi_tieu_thuc_te'])
    
    # Merge all
    df_full = df_diem.merge(df_chitieu_agg, on=['nam_hoc', 'ma_truong', 'clean_name'], how='left')
    df_full['tong_chi_tieu'] = df_full['tong_chi_tieu'].fillna(df_full.groupby('ma_truong')['tong_chi_tieu'].transform('median')).fillna(100)
    df_full['chi_tieu_thuc_te'] = df_full['chi_tieu_thuc_te'].fillna(df_full['tong_chi_tieu'] * 0.5)
    df_full['chi_tieu_thuc_te_nam_ngoai'] = df_full['chi_tieu_thuc_te_nam_ngoai'].fillna(df_full['chi_tieu_thuc_te'])
    
    # 4. Load External Features
    df_tier = pd.read_excel('data/raw/Tier list.xlsx')
    df_full = df_full.merge(df_tier[['ma_truong', 'tier_ranking']], on='ma_truong', how='left')
    df_full['tier_ranking'] = df_full['tier_ranking'].fillna('Tier 3')
    df_full['tier_score'] = df_full['tier_ranking'].map({'Tier 3': 1, 'Tier 2': 2, 'Tier 1': 3})
    
    df_full['ma_nganh_chuan'] = df_full['chuong_trinh_dao_tao'].apply(map_standard_major)
    
    df_trend = pd.read_csv('data/raw/trend_nganh_google.csv')
    df_full = df_full.merge(df_trend[['nam_hoc', 'ma_nganh_chuan', 'trend_score']], on=['nam_hoc', 'ma_nganh_chuan'], how='left')
    df_full['trend_score'] = df_full['trend_score'].fillna(20.0)
    
    # 5. Feature Engineering
    df_full['ratio_diem_pho_diem'] = df_full['diem_nam_ngoai'] / (df_full['diem_tb_nam_ngoai'] + 1)
    df_full['ti_le_choi_tong'] = np.log1p(df_full['Tong_So_Thi_Sinh'] / (df_full['tong_chi_tieu'] + 1))
    
    # Mask scale
    mask_scale = df_full['chuong_trinh_dao_tao'].str.contains('tiếng anh|ngôn ngữ anh|hệ số 2', case=False, na=False) | df_full['ma_xet_tuyen'].str.contains('D01', na=False)
    df_full.loc[mask_scale, 'diem_chuan'] = (df_full.loc[mask_scale, 'diem_chuan'] / 40.0) * 30.0
    df_full.loc[mask_scale, 'diem_nam_ngoai'] = (df_full.loc[mask_scale, 'diem_nam_ngoai'] / 40.0) * 30.0
    df_full['delta_diem_chuan_thuc_te'] = df_full['diem_chuan'] - df_full['diem_nam_ngoai']
    
    # Group Averages
    school_avg = df_full.groupby(['nam_hoc', 'ma_truong'])['diem_chuan'].mean().reset_index()
    school_avg['nam_hoc'] += 1
    school_avg = school_avg.rename(columns={'diem_chuan': 'school_avg_score'})
    
    major_avg = df_full.groupby(['nam_hoc', 'ma_nganh_chuan'])['diem_chuan'].mean().reset_index()
    major_avg['nam_hoc'] += 1
    major_avg = major_avg.rename(columns={'diem_chuan': 'major_avg_score'})
    
    df_full = df_full.merge(school_avg, on=['nam_hoc', 'ma_truong'], how='left')
    df_full['school_avg_score'] = df_full['school_avg_score'].fillna(df_full['diem_nam_ngoai'])
    
    df_full = df_full.merge(major_avg, on=['nam_hoc', 'ma_nganh_chuan'], how='left')
    df_full['major_avg_score'] = df_full['major_avg_score'].fillna(df_full['diem_nam_ngoai'])
    
    df_full['thi_format_moi'] = (df_full['nam_hoc'] >= 2025).astype(int)
    
    df_full['ma_truong_cat'] = df_full['ma_truong'].astype('category')
    df_full['ma_nganh_chuan_cat'] = df_full['ma_nganh_chuan'].astype('category')
    
    # 6. Train Test Split
    train_mask = df_full['nam_hoc'] < 2025
    test_mask = df_full['nam_hoc'] == 2025
    
    X_train_raw = df_full[train_mask].copy()
    X_test_raw = df_full[test_mask].copy()
    
    return df_full, X_train_raw, X_test_raw, df_chitieu_agg
