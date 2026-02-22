-- Demo data seed for marketplace (idempotent).

-- Ensure core categories exist.
INSERT INTO categories (name) VALUES
  ('Construction Materials'),
  ('Heavy Vehicles'),
  ('Transport Vehicles'),
  ('Equipment Rentals')
ON CONFLICT (name) DO NOTHING;

-- Password for all demo users: demo123
-- Hash type: pbkdf2_sha256 (compatible with app fallback verifier)
-- $pbkdf2-sha256$29000$875Xytn7f681JoTw/j8nZA$JyzZe49YfJA2xf3GarlCK7MV6EVddE8hmn6SGG14XwM
INSERT INTO users (name, email, password_hash, role, created_at) VALUES
  ('Demo Admin', 'admin.demo@example.com', '$pbkdf2-sha256$29000$875Xytn7f681JoTw/j8nZA$JyzZe49YfJA2xf3GarlCK7MV6EVddE8hmn6SGG14XwM', 'admin', NOW()),
  ('Demo User', 'user.demo@example.com', '$pbkdf2-sha256$29000$875Xytn7f681JoTw/j8nZA$JyzZe49YfJA2xf3GarlCK7MV6EVddE8hmn6SGG14XwM', 'user', NOW()),
  ('Demo Supplier One', 'supplier1.demo@example.com', '$pbkdf2-sha256$29000$875Xytn7f681JoTw/j8nZA$JyzZe49YfJA2xf3GarlCK7MV6EVddE8hmn6SGG14XwM', 'supplier', NOW()),
  ('Demo Supplier Two', 'supplier2.demo@example.com', '$pbkdf2-sha256$29000$875Xytn7f681JoTw/j8nZA$JyzZe49YfJA2xf3GarlCK7MV6EVddE8hmn6SGG14XwM', 'supplier', NOW())
ON CONFLICT (email) DO UPDATE
SET name = EXCLUDED.name,
    role = EXCLUDED.role;

-- Supplier profiles.
-- Update latest profile for demo supplier if it exists; otherwise insert a new row.
WITH supplier_user AS (
  SELECT u.id AS user_id FROM users u WHERE u.email = 'supplier1.demo@example.com'
), latest AS (
  SELECT s.id
  FROM suppliers s
  JOIN supplier_user su ON su.user_id = s.user_id
  ORDER BY s.id DESC
  LIMIT 1
), updated AS (
  UPDATE suppliers s
  SET business_name = 'Demo Steel Hub',
      phone = '9000000001',
      address = 'Noida Sector 63',
      approved = TRUE,
      featured = TRUE
  WHERE s.id IN (SELECT id FROM latest)
  RETURNING s.id
)
INSERT INTO suppliers (user_id, business_name, phone, address, approved, featured)
SELECT su.user_id, 'Demo Steel Hub', '9000000001', 'Noida Sector 63', TRUE, TRUE
FROM supplier_user su
WHERE NOT EXISTS (SELECT 1 FROM updated);

WITH supplier_user AS (
  SELECT u.id AS user_id FROM users u WHERE u.email = 'supplier2.demo@example.com'
), latest AS (
  SELECT s.id
  FROM suppliers s
  JOIN supplier_user su ON su.user_id = s.user_id
  ORDER BY s.id DESC
  LIMIT 1
), updated AS (
  UPDATE suppliers s
  SET business_name = 'Demo Crane Rentals',
      phone = '9000000002',
      address = 'Gurugram Industrial Zone',
      approved = TRUE,
      featured = FALSE
  WHERE s.id IN (SELECT id FROM latest)
  RETURNING s.id
)
INSERT INTO suppliers (user_id, business_name, phone, address, approved, featured)
SELECT su.user_id, 'Demo Crane Rentals', '9000000002', 'Gurugram Industrial Zone', TRUE, FALSE
FROM supplier_user su
WHERE NOT EXISTS (SELECT 1 FROM updated);

-- Supplier services.
INSERT INTO supplier_services (supplier_id, category_id, price, availability)
SELECT s.id, c.id, 1500.00, 'in stock'
FROM suppliers s
JOIN users u ON u.id = s.user_id
JOIN categories c ON c.name = 'Construction Materials'
WHERE u.email = 'supplier1.demo@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM supplier_services ss
    WHERE ss.supplier_id = s.id AND ss.category_id = c.id
  );

INSERT INTO supplier_services (supplier_id, category_id, price, availability)
SELECT s.id, c.id, 12000.00, 'available on request'
FROM suppliers s
JOIN users u ON u.id = s.user_id
JOIN categories c ON c.name = 'Heavy Vehicles'
WHERE u.email = 'supplier2.demo@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM supplier_services ss
    WHERE ss.supplier_id = s.id AND ss.category_id = c.id
  );

-- Demo bookings.
INSERT INTO bookings (user_id, supplier_id, status, description, created_at)
SELECT u.id, s.id, 'pending', 'Need 100 bags of cement for site A', NOW()
FROM users u
JOIN suppliers s ON TRUE
JOIN users su ON su.id = s.user_id
WHERE u.email = 'user.demo@example.com'
  AND su.email = 'supplier1.demo@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM bookings b
    WHERE b.user_id = u.id
      AND b.supplier_id = s.id
      AND b.description = 'Need 100 bags of cement for site A'
  );

INSERT INTO bookings (user_id, supplier_id, status, description, created_at)
SELECT u.id, s.id, 'pending', 'Require 2 cranes for 3 days', NOW()
FROM users u
JOIN suppliers s ON TRUE
JOIN users su ON su.id = s.user_id
WHERE u.email = 'user.demo@example.com'
  AND su.email = 'supplier2.demo@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM bookings b
    WHERE b.user_id = u.id
      AND b.supplier_id = s.id
      AND b.description = 'Require 2 cranes for 3 days'
  );

-- Demo review.
INSERT INTO reviews (user_id, supplier_id, rating, comment)
SELECT u.id, s.id, 5, 'Quick response and fair pricing.'
FROM users u
JOIN suppliers s ON TRUE
JOIN users su ON su.id = s.user_id
WHERE u.email = 'user.demo@example.com'
  AND su.email = 'supplier1.demo@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM reviews r
    WHERE r.user_id = u.id
      AND r.supplier_id = s.id
  );

-- Demo call logs.
INSERT INTO call_logs (user_id, supplier_id, timestamp)
SELECT u.id, s.id, NOW()
FROM users u
JOIN suppliers s ON TRUE
JOIN users su ON su.id = s.user_id
WHERE u.email = 'user.demo@example.com'
  AND su.email = 'supplier1.demo@example.com';

INSERT INTO call_logs (user_id, supplier_id, timestamp)
SELECT u.id, s.id, NOW()
FROM users u
JOIN suppliers s ON TRUE
JOIN users su ON su.id = s.user_id
WHERE u.email = 'user.demo@example.com'
  AND su.email = 'supplier2.demo@example.com';

-- Keep serial sequences aligned with current max IDs.
SELECT setval(pg_get_serial_sequence('suppliers', 'id'), COALESCE((SELECT MAX(id) FROM suppliers), 0) + 1, false);
SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE((SELECT MAX(id) FROM users), 0) + 1, false);

-- Summary
SELECT
  (SELECT COUNT(*) FROM users) AS users_count,
  (SELECT COUNT(*) FROM suppliers) AS suppliers_count,
  (SELECT COUNT(*) FROM supplier_services) AS supplier_services_count,
  (SELECT COUNT(*) FROM bookings) AS bookings_count,
  (SELECT COUNT(*) FROM reviews) AS reviews_count,
  (SELECT COUNT(*) FROM call_logs) AS call_logs_count;
