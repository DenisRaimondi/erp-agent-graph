-- Test master data, consistent with the emails seeded into the mailbox.
-- Companies, VAT numbers and domains are all made up.
--
--   docker compose exec -T postgres psql -U erp -d erp < db/seed.sql
--
-- THE DATA IS INCOMPLETE ON PURPOSE: some senders and some article codes that
-- appear in the emails are not in here, so that the graph meets real
-- discrepancies instead of a perfect world.

BEGIN;

TRUNCATE order_lines, orders, customer_addresses, customer_emails, customers, articles
    RESTART IDENTITY CASCADE;

INSERT INTO customers (code, name, vat_number, payment_terms) VALUES
    ('C0001', 'ACME Forniture srl',    'IT01234567801', '30 gg d.f.'),
    ('C0002', 'Rossi Impianti Srl',    'IT01234567802', '60 gg d.f.'),
    ('C0003', 'Delta Costruzioni Spa', 'IT01234567803', '60 gg d.f. fine mese'),
    ('C0004', 'Meridiana Trading Ltd', 'GB123456789',   'bonifico anticipato');

INSERT INTO customer_emails (email, customer_id) VALUES
    ('m.bianchi@acme-forniture.example',        1),
    ('ufficio.acquisti@rossi-impianti.example', 2),
    ('g.ferraro@delta-costruzioni.example',     3),
    ('purchasing@meridiana-trading.example',    4);
    -- In the emails but NOT registered, to exercise the domain match and the
    -- person reviewing:
    --   acquisti@rossi-impianti.example        (same company, another address)
    --   s.marchetti@delta-costruzioni.example  (same company, another person)
    --   ordini@meridiana-trading.example       (same company, another address)

INSERT INTO customer_addresses
    (customer_id, kind, street, postal_code, city, province, country, is_default) VALUES
    (1, 'headquarters', 'Via delle Industrie 12', '21100', 'Varese',  'VA', 'IT', true),
    (1, 'shipping',     'Via dei Magazzini 4',    '21100', 'Varese',  'VA', 'IT', false),
    (2, 'headquarters', 'Corso Europa 88',        '20025', 'Legnano', 'MI', 'IT', true),
    (3, 'headquarters', 'Via Cantiere Nord 3',    '10121', 'Torino',  'TO', 'IT', true),
    (3, 'shipping',     'Cantiere Nord Ovest',    '10093', 'Collegno','TO', 'IT', false),
    (4, 'headquarters', '17 Harbour Road',        'M1 4WB','Manchester','MN','GB', true);

INSERT INTO articles (code, description, unit_of_measure, unit_price, stock_qty) VALUES
    ('ART-1120', 'Guarnizione DN50',  'PZ',  4.2000,  500),
    ('ART-1121', 'Guarnizione DN65',  'PZ',  5.1000,   30),
    ('ART-0087', 'Fascetta inox',     'PZ',  0.8500, 1200),
    ('ART-3300', 'Valvola a sfera',   'PZ', 38.0000,    8);
    -- Mentioned in the emails and NOT in the catalogue: ART-001, ART-77

-- Historical orders: as if the ERP had been in use before the agent existed.
-- They give the model a reference on what each customer usually buys, which
-- helps when an email is vague ("the usual gaskets") or a code is mangled.
-- source_email_id is fake here: it matches no real email.
INSERT INTO orders
    (source_email_id, sender_email, customer_reference, customer_id,
     shipping_address_id, order_date, status, total_amount) VALUES
    ('storico-0001', 'm.bianchi@acme-forniture.example',        'ODA 2026/112',
     1, 2, DATE '2026-06-14', 'evaso',      1050.0000),
    ('storico-0002', 'm.bianchi@acme-forniture.example',        'ODA 2026/140',
     1, 2, DATE '2026-07-22', 'evaso',       357.0000),
    ('storico-0003', 'ufficio.acquisti@rossi-impianti.example', 'Ordine 2026/0331',
     2, 3, DATE '2026-05-30', 'evaso',       420.0000),
    ('storico-0004', 'g.ferraro@delta-costruzioni.example',     NULL,
     3, 5, DATE '2026-08-05', 'confermato',  304.0000);

INSERT INTO order_lines
    (order_id, line_no, article_code, description, unit_of_measure, unit_price,
     quantity, requested_date) VALUES
    -- ACME: buys DN50 gaskets and clamps
    (1, 1, 'ART-1120', 'Guarnizione DN50', 'PZ',  4.2000, 200, DATE '2026-06-20'),
    (1, 2, 'ART-0087', 'Fascetta inox',    'PZ',  0.8500, 250, DATE '2026-06-20'),
    (2, 1, 'ART-1120', 'Guarnizione DN50', 'PZ',  4.2000,  85, NULL),
    -- Rossi Impianti: gaskets in both sizes
    (3, 1, 'ART-1121', 'Guarnizione DN65', 'PZ',  5.1000,  40, DATE '2026-06-10'),
    (3, 2, 'ART-1120', 'Guarnizione DN50', 'PZ',  4.2000,  50, DATE '2026-06-10'),
    -- Delta Costruzioni: valves
    (4, 1, 'ART-3300', 'Valvola a sfera',  'PZ', 38.0000,   8, DATE '2026-08-20');

COMMIT;
