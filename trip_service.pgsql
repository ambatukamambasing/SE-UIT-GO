/*
===========================================================
== DỊCH VỤ NGƯỜI DÙNG (UserService)
== Database: user_db
== Trách nhiệm: Quản lý hành khách, tài xế, xe, xác thực.
===========================================================
*/

-- === Trigger cập nhật cột updated_at ===
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
    password_hash VARCHAR(255),
    full_name VARCHAR(100) NOT NULL CHECK (full_name <> ''),
    role VARCHAR(20) NOT NULL DEFAULT 'passenger'
        CHECK (role IN ('passenger', 'driver', 'admin')),
    is_verified BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_users_time CHECK (updated_at >= created_at)
);

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- === BẢNG DRIVER_PROFILES ===
CREATE TABLE driver_profiles (
    driver_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- định danh tài xế (sẽ trùng logic với trips.driver_id)
    user_id UUID NOT NULL UNIQUE, -- liên kết user gốc
    license_number VARCHAR(100) UNIQUE NOT NULL CHECK (license_number <> ''),
    license_expiry DATE,
    approval_status VARCHAR(20) DEFAULT 'pending'
        CHECK (approval_status IN ('pending', 'approved', 'rejected')),
    rating_avg NUMERIC(3,2) DEFAULT 0.0 CHECK (rating_avg >= 0 AND rating_avg <= 5),
    total_trips INT DEFAULT 0 CHECK (total_trips >= 0),
    profile_photo_url VARCHAR(512),
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
    driver_id UUID NOT NULL, -- FK logic (tham chiếu driver_profiles.driver_id)
    license_plate VARCHAR(20) UNIQUE NOT NULL CHECK (license_plate <> ''),
    model VARCHAR(100),
    color VARCHAR(50),
    year SMALLINT CHECK (year BETWEEN 1980 AND EXTRACT(YEAR FROM CURRENT_DATE) + 1),
    is_active BOOLEAN DEFAULT false,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES driver_profiles(driver_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TRIGGER trg_vehicles_updated_at
BEFORE UPDATE ON vehicles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- === BẢNG AUTH_PROVIDERS (OAuth) ===
CREATE TABLE user_auth_providers (
    user_id UUID NOT NULL,
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('local', 'google', 'facebook')),
    provider_user_id TEXT NOT NULL CHECK (provider_user_id <> ''),
    PRIMARY KEY (user_id, provider),
    UNIQUE (provider, provider_user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- === INDEXES ===
CREATE INDEX idx_users_email_lower ON users (LOWER(email));
CREATE INDEX idx_driver_profiles_status ON driver_profiles (approval_status);
CREATE INDEX idx_driver_profiles_user_id ON driver_profiles (user_id);
CREATE INDEX idx_vehicles_driver_id ON vehicles (driver_id);
CREATE UNIQUE INDEX idx_one_active_vehicle_per_driver
ON vehicles (driver_id)
WHERE (is_active = true);
