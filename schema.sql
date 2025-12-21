-- schema.sql
-- Database schema for The Voyager application
-- MySQL DDL with InnoDB engine for foreign key support

-- Drop tables in reverse dependency order if they exist
-- This allows the script to be re-run cleanly
DROP TABLE IF EXISTS itinerary_days;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS users;

-- Users table
-- Stores user account information with hashed passwords
CREATE TABLE users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Trips table
-- Stores trip itineraries created by users
-- Each trip belongs to exactly one user
CREATE TABLE trips (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    title VARCHAR(100) NOT NULL,
    num_days INT NOT NULL,
    preferences TEXT,
    INDEX idx_user_id (user_id),
    CONSTRAINT fk_trips_user
        FOREIGN KEY (user_id) 
        REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Itinerary Days table
-- Stores the detailed itinerary content for each day of each trip
-- Each day belongs to exactly one trip
CREATE TABLE itinerary_days (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    trip_id INT UNSIGNED NOT NULL,
    day_number INT NOT NULL,
    content TEXT NOT NULL,
    UNIQUE INDEX idx_trip_day (trip_id, day_number),
    CONSTRAINT fk_days_trip
        FOREIGN KEY (trip_id)
        REFERENCES trips(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;