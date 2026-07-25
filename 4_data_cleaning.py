import pandas as pd
from sqlalchemy import create_engine, text
import difflib
from config import DB_CONNECTION_STRING
def data_cleaning():
    print("Bat dau data cleaning...")
    engine = create_engine(DB_CONNECTION_STRING)
    with engine.begin() as conn:
        # Xử lý các trường luôn dùng thang 40 (NHF)
        conn.execute(text("UPDATE DiemChuanTruong SET diem_chuan = ROUND((diem_chuan / 40.0) * 30.0, 2) WHERE ma_truong IN ('NHF') AND diem_chuan > 10"))
    query_chitieu = "SELECT DISTINCT ma_truong, chuong_trinh_dao_tao AS ten_chitieu FROM ChiTieuTruong WHERE chuong_trinh_dao_tao IS NOT NULL"
    df_ct = pd.read_sql(query_chitieu, engine)
    
    query_diemchuan = "SELECT DISTINCT ma_truong, chuong_trinh_dao_tao AS ten_diemchuan FROM DiemChuanTruong WHERE chuong_trinh_dao_tao IS NOT NULL"
    df_dc = pd.read_sql(query_diemchuan, engine)
    
    import re
    def clean_str(s):
        if not isinstance(s, str): return ''
        s = s.lower()
        s = re.sub(r'chương trình\s*|đại trà\s*|chất lượng cao\s*|chuyên ngành\s*', '', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    schools = df_ct['ma_truong'].unique()
    update_queries = []
    
    for school in schools:
        ct_majors = df_ct[df_ct['ma_truong'] == school]['ten_chitieu'].tolist()
        dc_majors = df_dc[df_dc['ma_truong'] == school]['ten_diemchuan'].tolist()
        
        if not dc_majors:
            continue
            
        dc_clean_dict = {clean_str(name): name for name in dc_majors}
        
        for ct_name in ct_majors:
            ct_clean = clean_str(ct_name)
            matches = difflib.get_close_matches(ct_clean, list(dc_clean_dict.keys()), n=1, cutoff=0.90)
            
            if matches:
                best_match_clean = matches[0]
                best_match_orig = dc_clean_dict[best_match_clean]
                
                if ct_name != best_match_orig:
                    safe_ct_name = ct_name.replace("'", "''")
                    safe_best_match = best_match_orig.replace("'", "''")
                    update_queries.append(f"""
                        UPDATE ChiTieuTruong 
                        SET chuong_trinh_dao_tao = '{safe_best_match}'
                        WHERE ma_truong = '{school}' AND chuong_trinh_dao_tao = '{safe_ct_name}'
                    """)
                    
    if update_queries:
        with engine.begin() as conn:
            for q in update_queries:
                conn.execute(text(q))
    try:
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS MappingTenNganh"))
    except Exception as e:
        print(f"Lỗi: {e}")
if __name__ == "__main__":
    data_cleaning()

    print("Da chay xong file: 4_data_cleaning.py")
