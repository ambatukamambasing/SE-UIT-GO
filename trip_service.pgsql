/*
===========================================================
== DỊCH VỤ CHUYẾN ĐI (TripService)
== Database: trip_db
== Trách nhiệm: Quản lý chuyến đi, định tuyến, thanh toán, đánh giá.
===========================================================
*/

-- Trigger cập nhật updated_at
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

------------------------------------------------------------
-- BẢNG TRIPS
------------------------------------------------------------
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passenger_id UUID NOT NULL,    -- Tham chiếu đến users.id
    driver_id UUID,                -- Tham chiếu đến driver_profiles.driver_id
    vehicle_id UUID,               -- Tham chiếu đến vehicles.id
    start_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'in_progress', 'completed', 'cancelled')),
    estimated_fare NUMERIC(10,2) CHECK (estimated_fare >= 0),
    actual_fare NUMERIC(10,2) CHECK (actual_fare >= 0),
    distance_km NUMERIC(8,2) CHECK (distance_km >= 0),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (passenger_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES driver_profiles(driver_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TRIGGER trg_trips_updated_at
BEFORE UPDATE ON trips
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

------------------------------------------------------------
-- BẢNG TRIP_LOCATIONS
------------------------------------------------------------
CREATE TABLE trip_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL,
    pickup_address TEXT NOT NULL,
    pickup_lat NUMERIC(10,6),
    pickup_lng NUMERIC(10,6),
    dropoff_address TEXT,
    dropoff_lat NUMERIC(10,6),
    dropoff_lng NUMERIC(10,6),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE ON UPDATE CASCADE
);

------------------------------------------------------------
-- BẢNG TRIP_PAYMENTS
------------------------------------------------------------
CREATE TABLE trip_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL UNIQUE,
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('cash', 'credit_card', 'wallet')),
    amount NUMERIC(10,2) NOT NULL CHECK (amount >= 0),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded')),
    transaction_id VARCHAR(100) UNIQUE,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TRIGGER trg_trip_payments_updated_at
BEFORE UPDATE ON trip_payments
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

------------------------------------------------------------
-- BẢNG TRIP_RATINGS
------------------------------------------------------------
CREATE TABLE trip_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL,
    passenger_id UUID NOT NULL, -- user đánh giá tài xế
    driver_id UUID NOT NULL,    -- tài xế được đánh giá
    rating NUMERIC(2,1) CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (passenger_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES driver_profiles(driver_id) ON DELETE CASCADE ON UPDATE CASCADE
);

------------------------------------------------------------
-- INDEXES
------------------------------------------------------------
CREATE INDEX idx_trips_passenger_id ON trips (passenger_id);
CREATE INDEX idx_trips_driver_id ON trips (driver_id);
CREATE INDEX idx_trips_status ON trips (status);
CREATE INDEX idx_trip_payments_trip_id ON trip_payments (trip_id);
CREATE INDEX idx_trip_ratings_trip_id ON trip_ratings (trip_id);
CREATE INDEX idx_trip_locations_trip_id ON trip_locations (trip_id);
