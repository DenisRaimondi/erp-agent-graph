-- Modulo ordini di vendita dell'ERP.
--
-- Principio: questo database e' il sistema di verita' e deve essere sempre coerente.
-- Niente righe provvisorie, niente NULL di comodo. Quello che e' incompleto vive
-- fuori di qui, nello stato del grafo sospeso sull'interrupt; nell'ERP si scrive
-- solo quando l'ordine e' valido e ha un cliente.
--
-- Applicazione (il volume Postgres esiste gia', quindi docker-entrypoint-initdb.d
-- non verrebbe eseguito):
--   docker compose exec -T postgres psql -U erp -d erp < db/schema.sql

BEGIN;

DROP TABLE IF EXISTS order_lines;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customer_addresses;
DROP TABLE IF EXISTS customer_emails;
DROP TABLE IF EXISTS articles;
DROP TABLE IF EXISTS customers;

-- ---------------------------------------------------------------- anagrafiche

CREATE TABLE customers (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code           text NOT NULL UNIQUE,          -- codice cliente dell'ERP
    name           text NOT NULL,
    vat_number     text NOT NULL UNIQUE,          -- partita IVA
    payment_terms  text NOT NULL,                 -- es. "60 gg d.f."
    created_at     timestamptz NOT NULL DEFAULT now()
);

-- Un cliente scrive da piu' indirizzi. Tabella separata perche' e' anche il posto
-- dove il sistema impara: quando l'umano associa un mittente sconosciuto a un
-- cliente, qui nasce una riga e dal giro dopo l'aggancio e' automatico.
CREATE TABLE customer_emails (
    email        text PRIMARY KEY,
    customer_id  bigint NOT NULL REFERENCES customers (id) ON DELETE CASCADE,
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX customer_emails_customer_idx ON customer_emails (customer_id);

CREATE TABLE customer_addresses (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id  bigint NOT NULL REFERENCES customers (id) ON DELETE CASCADE,
    kind         text NOT NULL CHECK (kind IN ('sede', 'spedizione', 'fatturazione')),
    street       text NOT NULL,
    postal_code  text NOT NULL,
    city         text NOT NULL,
    province     text NOT NULL,
    country      text NOT NULL DEFAULT 'IT',
    is_default   boolean NOT NULL DEFAULT false
);

CREATE INDEX customer_addresses_customer_idx ON customer_addresses (customer_id);

CREATE TABLE articles (
    code             text PRIMARY KEY,
    description      text NOT NULL,
    unit_of_measure  text NOT NULL DEFAULT 'PZ',
    unit_price       numeric(12, 4) NOT NULL CHECK (unit_price >= 0),
    stock_qty        integer NOT NULL DEFAULT 0
);

-- --------------------------------------------------------------------- ordini

CREATE TABLE orders (
    id                   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Tracciabilita' verso la mail di origine. E' anche il thread_id del
    -- checkpointer: mail, ordine e stato del grafo condividono l'identificatore.
    -- UNIQUE = l'idempotenza la garantisce il database, non il codice.
    source_email_id      text NOT NULL UNIQUE,
    -- Il mittente come l'ha scritto lui, anche quando l'aggancio al cliente
    -- e' passato dal dominio o da una decisione umana.
    sender_email         text NOT NULL,
    -- Il riferimento che usa il cliente ("Ordine 2026/0447"), se l'ha indicato.
    customer_reference   text,

    customer_id          bigint NOT NULL REFERENCES customers (id),
    shipping_address_id  bigint NOT NULL REFERENCES customer_addresses (id),

    order_date           date NOT NULL DEFAULT current_date,
    status               text NOT NULL DEFAULT 'confermato'
                         CHECK (status IN ('confermato', 'evaso', 'annullato')),
    -- Somma delle righe, congelata sul documento.
    total_amount         numeric(14, 4) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    created_at           timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX orders_customer_idx ON orders (customer_id);
CREATE INDEX orders_status_idx ON orders (status);

CREATE TABLE order_lines (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id         bigint NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    line_no          integer NOT NULL CHECK (line_no > 0),

    article_code     text NOT NULL REFERENCES articles (code),
    -- Descrizione, unita' di misura e prezzo sono COPIATI dall'articolo al
    -- momento dell'ordine, non letti con una join. Se domani cambia il listino,
    -- gli ordini di ieri devono restare come sono stati fatti: un ordine e' un
    -- documento storico, non una vista sui dati correnti.
    description      text NOT NULL,
    unit_of_measure  text NOT NULL,
    unit_price       numeric(12, 4) NOT NULL CHECK (unit_price >= 0),

    quantity         integer NOT NULL CHECK (quantity > 0),
    -- Calcolata da Postgres: non puo' andare fuori sincrono con i suoi addendi.
    line_total       numeric(16, 4) GENERATED ALWAYS AS (quantity * unit_price) STORED,

    requested_date   date,

    UNIQUE (order_id, line_no)
);

CREATE INDEX order_lines_order_idx ON order_lines (order_id);
CREATE INDEX order_lines_article_idx ON order_lines (article_code);

COMMIT;
