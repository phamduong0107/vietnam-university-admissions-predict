# 🎓 Hệ thống AI Dự báo Điểm chuẩn Đại học 2026 (University Admission Prediction AI)

## 📌 Giới thiệu dự án (Overview)
Đây là hệ thống Học máy (Machine Learning) toàn diện được thiết kế để dự báo điểm chuẩn các ngành của các trường Đại học tại Việt Nam cho kỳ thi THPT Quốc gia năm 2026. Hệ thống không chỉ sử dụng hồi quy thống kê đơn thuần mà kết hợp phương pháp Dual-Model Ensemble Blending (Hòa trộn Mô hình Kép), khai thác đa chiều các nguồn dữ liệu: Lịch sử điểm chuẩn, Phổ điểm thực tế, Biến động chỉ tiêu, Phân cấp trường học (Tier-list), và Tín hiệu nhu cầu xã hội theo thời gian thực (Google Trends).

## 🛠️ Công nghệ cốt lõi (Tech Stack)
* **Thuật toán Học máy:** CatBoost (Xử lý tối ưu dữ liệu dạng Categorical mà không cần One-Hot Encoding).
* **Tối ưu hóa Siêu tham số:** Optuna (Bayesian Optimization).
* **Khai thác dữ liệu:** `pytrends` (Google Trends API), `tenacity` (Cơ chế Anti-Bot, Exponential Backoff, Jitter).
* **Tiền xử lý & Tính toán:** `pandas`, `numpy`, `scikit-learn`.
* **Cơ sở dữ liệu:** SQL Server (SQLAlchemy).
* **Giao diện người dùng:** Streamlit (Nằm trong file `app.py`).

## 📂 Kiến trúc Thư mục (Project Structure)
```text
📦 admission-prediction-ai
 ┣ 📂 data
 ┃ ┣ 📂 raw
 ┃ ┃ ┣ 📜 Tier list.xlsx             # Phân cấp đẳng cấp trường ĐH (Tier 1, 2, 3)
 ┃ ┃ ┗ 📜 trend_nganh_google.csv     # Dữ liệu Google Trends tải về tự động
 ┣ 📂 models
 ┃ ┗ 📜 ultimate_model.pkl           # Trọng số AI đã huấn luyện (Joblib Dump)
 ┣ 📂 results
 ┃ ┗ 📜 predictions_2026.csv         # Bảng xuất kết quả dự báo chốt hạ
 ┣ 📂 src
 ┃ ┣ 📜 data_processing.py           # Pipeline ETL, Time-shifting & Feature Engineering
 ┃ ┣ 📜 model_training.py            # Kiến trúc thuật toán, Optuna & Ensemble
 ┃ ┗ 📜 prediction.py                # Pipeline Inference cho môi trường Production
 ┣ 📜 5_get_google_trends.py         # Bot cào dữ liệu xu hướng chống chặn (Anti-bot Evasion)
 ┣ 📜 6_train_model.py               # File kích hoạt toàn bộ luồng huấn luyện
 ┣ 📜 app.py                         # Giao diện Web App (Streamlit)
 ┣ 📜 config.py                      # Lưu trữ DB_CONNECTION_STRING
 ┗ 📜 README.md
🧠 Kiến trúc Trí tuệ Nhân tạo (AI Architecture)
Dự án sử dụng cơ chế Federated Training (Huấn luyện phân cụm) kết hợp Dual-Architecture. Thay vì dùng 1 mô hình duy nhất, hệ thống chia nhỏ bài toán thành 3 khối ngành cốt lõi (G1: Kỹ thuật, G2: Xã hội, G3: Y tế) và triển khai 6 Mạng Học máy song song:

Mô hình Trực tiếp (Direct Model): Dự báo trực tiếp điểm số để bắt được Tầm nhìn Đại cục (Global Scope).

Mô hình Chênh lệch (Delta/Residual Model): Học độ dao động biến thiên (Δ) so với điểm chuẩn năm ngoái để bắt được sự nhạy cảm vi mô của Phổ điểm và Chỉ tiêu.

Bộ nội suy Tuyến tính (Linear Blending): Sử dụng thuật toán Grid-Search 1D để tìm ra Tỷ lệ vàng α nhằm hòa trộn khuyết điểm của cả 2 mô hình trên, mang lại Sai số MAE cực tiểu.

🚰 Luồng Xử lý Dữ liệu (Data Pipeline - ETL)
File data_processing.py thực thi chuỗi Pipeline gồm 6 bước khắt khe:

Làm sạch ngôn ngữ học (Text Normalization): Loại bỏ tiếng Việt có dấu, ký tự đặc biệt, regex bóc tách mã ngành.

Trích xuất Đỉnh tín hiệu (Signal Maximization): Xử lý ngành xét nhiều tổ hợp bằng cách lấy tổ hợp có lượng sinh viên thi đông nhất (đại diện độ khó chung).

Tịnh tiến Thời gian (Time-shifting): "Giáng cấp" dữ liệu hiện tại thành t-1 (Ví dụ: Biến điểm chuẩn 2025 thành thuộc tính diem_nam_ngoai cho năm 2026).

Phân rã Biến ngoại sinh (Exogenous Injection): Dán điểm Tier-list trường học và sức hút Google Trends vào ma trận học.

Khai phá Đặc trưng (Feature Engineering): Sử dụng hàm logarit tự nhiên np.log1p() để làm phẳng Tỷ lệ chọi (Tổng thí sinh / Chỉ tiêu), ép chuẩn thang 40 về thang 30 cho khối ngành Ngôn ngữ.

Lọc Dữ liệu (Train/Test Split): Tách biệt rạch ròi bằng mặt nạ mốc năm (Train < 2025, Test = 2025).

🚀 Hướng dẫn Sử dụng (How to Run)
1. Cài đặt Môi trường
Cần đảm bảo Python >= 3.9 và cài đặt các thư viện lõi:

Bash
pip install pandas numpy scikit-learn catboost optuna pytrends tenacity sqlalchemy streamlit openpyxl
Đảm bảo bạn đã cấu hình chuỗi kết nối SQL Server tại config.py.

2. Thu thập Dữ liệu Ngoại sinh (Google Trends)
Chạy kịch bản cào dữ liệu xã hội. Script đã được tích hợp bộ kháng chặn (Exponential Backoff + Random Jitter) để không bị Google cấm IP.

Bash
python 5_get_google_trends.py
Dữ liệu sẽ được lưu tại data/raw/trend_nganh_google.csv

3. Huấn luyện Mô hình & Dự báo (Training & Inference)
Kích hoạt Trình điều khiển chính. File này sẽ gọi data_processing, sau đó đánh thức model_training để Optuna tìm tham số, chốt Tỷ lệ vàng, lưu AI vào models/ultimate_model.pkl, và cuối cùng gọi prediction.py để xuất kết quả năm 2026.

Bash
python 6_train_model.py
Kết quả cuối cùng sẽ ra lò tại results/predictions_2026.csv

4. Kích hoạt Ứng dụng Web
Mở Dashboard trực quan bằng Streamlit để xem biểu đồ và tra cứu điểm dự báo cho thí sinh:

Bash
streamlit run app.py
📈 Đánh giá Hiệu năng (Evaluation)
Hệ thống sử dụng Mean Absolute Error (MAE) làm hàm mất mát (Loss Function) chuẩn, do đặc thù ngành giáo dục cần độ sai số tuyệt đối đo bằng thang điểm thực (Ví dụ: Lệch 0.5 điểm) thay vì bình phương sai số (MSE). Độ chính xác tương quan được đo lường bằng R² Score.
