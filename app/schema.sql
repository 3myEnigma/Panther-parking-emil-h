DROP TABLE IF EXISTS permit;
DROP TABLE IF EXISTS lot;
DROP TABLE IF EXISTS vehicle;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'driver' CHECK (role IN ('driver', 'admin')),
    is_admin      INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1))
);

CREATE TABLE lot (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL UNIQUE,
    zone     TEXT    NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    occupied INTEGER NOT NULL DEFAULT 0 CHECK (occupied >= 0)
);

CREATE TABLE vehicle (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plate   TEXT    NOT NULL UNIQUE,
    make    TEXT    NOT NULL,
    model   TEXT    NOT NULL,
    color   TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE permit (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    zone       TEXT    NOT NULL,
    status     TEXT    NOT NULL DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicle(id)
);

-- Sample data so the app shows something on first run.
INSERT INTO lot (name, zone, capacity, occupied) VALUES
    ('Lot 1 - Memorial Student Center', 'Student', 220, 40),
    ('Lot 7 - Harrington Science',      'Student', 150, 120),
    ('Lot 12 - Admin Building',         'Faculty/Staff', 80, 80);
