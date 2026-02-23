-- Demo data seed for marketplace (idempotent).
-- Login mode: phone + OTP only.

-- Ensure core categories exist.
INSERT INTO categories (name) VALUES
  ('Construction Materials'),
  ('Heavy Vehicles'),
  ('Transport Vehicles'),
  ('Equipment Rentals')
ON CONFLICT (name) DO NOTHING;

-- Shared hash for internal/demo records (password not used in OTP login).
-- Hash type: pbkdf2_sha256
-- $pbkdf2-sha256$29000$875Xytn7f681JoTw/j8nZA$JyzZe49YfJA2xf3GarlCK7MV6EVddE8hmn6SGG14XwM

-- Clean old email-password demo accounts and old phone-demo identities.
DELETE FROM users
WHERE email IN (
  'admin.demo@example.com',
  'user.demo@example.com',
  'supplier1.demo@example.com',
  'supplier2.demo@example.com',
  'otp.admin.919000000001@graminhub.local',
  'otp.user.919000000002@graminhub.local',
  'otp.supplier.919000000003@graminhub.local',
  'otp.supplier.919000000004@graminhub.local'
);

-- Fresh OTP demo users.
INSERT INTO users (name, email, phone, password_hash, role, created_at) VALUES
  ('Owner Demo', 'otp.admin.919000000001@graminhub.local', '919000000001', '$pbkdf2-sha256$29000$875Xytn7f681JoTw/j8nZA$JyzZe49YfJA2xf3GarlCK7MV6EVddE8hmn6SGG14XwM', 'admin', NOW()),
  ('Buyer Demo', 'otp.user.919000000002@graminhub.local', '919000000002', '$pbkdf2-sha256$29000$875Xytn7f681JoTw/j8nZA$JyzZe49YfJA2xf3GarlCK7MV6EVddE8hmn6SGG14XwM', 'user', NOW()),
  ('Supplier Demo A', 'otp.supplier.919000000003@graminhub.local', '919000000003', '$pbkdf2-sha256$29000$875Xytn7f681JoTw/j8nZA$JyzZe49YfJA2xf3GarlCK7MV6EVddE8hmn6SGG14XwM', 'supplier', NOW()),
  ('Supplier Demo B', 'otp.supplier.919000000004@graminhub.local', '919000000004', '$pbkdf2-sha256$29000$875Xytn7f681JoTw/j8nZA$JyzZe49YfJA2xf3GarlCK7MV6EVddE8hmn6SGG14XwM', 'supplier', NOW())
ON CONFLICT (email) DO UPDATE
SET name = EXCLUDED.name,
    phone = EXCLUDED.phone,
    role = EXCLUDED.role;

-- Replace old supplier profiles for demo suppliers with clean records.
DELETE FROM suppliers
WHERE user_id IN (
  SELECT id FROM users WHERE email IN (
    'otp.supplier.919000000003@graminhub.local',
    'otp.supplier.919000000004@graminhub.local'
  )
);

INSERT INTO suppliers (user_id, business_name, phone, address, approved, blocked, featured)
SELECT id, 'Nava Cement & Steel Depot', '9000000003', 'Sonbhadra Main Market', TRUE, FALSE, TRUE
FROM users
WHERE email = 'otp.supplier.919000000003@graminhub.local';

INSERT INTO suppliers (user_id, business_name, phone, address, approved, blocked, featured)
SELECT id, 'Gaon Truck & Crane Services', '9000000004', 'Chopan Transport Yard', TRUE, FALSE, FALSE
FROM users
WHERE email = 'otp.supplier.919000000004@graminhub.local';

-- Demo supplier item listings (item name mandatory; photos optional).
INSERT INTO supplier_services (
  supplier_id, category_id, item_name, item_details, item_variant,
  photo_url_1, photo_url_2, photo_url_3, price, availability
)
SELECT s.id, c.id, 'PPC Cement', 'Fresh stock for bulk orders', '50kg bag',
       'https://images.unsplash.com/photo-1590247813693-5541d1c609fd',
       'https://images.unsplash.com/photo-1519802772250-a52a9af0eacb',
       NULL, 420.00, 'in stock'
FROM suppliers s
JOIN users u ON u.id = s.user_id
JOIN categories c ON c.name = 'Construction Materials'
WHERE u.email = 'otp.supplier.919000000003@graminhub.local';

INSERT INTO supplier_services (
  supplier_id, category_id, item_name, item_details, item_variant,
  photo_url_1, photo_url_2, photo_url_3, price, availability
)
SELECT s.id, c.id, 'River Sand', 'Washed river sand for slab work', 'Per tractor trolley',
       NULL, NULL, NULL, 1800.00, 'available on request'
