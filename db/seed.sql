-- Anagrafiche di prova, coerenti con le mail generate dal seed della casella.
-- Aziende, partite IVA e domini sono inventati.
--
--   docker compose exec -T postgres psql -U erp -d erp < db/seed.sql
--
-- IL CENSIMENTO E' INCOMPLETO DI PROPOSITO: alcuni mittenti e alcuni codici
-- articolo presenti nelle mail non stanno qui dentro, cosi' il grafo incontra
-- discrepanze vere invece che un mondo perfetto.

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
    -- Presenti nelle mail e NON censiti, per far lavorare l'aggancio per dominio
    -- e l'umano:
    --   acquisti@rossi-impianti.example        (stessa azienda, altro indirizzo)
    --   s.marchetti@delta-costruzioni.example  (stessa azienda, altra persona)
    --   ordini@meridiana-trading.example       (stessa azienda, altro indirizzo)

INSERT INTO customer_addresses
    (customer_id, kind, street, postal_code, city, province, country, is_default) VALUES
    (1, 'sede',        'Via delle Industrie 12', '21100', 'Varese',  'VA', 'IT', true),
    (1, 'spedizione',  'Via dei Magazzini 4',    '21100', 'Varese',  'VA', 'IT', false),
    (2, 'sede',        'Corso Europa 88',        '20025', 'Legnano', 'MI', 'IT', true),
    (3, 'sede',        'Via Cantiere Nord 3',    '10121', 'Torino',  'TO', 'IT', true),
    (3, 'spedizione',  'Cantiere Nord Ovest',    '10093', 'Collegno','TO', 'IT', false),
    (4, 'sede',        '17 Harbour Road',        'M1 4WB','Manchester','MN','GB', true);

INSERT INTO articles (code, description, unit_of_measure, unit_price, stock_qty) VALUES
    ('ART-1120', 'Guarnizione DN50',  'PZ',  4.2000,  500),
    ('ART-1121', 'Guarnizione DN65',  'PZ',  5.1000,   30),
    ('ART-0087', 'Fascetta inox',     'PZ',  0.8500, 1200),
    ('ART-3300', 'Valvola a sfera',   'PZ', 38.0000,    8);
    -- Citati nelle mail e NON a catalogo: ART-001, ART-77

COMMIT;
