print("Bat dau train model...")
import warnings
warnings.filterwarnings('ignore')

from src.data_processing import load_and_preprocess_data
from src.model_training import train_all_groups
from src.prediction import predict_2026

# 1. Tải và tiền xử lý dữ liệu
print("Dang tai va tien xu ly du lieu...")
df_full, X_train_raw, X_test_raw, df_chitieu_agg = load_and_preprocess_data()

# 2. Huấn luyện mô hình
print("Tien hanh huan luyen mo hinh (Optuna + CatBoost)...")
ultimate_brain = train_all_groups(df_full, X_train_raw, X_test_raw)

# 3. Dự đoán điểm chuẩn 2026
print("Dang du doan diem cho nam 2026...")
predict_2026(X_test_raw, df_chitieu_agg, ultimate_brain)

print("Da chay xong file: 6_train_model.py")
