CREATE OR ALTER PROCEDURE sp_DongBo_DiemChuanTruong
AS
BEGIN
    -- 1. Cập nhật trường đại học mới (nếu có)
    INSERT INTO DanhMucTruong (ma_truong, ten_truong)
    SELECT DISTINCT ma_truong, ma_truong FROM Staging_DiemChuan
    WHERE ma_truong NOT IN (SELECT ma_truong FROM DanhMucTruong);

    -- 2. Xóa điểm chuẩn cũ của các năm tương ứng để không bị trùng lặp
    DELETE FROM DiemChuanTruong 
    WHERE nam_hoc IN (SELECT DISTINCT nam_hoc FROM Staging_DiemChuan);

    -- 3. Bơm điểm chuẩn mới vào
    INSERT INTO DiemChuanTruong (nam_hoc, ma_truong, chuong_trinh_dao_tao, ma_xet_tuyen, diem_chuan)
    SELECT nam_hoc, ma_truong, chuong_trinh_dao_tao, ma_xet_tuyen, diem_chuan
    FROM Staging_DiemChuan;
END;
GO

CREATE OR ALTER PROCEDURE sp_UpdateThongKePhoDiem_Cache
AS
BEGIN
    TRUNCATE TABLE ThongKePhoDiem_Cache;
    
    INSERT INTO ThongKePhoDiem_Cache (Nam, Ma_To_Hop, Diem_Trung_Binh, So_Luong_Tren_25, So_Luong_Tren_27, Tong_So_Thi_Sinh)
    SELECT 
        nam_hoc AS Nam,
        ma_to_hop AS Ma_To_Hop,
        AVG(TongDiem + 0.5) AS Diem_Trung_Binh,
        SUM(CASE WHEN (TongDiem + 0.5) >= 25 THEN 1 ELSE 0 END) AS So_Luong_Tren_25,
        SUM(CASE WHEN (TongDiem + 0.5) >= 27 THEN 1 ELSE 0 END) AS So_Luong_Tren_27,
        COUNT(SOBAODANH) AS Tong_So_Thi_Sinh
    FROM KetQuaXetTuyen
    GROUP BY nam_hoc, ma_to_hop;
END;
GO
