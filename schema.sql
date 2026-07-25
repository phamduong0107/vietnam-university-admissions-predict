-- 1. Bảng lưu thông tin môn học (Danh mục)
CREATE TABLE DanhMucMonHoc (
    ma_mon VARCHAR(20) PRIMARY KEY,
    ten_mon NVARCHAR(100) NOT NULL
);

-- 2. Bảng lưu dữ liệu điểm (Bảng dọc)
CREATE TABLE BangDiem (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nam_hoc INT NOT NULL,
    SOBAODANH NVARCHAR(20) NOT NULL,
    ma_mon VARCHAR(20),
    diem_so DECIMAL(4,2),
    ma_ngoai_ngu VARCHAR(20) NULL,
    FOREIGN KEY (ma_mon) REFERENCES DanhMucMonHoc(ma_mon)
);

-- Chèn mẫu môn học
INSERT INTO DanhMucMonHoc VALUES 
('TOAN', N'Toán'), ('VAN', N'Văn'), ('LY', N'Lý'), ('HOA', N'Hóa'), 
('SINH', N'Sinh'), ('TIN', N'Tin học'), ('CN_CN', N'Công nghệ công nghiệp'), 
('CN_NN', N'Công nghệ nông nghiệp'), ('SU', N'Sử'), ('DIA', N'Địa'), 
('GD_PL', N'GD Kinh tế & Pháp luật'), ('NGOAI_NGU', N'Ngoại ngữ');

-- 3. Bảng danh mục trường 
CREATE TABLE DanhMucTruong (
    ma_truong VARCHAR(20) PRIMARY KEY,
    ten_truong NVARCHAR(255) NOT NULL
);

-- 4. Bảng chỉ tiêu đào tạo
CREATE TABLE ChiTieuTruong (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nam_hoc INT NOT NULL,
    ma_truong VARCHAR(20),
    chuong_trinh_dao_tao NVARCHAR(255),
    ma_xet_tuyen VARCHAR(1000), -- Đã nới rộng để chống lỗi truncation
    chi_tieu INT,
    ty_le_chi_tieu_thpt FLOAT,
    FOREIGN KEY (ma_truong) REFERENCES DanhMucTruong(ma_truong)
);

-- 5. Bảng điểm chuẩn trường
CREATE TABLE DiemChuanTruong (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nam_hoc INT NOT NULL,
    ma_truong VARCHAR(20),
    chuong_trinh_dao_tao NVARCHAR(255),
    ma_xet_tuyen VARCHAR(1000), -- Đã nới rộng
    diem_chuan DECIMAL(4,2),
    FOREIGN KEY (ma_truong) REFERENCES DanhMucTruong(ma_truong)
);

-- 6. Bảng danh mục các tổ hợp (A00, A01, D01...)
CREATE TABLE DanhMucToHop (
    ma_to_hop VARCHAR(10) PRIMARY KEY,
    ten_to_hop NVARCHAR(100)
);

-- 7. Bảng chi tiết môn học trong từng tổ hợp
CREATE TABLE ChiTietToHop (
    ma_to_hop VARCHAR(10),
    ma_mon VARCHAR(20),
    PRIMARY KEY (ma_to_hop, ma_mon),
    FOREIGN KEY (ma_to_hop) REFERENCES DanhMucToHop(ma_to_hop),
    FOREIGN KEY (ma_mon) REFERENCES DanhMucMonHoc(ma_mon)
);

-- 8. Bảng lưu thông tin mã ngoại ngữ tương ứng với khối thi
CREATE TABLE ToHopNgoaiNgu(
    ma_to_hop VARCHAR(5),
    ma_ngoai_ngu VARCHAR(2)
);

-- 9. Các bảng đệm chứa dữ liệu thô từ CSV nạp vào
-- ĐÃ XÓA CREATE TABLE Ở ĐÂY!
-- Lý do: Tính năng "Import Flat File" của SSMS yêu cầu BẢNG CHƯA TỒN TẠI để nó tự động tạo bảng.
-- Bạn cứ dùng Import Flat File, SSMS sẽ tự sinh ra 4 bảng diem_thpt_2023, 2024, 2025, 2026 cho bạn!

-- 10. Bảng lưu kết quả tính toán tổng điểm cuối cùng phục vụ AI
CREATE TABLE KetQuaXetTuyen (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nam_hoc INT,
    SOBAODANH NVARCHAR(20),
    ma_to_hop VARCHAR(10),
    TongDiem DECIMAL(5,2),
);
GO

-- 11. Bảng Danh mục Ngành Chuẩn (Dùng để chuẩn hóa tên ngành dị biệt)
CREATE TABLE DanhMucNganhChuan (
    ma_nganh_chuan VARCHAR(50) PRIMARY KEY,
    ten_nganh_chuan NVARCHAR(255) NOT NULL
);

-- 12. Bảng Mapping Ngành (Ánh xạ tên ngành gốc sang mã ngành chuẩn)
CREATE TABLE MappingNganh (
    id INT IDENTITY(1,1) PRIMARY KEY,
    ma_truong VARCHAR(20),
    chuong_trinh_dao_tao_goc NVARCHAR(255),
    ma_nganh_chuan VARCHAR(50),
    FOREIGN KEY (ma_truong) REFERENCES DanhMucTruong(ma_truong),
    FOREIGN KEY (ma_nganh_chuan) REFERENCES DanhMucNganhChuan(ma_nganh_chuan)
);
GO

-- 13. Bảng Cache Phổ điểm (Mô phỏng cộng 0.5 điểm ưu tiên trung bình)
CREATE TABLE ThongKePhoDiem_Cache (
    Nam INT,
    Ma_To_Hop VARCHAR(10),
    Diem_Trung_Binh DECIMAL(5,2),
    So_Luong_Tren_25 INT,
    So_Luong_Tren_27 INT,
    Tong_So_Thi_Sinh INT,
    PRIMARY KEY (Nam, Ma_To_Hop)
);
GO