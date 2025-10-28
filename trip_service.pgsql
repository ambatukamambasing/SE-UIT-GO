-- ===========================================================
-- DATABASE: trip_db
-- DỊCH VỤ: TripService (tách biệt với UserService)
-- ===========================================================

-- === HÀM TRIGGER cập nhật updated_at ===
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ===========================================================
-- BẢNG TRIPS
-- ===========================================================
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    passenger_id UUID NOT NULL,  -- UUID người đi (đồng bộ từ UserService)
    driver_id UUID,              -- UUID tài xế (đồng bộ từ UserService)
    vehicle_id UUID,             -- UUID xe (đồng bộ từ VehicleService)

    status VARCHAR(30) NOT NULL DEFAULT 'requested'
        CHECK (status IN ('requested', 'accepted', 'in_progress', 'completed', 'cancelled')),

    -- Địa điểm bắt đầu & kết thúc
    start_location_address TEXT NOT NULL,
    start_lat NUMERIC(10,8) NOT NULL CHECK (start_lat BETWEEN -90 AND 90),
    start_lng NUMERIC(11,8) NOT NULL CHECK (start_lng BETWEEN -180 AND 180),
    end_location_address TEXT NOT NULL,
    end_lat NUMERIC(10,8) NOT NULL CHECK (end_lat BETWEEN -90 AND 90),
    end_lng NUMERIC(11,8) NOT NULL CHECK (end_lng BETWEEN -180 AND 180),

    -- Chi tiết chuyến
    estimated_fare NUMERIC(10,2) CHECK (estimated_fare >= 0),
    final_fare NUMERIC(10,2) CHECK (final_fare >= 0),
    distance_km NUMERIC(6,2) CHECK (distance_km >= 0),
    duration_min NUMERIC(6,2) CHECK (duration_min >= 0),

    requested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_trips_updated_at
BEFORE UPDATE ON trips
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- ===========================================================
-- BẢNG BILLS
-- ===========================================================
CREATE TABLE bills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL UNIQUE,   -- FK logic sang trips (nội bộ)
    passenger_id UUID NOT NULL,     -- UUID từ UserService
    driver_id UUID NOT NULL,        -- UUID từ UserService
    amount NUMERIC(10,2) NOT NULL CHECK (amount >= 0),
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method <> ''),
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'completed', 'failed')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


-- ===========================================================
-- BẢNG TRIP_REVIEWS
-- ===========================================================
CREATE TABLE trip_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL UNIQUE,
    passenger_id UUID NOT NULL,
    driver_id UUID NOT NULL,
    rating_for_driver SMALLINT CHECK (rating_for_driver BETWEEN 1 AND 5),
    comment_for_driver TEXT,
    rating_for_passenger SMALLINT CHECK (rating_for_passenger BETWEEN 1 AND 5),
    comment_for_passenger TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


-- ===========================================================
-- QUAN HỆ NỘI BỘ TRONG TRIP_DB
-- ===========================================================
ALTER TABLE bills
ADD CONSTRAINT fk_bills_trip FOREIGN KEY (trip_id)
    REFERENCES trips(id) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE trip_reviews
ADD CONSTRAINT fk_reviews_trip FOREIGN KEY (trip_id)
    REFERENCES trips(id) ON DELETE CASCADE ON UPDATE CASCADE;


-- ===========================================================
-- INDEXES TỐI ƯU
-- ===========================================================
CREATE INDEX idx_trips_passenger_id ON trips (passenger_id);
CREATE INDEX idx_trips_driver_id ON trips (driver_id);
CREATE INDEX idx_trips_status ON trips (status);

CREATE INDEX idx_bills_trip_id ON bills (trip_id);
CREATE INDEX idx_reviews_trip_id ON trip_reviews (trip_id);
CREATE INDEX idx_reviews_driver_id ON trip_reviews (driver_id);

-- ===========================================================
-- GHI CHÚ
-- ===========================================================
-- ⚙️ TripService chỉ lưu UUID từ các service khác (User, Vehicle)
-- ⚙️ Không có FK cross-service → tránh coupling
-- ⚙️ Các service giao tiếp qua API / message queue / event bus (ví dụ: Kafka, RabbitMQ)
-- ===========================================================
