import pandas as pd
import requests 
import time
from sqlalchemy import create_engine , text
from sqlalchemy.types import NVARCHAR, INTEGER, FLOAT
from config import DB_CONNECTION_STRING, ODBC_CONNECTION_STRING
truong_dict = {
    'BKA': {'id': 302, 'slug': 'dai-hoc-bach-khoa-ha-noi-BKA'},
    'BVH': {'id': 227, 'slug': 'hoc-vien-cong-nghe-buu-chinh-vien-thong-phia-bac-BVH'},
    'DCN': {'id': 308, 'slug': 'dai-hoc-cong-nghiep-ha-noi-DCN'},
    'DKH': {'id': 328, 'slug': 'dai-hoc-duoc-ha-noi-DKH'},
    'DKK': {'id': 356, 'slug': 'dai-hoc-kinh-te-ky-thuat-cong-nghiep-DKK'},
    'FBU': {'id': 474, 'slug': 'dai-hoc-tai-chinh-ngan-hang-ha-noi-FBU'},
    'GHA': {'id': 330, 'slug': 'dai-hoc-giao-thong-van-tai-co-so-phia-bac-GHA'},
    'HBT': {'id': 224, 'slug': 'hoc-vien-bao-chi-va-tuyen-truyen-HBT'},
    'HNM': {'id': 126, 'slug': 'dai-hoc-thu-do-ha-noi-HNM'},
    'HPN': {'id': 556, 'slug': 'hoc-vien-phu-nu-viet-nam-HPN'},
    'HQT': {'id': 246, 'slug': 'hoc-vien-ngoai-giao-HQT'},
    'HTC': {'id': 258, 'slug': 'hoc-vien-tai-chinh-HTC'},
    'HVN': {'id': 562, 'slug': 'hoc-vien-nong-nghiep-viet-nam-HVN'},
    'KHA': {'id': 357, 'slug': 'dai-hoc-kinh-te-quoc-dan-KHA'},
    'KMA': {'id': 245, 'slug': 'hoc-vien-ky-thuat-mat-ma-KMA'},
    'LPH': {'id': 368, 'slug': 'dai-hoc-luat-ha-noi-LPH'},
    'NHF': {'id': 336, 'slug': 'dai-hoc-ha-noi-NHF'},
    'NHH': {'id': 247, 'slug': 'hoc-vien-ngan-hang-NHH'},
    'NTH': {'id': 382, 'slug': 'dai-hoc-ngoai-thuong-co-so-phia-bac-NTH'},
    'PKA': {'id': 423, 'slug': 'dai-hoc-phenikaa-PKA'},
    'QHE': {'id': 352, 'slug': 'dai-hoc-kinh-te-ha-noi-QHE'},
    'QHF': {'id': 380, 'slug': 'dai-hoc-ngoai-ngu-ha-noi-QHF'},
    'QHI': {'id': 311, 'slug': 'dai-hoc-cong-nghe-dai-hoc-quoc-gia-ha-noi-QHI'},
    'QHL': {'id': 266, 'slug': 'dai-hoc-luat-dai-hoc-quoc-gia-ha-noi-QHL'},
    'QHS': {'id': 533, 'slug': 'dai-hoc-giao-duc-ha-noi-QHS'},
    'QHT': {'id': 346, 'slug': 'dai-hoc-khoa-hoc-tu-nhien-dai-hoc-quoc-gia-ha-noi-QHT'},
    'QHX': {'id': 348, 'slug': 'dai-hoc-khoa-hoc-xa-hoi-va-nhan-van-ha-noi-QHX'},
    'QHY': {'id': 471, 'slug': 'dai-hoc-y-duoc-dai-hoc-quoc-gia-ha-noi-QHY'},
    'SPH': {'id': 411, 'slug': 'dai-hoc-su-pham-ha-noi-SPH'},
    'TLA': {'id': 421, 'slug': 'dai-hoc-thuy-loi-co-so-1-TLA'},
    'TMU': {'id': 426, 'slug': 'dai-hoc-thuong-mai-TMU'},
    'XDA': {'id': 443, 'slug': 'dai-hoc-xay-dung-ha-noi-XDA'},
    'YHB': {'id': 448, 'slug': 'dai-hoc-y-ha-noi-YHB'},
    'YTC': {'id': 452, 'slug': 'dai-hoc-y-te-cong-cong-YTC'},
}
years = [2025,2024,2023,2022]
data_list = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
for ma_truong, thong_tin in truong_dict.items():
    print(f"Dang lay diem chuan truong {ma_truong}...")
    for year in years:
        target_url = f"https://diemthi.tuyensinh247.com/api/common/cutoff-score?school_id={thong_tin['id']}&method_id=1&year={year}"
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(target_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    json_data = response.json()
                    if json_data.get('success') is True and 'data' in json_data:
                        for item in json_data['data']:
                            ten_nganh = item.get('name', '').strip()
                            ma_to_hop = item.get('block', '').strip()
                            diem_raw = str(item.get('mark', '')).strip()
                            if ma_to_hop == '' or ten_nganh == '':
                                continue
                            try:
                                diem = float(diem_raw)
                            except ValueError:
                                diem = None
                            data_list.append({
                                'nam_hoc': year,
                                'ma_truong': ma_truong,
                                'chuong_trinh_dao_tao': ten_nganh,
                                'ma_xet_tuyen': ma_to_hop,
                                'diem_chuan': diem
                                })
                    break
                else:
                    pass
            except Exception as e:
                time.sleep(2) 
        time.sleep(1)
df = pd.DataFrame(data_list)
if not df.empty:
    df = df.dropna(subset=['diem_chuan'])
    df = df[df['diem_chuan'] <= 30]
    df['ma_xet_tuyen'] = df['ma_xet_tuyen'].str.split(';')
    df = df.explode('ma_xet_tuyen')
    df['ma_xet_tuyen'] = df['ma_xet_tuyen'].str.strip()
    df = df[df['ma_xet_tuyen'] != '']
    df = df[df['ma_xet_tuyen'].str.len() <= 5]
    engine = create_engine(DB_CONNECTION_STRING)
    df.to_sql(name='Staging_DiemChuan', con=engine, if_exists='replace', index=False, dtype={
        'nam_hoc': INTEGER(),
        'ma_truong': NVARCHAR(50),
        'chuong_trinh_dao_tao': NVARCHAR(500),
        'ma_xet_tuyen': NVARCHAR(50),
        'diem_chuan': FLOAT()
    })
try:
    with engine.begin() as conn:
        conn.execute(text("EXEC sp_DongBo_DiemChuanTruong"))
except Exception as e:
    print(f"Lỗi: {e}")

    pass

print("Da chay xong file: 2_scrape_diemchuan.py")
