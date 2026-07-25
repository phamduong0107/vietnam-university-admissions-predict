import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.types import String
import os
from config import DB_CONNECTION_STRING
engine = create_engine(DB_CONNECTION_STRING, fast_executemany=True)
RENAME_MAP = {
    'sbd': 'SOBAODANH', 'toan': 'Toan', 'ngu_van': 'Van', 'vat_li': 'Li', 
    'hoa_hoc': 'Hoa', 'sinh_hoc': 'Sinh', 'lich_su': 'Su', 'dia_li': 'Dia', 
    'gdcd': 'GD_KT_PL', 'ngoai_ngu': 'Ngoai_ngu', 'ma_ngoai_ngu': 'Ma_ngoai_ngu',
    'STT': 'STT', 'SOBAODANH': 'SOBAODANH', 'Toán': 'Toan', 'Văn': 'Van', 
    'Lí': 'Li', 'Hóa': 'Hoa', 'Sinh': 'Sinh', 'Tin học': 'Tin_hoc',
    'Công nghệ công nghiệp': 'Cong_nghe_CN', 'Công nghệ nông nghiệp': 'Cong_nghe_NN', 
    'Sử': 'Su', 'Địa': 'Dia', 'Giáo dục kinh tế và pháp luật': 'GD_KT_PL', 
    'Ngoại ngữ': 'Ngoai_ngu', 'Mã môn ngoại ngữ': 'Ma_ngoai_ngu',
    'dm1': 'Toan', 'dm2': 'Van', 'dm3': 'Ngoai_ngu', 'dm4': 'Su', 'dm5': 'Dia', 
    'dm6': 'GD_KT_PL', 'dm7': 'Li', 'dm8': 'Hoa', 'dm9': 'Sinh', 'dm10': 'Tin_hoc',
    'dm11': 'Mon_Khac_11', 'dm12': 'Cong_nghe_CN', 'dm13': 'Cong_nghe_NN',
    'NguVan': 'Van', 'VatLy': 'Li', 'HoaHoc': 'Hoa', 'SinhHoc': 'Sinh', 
    'LichSu': 'Su', 'DiaLy': 'Dia', 'GDCD': 'GD_KT_PL', 'KinhTePhapLuat': 'GD_KT_PL',
    'TinHoc': 'Tin_hoc', 'CongNgheCongNghiep': 'Cong_nghe_CN', 'CongNgheNongNghiep': 'Cong_nghe_NN',
    'NgoaiNgu': 'Ngoai_ngu', 'MaMonNgoaiNgu': 'Ma_ngoai_ngu', 'SBD': 'SOBAODANH'
}
COLS_TO_KEEP = ['nam_hoc', 'SOBAODANH', 'Toan', 'Van', 'Li', 'Hoa', 'Sinh', 
                'Tin_hoc', 'Cong_nghe_CN', 'Cong_nghe_NN', 'Su', 
                'Dia', 'GD_KT_PL', 'Ngoai_ngu', 'Ma_ngoai_ngu']
def clean_and_format_data(df, year):
    """Hàm dọn dẹp và chuẩn hóa dữ liệu chung cho cả CSV và Excel"""
    if year == 2026 and 'ngoai_ngu' in df.columns:
        df = df.rename(columns={'ngoai_ngu': 'Ma_ngoai_ngu'})
    df = df.rename(columns=RENAME_MAP)
    if 'STT' in df.columns:
        df = df.drop(columns=['STT'])
    if 'SOBAODANH' in df.columns:
        df['SOBAODANH'] = df['SOBAODANH'].astype(str).str.replace(r'\.0$', '', regex=True)
    df = df.loc[:, ~df.columns.duplicated()].copy()
    df['nam_hoc'] = year
    for c in COLS_TO_KEEP:
        if c not in df.columns:
            df[c] = None
    for col in ['Toan', 'Van', 'Li', 'Hoa', 'Sinh', 'Tin_hoc', 'Cong_nghe_CN', 'Cong_nghe_NN', 'Su', 'Dia', 'GD_KT_PL', 'Ngoai_ngu']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df[COLS_TO_KEEP].copy()
def import_excel_multi_sheets(file_path, year):
    """Đọc file Excel nhiều sheet"""
    if not os.path.exists(file_path):
        return
    all_sheets = pd.read_excel(file_path, sheet_name=None, dtype=str)
    for sheet_name, df in all_sheets.items():
        df_clean = clean_and_format_data(df, year)
        try:
            df_clean.to_sql('Staging_BangDiem', con=engine, if_exists='append', index=False, chunksize=100000, dtype={'SOBAODANH': String(50)})
        except Exception as e:
            print(f"Lỗi: {e}")
def import_csv(file_path, year):
    """Đọc file CSV hoặc TXT"""
    if not os.path.exists(file_path):
        return
    df = pd.read_csv(file_path, dtype=str)
    df_clean = clean_and_format_data(df, year)
    try:
        df_clean.to_sql('Staging_BangDiem', con=engine, if_exists='append', index=False, chunksize=100000, dtype={'SOBAODANH': String(50)})
    except Exception as e:
        print(f"Lỗi: {e}")
if __name__ == "__main__":
    print("Bat dau import du lieu vao SQL...")
    with engine.begin() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS Staging_BangDiem"))
        except Exception as e:
            print(f"Lỗi: {e}")
    print("Dang nap du lieu 2023...")
    import_csv('data/raw/diem_thpt_2023.csv', 2023)
    print("Dang nap du lieu 2024...")
    import_csv('data/raw/diem_thpt_2024.csv', 2024)
    print("Dang nap du lieu 2025...")
    import_csv('data/raw/diem_thpt_2025.csv', 2025)
    print("Dang nap du lieu 2026...")
    import_csv('data/raw/diem_thpt_2026.csv', 2026)

    print("Da chay xong file: 1_import_data_to_sql.py")