FROM suppliers s
JOIN users u ON u.id = s.user_id
JOIN categories c ON c.name = 'Construction Materials'
WHERE u.email = 'otp.supplier.919000000003@graminhub.local';

INSERT INTO supplier_services (
  supplier_id, category_id, item_name, item_details, item_variant,
  photo_url_1, photo_url_2, photo_url_3, price, availability
)
SELECT s.id, c.id, '12-Wheeler Truck', 'Ideal for cement and balu transport', 'Per trip',
       'https://images.unsplash.com/photo-1556122071-e404eaedb77f',
       NULL, NULL, 12000.00, 'available on request'
FROM suppliers s
JOIN users u ON u.id = s.user_id
JOIN categories c ON c.name = 'Transport Vehicles'
WHERE u.email = 'otp.supplier.919000000004@graminhub.local';

INSERT INTO supplier_services (
  supplier_id, category_id, item_name, item_details, item_variant,
  photo_url_1, photo_url_2, photo_url_3, price, availability
)
SELECT s.id, c.id, 'Hydra Crane', 'Site loading and heavy lifting', '12 ton',
       'https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc',
       'https://images.unsplash.com/photo-1489515217757-5fd1be406fef',
       NULL, 15000.00, 'book 1 day prior'
FROM suppliers s
JOIN users u ON u.id = s.user_id
JOIN categories c ON c.name = 'Heavy Vehicles'
WHERE u.email = 'otp.supplier.919000000004@graminhub.local';

-- Demo booking.
INSERT INTO bookings (user_id, supplier_id, status, description, created_at)
SELECT buyer.id, supplier.id, 'pending', 'Need 200 PPC cement bags tomorrow', NOW()
FROM users buyer
JOIN users su ON su.email = 'otp.supplier.919000000003@graminhub.local'
JOIN suppliers supplier ON supplier.user_id = su.id
WHERE buyer.email = 'otp.user.919000000002@graminhub.local'
  AND NOT EXISTS (
    SELECT 1 FROM bookings b
    WHERE b.user_id = buyer.id
      AND b.supplier_id = supplier.id
      AND b.description = 'Need 200 PPC cement bags tomorrow'
  );

-- Demo review.
INSERT INTO reviews (user_id, supplier_id, rating, comment)
SELECT buyer.id, supplier.id, 5, 'Delivery was on time and item quality was good.'
FROM users buyer
JOIN users su ON su.email = 'otp.supplier.919000000003@graminhub.local'
JOIN suppliers supplier ON supplier.user_id = su.id
WHERE buyer.email = 'otp.user.919000000002@graminhub.local'
  AND NOT EXISTS (
    SELECT 1 FROM reviews r
    WHERE r.user_id = buyer.id
      AND r.supplier_id = supplier.id
  );

-- Demo call logs.
INSERT INTO call_logs (user_id, supplier_id, timestamp)
SELECT buyer.id, supplier.id, NOW()
FROM users buyer
JOIN users su ON su.email = 'otp.supplier.919000000003@graminhub.local'
JOIN suppliers supplier ON supplier.user_id = su.id
WHERE buyer.email = 'otp.user.919000000002@graminhub.local';

INSERT INTO call_logs (user_id, supplier_id, timestamp)
SELECT buyer.id, supplier.id, NOW()
FROM users buyer
JOIN users su ON su.email = 'otp.supplier.919000000004@graminhub.local'
JOIN suppliers supplier ON supplier.user_id = su.id
WHERE buyer.email = 'otp.user.919000000002@graminhub.local';

-- Keep serial sequences aligned with current max IDs.
SELECT setval(pg_get_serial_sequence('suppliers', 'id'), COALESCE((SELECT MAX(id) FROM suppliers), 0) + 1, false);
SELECT setval(pg_get_serial_sequence('supplier_services', 'id'), COALESCE((SELECT MAX(id) FROM supplier_services), 0) + 1, false);
SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE((SELECT MAX(id) FROM users), 0) + 1, false);

-- Summary
SELECT
  (SELECT COUNT(*) FROM users) AS users_count,
  (SELECT COUNT(*) FROM suppliers) AS suppliers_count,
  (SELECT COUNT(*) FROM supplier_services) AS supplier_services_count,
  (SELECT COUNT(*) FROM bookings) AS bookings_count,
  (SELECT COUNT(*) FROM reviews) AS reviews_count,
  (SELECT COUNT(*) FROM call_logs) AS call_logs_count;
