-- ===========================================================
-- DATABASE: driver_db
-- DỊCH VỤ: DriverService
-- Trách nhiệm: Quản lý tài xế (driver), trạng thái online/offline,
-- vị trí theo thời gian thực, và lịch sử hoạt động.
-- ===========================================================

-- === Hàm cập nhật tự động updated_at ===
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ===========================================================
-- BẢNG DRIVERS
-- ===========================================================
CREATE TABLE drivers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    license_number VARCHAR(100) UNIQUE NOT NULL,
    vehicle_type VARCHAR(50),
    rating_avg NUMERIC(3,2) DEFAULT 0 CHECK (rating_avg >= 0 AND rating_avg <= 5),
    total_trips INT DEFAULT 0 CHECK (total_trips >= 0),
    is_online BOOLEAN DEFAULT false,
    last_active TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_drivers_updated_at
BEFORE UPDATE ON drivers
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- ===========================================================
-- BẢNG DRIVER_LOCATIONS (vị trí theo thời gian thực)
-- ===========================================================
CREATE TABLE driver_locations (
    driver_id UUID PRIMARY KEY REFERENCES drivers(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    latitude NUMERIC(10,8) NOT NULL,
    longitude NUMERIC(11,8) NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_driver_locations_geo 
ON driver_locations (latitude, longitude);


-- ===========================================================
-- BẢNG DRIVER_STATUS_LOGS (lịch sử trạng thái)
-- ===========================================================
CREATE TABLE driver_status_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    driver_id UUID NOT NULL REFERENCES drivers(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    status VARCHAR(20) NOT NULL 
        CHECK (status IN ('offline', 'online', 'on_trip', 'inactive')),
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_driver_status_driver_id ON driver_status_logs(driver_id);


-- ===========================================================
-- BẢNG DRIVER_EARNINGS (doanh thu tài xế)
-- ===========================================================
CREATE TABLE driver_earnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    driver_id UUID NOT NULL REFERENCES drivers(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    trip_id UUID,
    amount NUMERIC(10,2) CHECK (amount >= 0),
    payment_method VARCHAR(50) CHECK (payment_method IN ('cash', 'momo', 'card')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_driver_earnings_driver_id ON driver_earnings(driver_id);


-- ===========================================================
-- VIEW: Tổng thu nhập mỗi tài xế
-- ===========================================================
CREATE OR REPLACE VIEW driver_total_earnings AS
SELECT 
    d.id AS driver_id,
    d.full_name,
    COALESCE(SUM(e.amount), 0) AS total_earnings
FROM drivers d
LEFT JOIN driver_earnings e ON d.id = e.driver_id
GROUP BY d.id, d.full_name;
