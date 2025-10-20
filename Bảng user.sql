/*
===========================================================
== DỊCH VỤ USER (UserService)
== Database: user_db
== Trách nhiệm: Quản lý người dùng, tài xế, xe cộ, xác thực.
===========================================================
*/

-- === Trigger Function Dùng Chung ===
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- === BẢNG USERS ===
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL CHECK (email <> ''),
    phone_number VARCHAR(20) UNIQUE CHECK (phone_number ~ '^[0-9+\-() ]*$'),
    password_hash VARCHAR(255), -- Cho phép NULL để hỗ trợ OAuth (Google, Facebook)
    full_name VARCHAR(100) NOT NULL CHECK (full_name <> ''),
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_users_time CHECK (updated_at >= created_at)
);

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- === BẢNG ROLES ===
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL CHECK (name IN ('passenger', 'driver'))
);

INSERT INTO roles (name) VALUES ('passenger'), ('driver')
ON CONFLICT DO NOTHING;


-- === BẢNG USER_ROLES ===
CREATE TABLE user_roles (
    user_id UUID NOT NULL,
    role_id INT NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE ON UPDATE CASCADE
);


-- === BẢNG USER_AUTH_PROVIDERS ===
CREATE TABLE user_auth_providers (
    user_id UUID NOT NULL,
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('local', 'google', 'facebook')),
    provider_user_id TEXT NOT NULL CHECK (provider_user_id <> ''),
    PRIMARY KEY (user_id, provider),
    UNIQUE (provider, provider_user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);


-- === BẢNG DRIVER_PROFILES ===
CREATE TABLE driver_profiles (
    user_id UUID PRIMARY KEY,
    license_number VARCHAR(100) UNIQUE NOT NULL CHECK (license_number <> ''),
    license_expiry DATE,
    approval_status VARCHAR(20) DEFAULT 'pending'
        CHECK (approval_status IN ('pending', 'approved', 'rejected')),
    profile_photo_url VARCHAR(512),
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TRIGGER trg_driver_profiles_updated_at
BEFORE UPDATE ON driver_profiles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- === BẢNG VEHICLES ===
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    driver_user_id UUID NOT NULL,
    license_plate VARCHAR(20) UNIQUE NOT NULL CHECK (license_plate <> ''),
    model VARCHAR(100),
    color VARCHAR(50),
    year SMALLINT CHECK (year BETWEEN 1980 AND EXTRACT(YEAR FROM CURRENT_DATE) + 1),
    is_active BOOLEAN DEFAULT false,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_user_id) REFERENCES driver_profiles(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TRIGGER trg_vehicles_updated_at
BEFORE UPDATE ON vehicles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- === INDEXES UserService ===
CREATE INDEX idx_users_email_lower ON users (LOWER(email));
CREATE INDEX idx_driver_profiles_status ON driver_profiles (approval_status);
CREATE INDEX idx_vehicles_driver_user_id ON vehicles (driver_user_id);
CREATE INDEX idx_auth_providers_user_id ON user_auth_providers (user_id);

-- Mỗi tài xế chỉ có 1 xe active tại 1 thời điểm
CREATE UNIQUE INDEX idx_one_active_vehicle_per_driver
ON vehicles (driver_user_id)
WHERE (is_active = true);



/*
===========================================================
== DỊCH VỤ CHUYẾN ĐI (TripService)
== Database: trip_db
== Trách nhiệm: Quản lý chuyến đi, hóa đơn, đánh giá.
===========================================================
*/

-- === Trigger Function Dùng Chung ===
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- === BẢNG TRIPS ===
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- id-trip
    
    -- Liên kết logic sang UserService
    passenger_id UUID NOT NULL,
    driver_id UUID,
    vehicle_id UUID,
    
    status VARCHAR(30) NOT NULL DEFAULT 'requested'
        CHECK (status IN (
            'requested', 'no_driver_found', 'accepted', 'arrived',
            'in_progress', 'completed', 'cancelled_by_passenger', 'cancelled_by_driver'
        )),

    -- Thông tin vị trí
    start_location_address TEXT NOT NULL,
    start_location_lat DECIMAL(10, 8) NOT NULL CHECK (start_location_lat BETWEEN -90 AND 90),
    start_location_lon DECIMAL(11, 8) NOT NULL CHECK (start_location_lon BETWEEN -180 AND 180),
    end_location_address TEXT NOT NULL,
    end_location_lat DECIMAL(10, 8) NOT NULL CHECK (end_location_lat BETWEEN -90 AND 90),
    end_location_lon DECIMAL(11, 8) NOT NULL CHECK (end_location_lon BETWEEN -180 AND 180),

    estimated_fare DECIMAL(10, 2) CHECK (estimated_fare >= 0),
    final_fare DECIMAL(10, 2) CHECK (final_fare >= 0),

    requested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_trips_updated_at
BEFORE UPDATE ON trips
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- === BẢNG BILLS ===
CREATE TABLE bills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID UNIQUE NOT NULL,
    passenger_id UUID NOT NULL,
    driver_id UUID NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method <> ''),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE ON UPDATE CASCADE
);


-- === BẢNG TRIP_REVIEWS ===
CREATE TABLE trip_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID UNIQUE NOT NULL,
    passenger_id UUID NOT NULL,
    driver_id UUID NOT NULL,
    rating_for_driver SMALLINT CHECK (rating_for_driver BETWEEN 1 AND 5),
    comment_for_driver TEXT,
    rating_for_passenger SMALLINT CHECK (rating_for_passenger BETWEEN 1 AND 5),
    comment_for_passenger TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- === INDEXES TripService ===
CREATE INDEX idx_trips_passenger_id ON trips (passenger_id);
CREATE INDEX idx_trips_driver_id ON trips (driver_id);
CREATE INDEX idx_trips_status ON trips (status);
CREATE INDEX idx_bills_trip_id ON bills (trip_id);
CREATE INDEX idx_reviews_trip_id ON trip_reviews (trip_id);
CREATE INDEX idx_reviews_driver_id ON trip_reviews (driver_id);
