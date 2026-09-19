-- Sales order module of the ERP.
--
-- Principle: this database is the system of record and must always be consistent.
-- No provisional rows, no NULLs of convenience. Whatever is incomplete lives
-- outside of here, in the state of the graph suspended on its interrupt; the ERP
-- is written only once an order is valid and has a customer.
--
-- To apply it (the Postgres volume already exists, so docker-entrypoint-initdb.d
-- would not run):
--   docker compose exec -T postgres psql -U erp -d erp < db/schema.sql

BEGIN;

DROP TABLE IF EXISTS order_lines;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customer_addresses;
DROP TABLE IF EXISTS customer_emails;
DROP TABLE IF EXISTS articles;
DROP TABLE IF EXISTS customers;

-- ------------------------------------------------------------- master data

CREATE TABLE customers (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code           text NOT NULL UNIQUE,          -- ERP customer code
    name           text NOT NULL,
    vat_number     text NOT NULL UNIQUE,          -- partita IVA
    payment_terms  text NOT NULL,                 -- es. "60 gg d.f."
    created_at     timestamptz NOT NULL DEFAULT now()
);

-- One customer writes from several addresses. A separate table because it is also
-- where the system learns: when a person attaches an unknown sender to a customer,
-- a row is born here and from the next email on the match is automatic.
CREATE TABLE customer_emails (
    email        text PRIMARY KEY,
    customer_id  bigint NOT NULL REFERENCES customers (id) ON DELETE CASCADE,
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX customer_emails_customer_idx ON customer_emails (customer_id);

CREATE TABLE customer_addresses (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id  bigint NOT NULL REFERENCES customers (id) ON DELETE CASCADE,
    kind         text NOT NULL CHECK (kind IN ('headquarters', 'shipping', 'billing')),
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

-- ------------------------------------------------------------------- orders

CREATE TABLE orders (
    id                   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Traceability back to the source email. It is also the checkpointer
    -- thread_id: email, order and graph state share the same identifier.
    -- UNIQUE = idempotency is guaranteed by the database, not by the code.
    source_email_id      text NOT NULL UNIQUE,
    -- The sender as they wrote it, even when the match to the customer went
    -- through the domain or through a human decision.
    sender_email         text NOT NULL,
    -- The reference the customer uses ("Ordine 2026/0447"), when they state one.
    customer_reference   text,

    customer_id          bigint NOT NULL REFERENCES customers (id),
    shipping_address_id  bigint NOT NULL REFERENCES customer_addresses (id),

    order_date           date NOT NULL DEFAULT current_date,
    status               text NOT NULL DEFAULT 'confermato'
                         CHECK (status IN ('confermato', 'evaso', 'annullato')),
    -- Sum of the lines, frozen on the document.
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
    -- Description, unit of measure and price are COPIED from the article when the
    -- order is written, not read with a join. If the price list changes tomorrow,
    -- yesterday's orders must stay as they were placed: an order is a historical
    -- document, not a view over current data.
    description      text NOT NULL,
    unit_of_measure  text NOT NULL,
    unit_price       numeric(12, 4) NOT NULL CHECK (unit_price >= 0),

    quantity         integer NOT NULL CHECK (quantity > 0),
    -- Computed by Postgres: it cannot drift out of sync with its own operands.
    line_total       numeric(16, 4) GENERATED ALWAYS AS (quantity * unit_price) STORED,

    requested_date   date,

    UNIQUE (order_id, line_no)
);

CREATE INDEX order_lines_order_idx ON order_lines (order_id);
CREATE INDEX order_lines_article_idx ON order_lines (article_code);

-- Every email the agent has picked up, and nothing more.
--
-- The row is written once, when the dispatcher takes the email: it says "this one
-- has been seen", so the same email is never processed twice and an email that
-- dies mid-run still leaves a trace instead of an invisible orphan checkpoint.
--
-- What the graph then made of it is NOT copied here: `thread_id` is the LangGraph
-- run, and the full step-by-step state is read back with get_state_history().
-- Only `status` moves, to follow the row through its life.
CREATE TABLE inbound_mails (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    thread_id    text NOT NULL UNIQUE,

    status       text NOT NULL DEFAULT 'pending'
                 CHECK (status IN (
                     'pending', 'processing', 'interrupted', 'discarded',
                     'awaiting_review', 'completed', 'failed'
                 )),

    -- The email as it arrived, so the register still reads if the mailbox is emptied.
    sender       text NOT NULL,
    subject      text NOT NULL,
    body         text NOT NULL,
    received_at  timestamptz NOT NULL,

    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now()
);

-- The queue the web app reads.
CREATE INDEX inbound_mails_status_idx ON inbound_mails (status);

COMMIT;