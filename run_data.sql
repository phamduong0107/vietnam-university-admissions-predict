TRUNCATE TABLE KetQuaXetTuyen;
GO

INSERT INTO KetQuaXetTuyen (nam_hoc, SOBAODANH, ma_to_hop, TongDiem)
SELECT S.nam_hoc, S.SOBAODANH, C.ma_to_hop, C.TongDiem
FROM Staging_BangDiem S
CROSS APPLY (
    SELECT 'A00' AS ma_to_hop, (Hoa + Li + Toan) AS TongDiem WHERE Hoa IS NOT NULL AND Li IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'A01' AS ma_to_hop, (Li + Ngoai_ngu + Toan) AS TongDiem WHERE Li IS NOT NULL AND Ngoai_ngu IS NOT NULL AND Toan IS NOT NULL AND (Ma_ngoai_ngu = 'N1' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'A02' AS ma_to_hop, (Li + Sinh + Toan) AS TongDiem WHERE Li IS NOT NULL AND Sinh IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'A03' AS ma_to_hop, (Li + Su + Toan) AS TongDiem WHERE Li IS NOT NULL AND Su IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'A04' AS ma_to_hop, (Dia + Li + Toan) AS TongDiem WHERE Dia IS NOT NULL AND Li IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'A05' AS ma_to_hop, (Hoa + Su + Toan) AS TongDiem WHERE Hoa IS NOT NULL AND Su IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'A06' AS ma_to_hop, (Dia + Hoa + Toan) AS TongDiem WHERE Dia IS NOT NULL AND Hoa IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'A07' AS ma_to_hop, (Dia + Su + Toan) AS TongDiem WHERE Dia IS NOT NULL AND Su IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'A08' AS ma_to_hop, (GD_KT_PL + Su + Toan) AS TongDiem WHERE GD_KT_PL IS NOT NULL AND Su IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'A09' AS ma_to_hop, (Dia + GD_KT_PL + Toan) AS TongDiem WHERE Dia IS NOT NULL AND GD_KT_PL IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'A10' AS ma_to_hop, (GD_KT_PL + Li + Toan) AS TongDiem WHERE GD_KT_PL IS NOT NULL AND Li IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'A11' AS ma_to_hop, (GD_KT_PL + Hoa + Toan) AS TongDiem WHERE GD_KT_PL IS NOT NULL AND Hoa IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'B00' AS ma_to_hop, (Hoa + Sinh + Toan) AS TongDiem WHERE Hoa IS NOT NULL AND Sinh IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'B01' AS ma_to_hop, (Sinh + Su + Toan) AS TongDiem WHERE Sinh IS NOT NULL AND Su IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'B02' AS ma_to_hop, (Dia + Sinh + Toan) AS TongDiem WHERE Dia IS NOT NULL AND Sinh IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'B03' AS ma_to_hop, (Sinh + Toan + Van) AS TongDiem WHERE Sinh IS NOT NULL AND Toan IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'B04' AS ma_to_hop, (GD_KT_PL + Sinh + Toan) AS TongDiem WHERE GD_KT_PL IS NOT NULL AND Sinh IS NOT NULL AND Toan IS NOT NULL
    UNION ALL
    SELECT 'B08' AS ma_to_hop, (Ngoai_ngu + Sinh + Toan) AS TongDiem WHERE Ngoai_ngu IS NOT NULL AND Sinh IS NOT NULL AND Toan IS NOT NULL AND (Ma_ngoai_ngu = 'N1' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'C00' AS ma_to_hop, (Dia + Su + Van) AS TongDiem WHERE Dia IS NOT NULL AND Su IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C01' AS ma_to_hop, (Li + Toan + Van) AS TongDiem WHERE Li IS NOT NULL AND Toan IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C02' AS ma_to_hop, (Hoa + Toan + Van) AS TongDiem WHERE Hoa IS NOT NULL AND Toan IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C03' AS ma_to_hop, (Su + Toan + Van) AS TongDiem WHERE Su IS NOT NULL AND Toan IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C04' AS ma_to_hop, (Dia + Toan + Van) AS TongDiem WHERE Dia IS NOT NULL AND Toan IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C05' AS ma_to_hop, (Hoa + Li + Van) AS TongDiem WHERE Hoa IS NOT NULL AND Li IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C06' AS ma_to_hop, (Li + Sinh + Van) AS TongDiem WHERE Li IS NOT NULL AND Sinh IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C07' AS ma_to_hop, (Li + Su + Van) AS TongDiem WHERE Li IS NOT NULL AND Su IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C08' AS ma_to_hop, (Hoa + Sinh + Van) AS TongDiem WHERE Hoa IS NOT NULL AND Sinh IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C09' AS ma_to_hop, (Dia + Li + Van) AS TongDiem WHERE Dia IS NOT NULL AND Li IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C10' AS ma_to_hop, (Hoa + Su + Van) AS TongDiem WHERE Hoa IS NOT NULL AND Su IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C12' AS ma_to_hop, (Sinh + Su + Van) AS TongDiem WHERE Sinh IS NOT NULL AND Su IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C14' AS ma_to_hop, (GD_KT_PL + Toan + Van) AS TongDiem WHERE GD_KT_PL IS NOT NULL AND Toan IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C19' AS ma_to_hop, (GD_KT_PL + Su + Van) AS TongDiem WHERE GD_KT_PL IS NOT NULL AND Su IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'C20' AS ma_to_hop, (Dia + GD_KT_PL + Van) AS TongDiem WHERE Dia IS NOT NULL AND GD_KT_PL IS NOT NULL AND Van IS NOT NULL
    UNION ALL
    SELECT 'D01' AS ma_to_hop, (Ngoai_ngu + Toan + Van) AS TongDiem WHERE Ngoai_ngu IS NOT NULL AND Toan IS NOT NULL AND Van IS NOT NULL AND (Ma_ngoai_ngu = 'N1' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D02' AS ma_to_hop, (Ngoai_ngu + Toan + Van) AS TongDiem WHERE Ngoai_ngu IS NOT NULL AND Toan IS NOT NULL AND Van IS NOT NULL AND (Ma_ngoai_ngu = 'N2' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D03' AS ma_to_hop, (Ngoai_ngu + Toan + Van) AS TongDiem WHERE Ngoai_ngu IS NOT NULL AND Toan IS NOT NULL AND Van IS NOT NULL AND (Ma_ngoai_ngu = 'N3' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D04' AS ma_to_hop, (Ngoai_ngu + Toan + Van) AS TongDiem WHERE Ngoai_ngu IS NOT NULL AND Toan IS NOT NULL AND Van IS NOT NULL AND (Ma_ngoai_ngu = 'N4' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D05' AS ma_to_hop, (Ngoai_ngu + Toan + Van) AS TongDiem WHERE Ngoai_ngu IS NOT NULL AND Toan IS NOT NULL AND Van IS NOT NULL AND (Ma_ngoai_ngu = 'N5' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D06' AS ma_to_hop, (Ngoai_ngu + Toan + Van) AS TongDiem WHERE Ngoai_ngu IS NOT NULL AND Toan IS NOT NULL AND Van IS NOT NULL AND (Ma_ngoai_ngu = 'N6' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D07' AS ma_to_hop, (Hoa + Ngoai_ngu + Toan) AS TongDiem WHERE Hoa IS NOT NULL AND Ngoai_ngu IS NOT NULL AND Toan IS NOT NULL AND (Ma_ngoai_ngu = 'N1' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D08' AS ma_to_hop, (Ngoai_ngu + Sinh + Toan) AS TongDiem WHERE Ngoai_ngu IS NOT NULL AND Sinh IS NOT NULL AND Toan IS NOT NULL AND (Ma_ngoai_ngu = 'N1' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D09' AS ma_to_hop, (Ngoai_ngu + Su + Toan) AS TongDiem WHERE Ngoai_ngu IS NOT NULL AND Su IS NOT NULL AND Toan IS NOT NULL AND (Ma_ngoai_ngu = 'N1' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D10' AS ma_to_hop, (Dia + Ngoai_ngu + Toan) AS TongDiem WHERE Dia IS NOT NULL AND Ngoai_ngu IS NOT NULL AND Toan IS NOT NULL AND (Ma_ngoai_ngu = 'N1' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D11' AS ma_to_hop, (Li + Ngoai_ngu + Van) AS TongDiem WHERE Li IS NOT NULL AND Ngoai_ngu IS NOT NULL AND Van IS NOT NULL AND (Ma_ngoai_ngu = 'N1' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D12' AS ma_to_hop, (Hoa + Ngoai_ngu + Van) AS TongDiem WHERE Hoa IS NOT NULL AND Ngoai_ngu IS NOT NULL AND Van IS NOT NULL AND (Ma_ngoai_ngu = 'N1' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D13' AS ma_to_hop, (Ngoai_ngu + Sinh + Van) AS TongDiem WHERE Ngoai_ngu IS NOT NULL AND Sinh IS NOT NULL AND Van IS NOT NULL AND (Ma_ngoai_ngu = 'N1' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D14' AS ma_to_hop, (Ngoai_ngu + Su + Van) AS TongDiem WHERE Ngoai_ngu IS NOT NULL AND Su IS NOT NULL AND Van IS NOT NULL AND (Ma_ngoai_ngu = 'N1' OR Ma_ngoai_ngu IS NULL)
    UNION ALL
    SELECT 'D15' AS ma_to_hop, (Dia + Ngoai_ngu + Van) AS TongDiem WHERE Dia IS NOT NULL AND Ngoai_ngu IS NOT NULL AND Van IS NOT NULL AND (Ma_ngoai_ngu = 'N1' OR Ma_ngoai_ngu IS NULL)
) C;
GO

EXEC sp_UpdateThongKePhoDiem_Cache;
GO
