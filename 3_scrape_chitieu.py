import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.types import NVARCHAR, INTEGER, VARCHAR
from config import DB_CONNECTION_STRING
import os

def import_chitieu_from_excel():
    print("Bat dau nap du lieu chi tieu tu Excel...")
    engine = create_engine(DB_CONNECTION_STRING)
    excel_path = 'data/raw/Chỉ tiêu.xlsx'
    
    if not os.path.exists(excel_path):
        print(f"Lỗi: Không tìm thấy file {excel_path}")
        return

    try:
        # 1. Đọc dữ liệu
        df_excel = pd.read_excel(excel_path)
        
        # Tiền xử lý các dòng trống và định dạng cột năm học
        df_excel['nam_hoc'] = pd.to_numeric(df_excel['nam_hoc'], errors='coerce')
        df_excel = df_excel.dropna(subset=['nam_hoc'])
        df_excel['nam_hoc'] = df_excel['nam_hoc'].astype(int)
        
        # 2. Xử lý cột tỷ lệ chỉ tiêu (chuyển dấu phẩy thành dấu chấm)
        if 'ty_le_chi_tieu_thpt' in df_excel.columns:
            df_excel['ty_le_chi_tieu_thpt'] = df_excel['ty_le_chi_tieu_thpt'].astype(str).str.replace(',', '.')
            df_excel['ty_le_chi_tieu_thpt'] = pd.to_numeric(df_excel['ty_le_chi_tieu_thpt'], errors='coerce')
            df_excel['ty_le_chi_tieu_thpt'] = df_excel['ty_le_chi_tieu_thpt'].round(2)
        else:
            df_excel['ty_le_chi_tieu_thpt'] = None
        
        # Xử lý gán tên cột cho khớp logic SQL
        df_sql = df_excel.copy()
        if 'ma_to_hop' in df_sql.columns:
            df_sql['ma_xet_tuyen'] = df_sql['ma_to_hop']
            
        # 3. Tính toán chỉ tiêu thực tế dành cho xét tuyển THPT
        df_sql['tong_chi_tieu'] = pd.to_numeric(df_sql['tong_chi_tieu'], errors='coerce').fillna(0)
        df_sql['chi_tieu'] = df_sql['tong_chi_tieu'].astype(int) # File 7_train_model.py can chi_tieu la tong_chi_tieu
        
        # 4. Lọc đúng các cột cần thiết cho DB
        cols_to_keep = ['nam_hoc', 'ma_truong', 'chuong_trinh_dao_tao', 'ma_xet_tuyen', 'chi_tieu', 'ty_le_chi_tieu_thpt']
        for col in cols_to_keep:
            if col not in df_sql.columns:
                df_sql[col] = None
        df_sql = df_sql[cols_to_keep]

        # 5. Nạp vào SQL
        with engine.begin() as conn:
            # Đảm bảo trường tồn tại trong DanhMucTruong
            unique_schools = df_sql['ma_truong'].dropna().unique()
            for school in unique_schools:
                conn.execute(text(f"IF NOT EXISTS (SELECT 1 FROM DanhMucTruong WHERE ma_truong = '{school}') INSERT INTO DanhMucTruong (ma_truong, ten_truong) VALUES ('{school}', '{school}')"))
            
            # Xóa sạch dữ liệu cũ
            print("Dang xoa du lieu cu trong ChiTieuTruong...")
            conn.execute(text("DELETE FROM ChiTieuTruong"))
            
        print("Dang nap du lieu moi vao ChiTieuTruong...")
        from sqlalchemy.types import FLOAT
        df_sql.to_sql('ChiTieuTruong', con=engine, if_exists='append', index=False, dtype={
            'nam_hoc': INTEGER(),
            'ma_truong': VARCHAR(20),
            'chuong_trinh_dao_tao': NVARCHAR(255),
            'ma_xet_tuyen': VARCHAR(1000),
            'chi_tieu': INTEGER(),
            'ty_le_chi_tieu_thpt': FLOAT()
        })
        
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == '__main__':
    import_chitieu_from_excel()
    print("Da chay xong file: 3_scrape_chitieu.py")
