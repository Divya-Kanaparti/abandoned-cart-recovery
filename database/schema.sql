CREATE DATABASE IF NOT EXISTS cart_recovery
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE cart_recovery;

CREATE TABLE IF NOT EXISTS customers (
  customer_id VARCHAR(20) PRIMARY KEY,
  first_name VARCHAR(80) NOT NULL,
  last_name VARCHAR(80) NOT NULL,
  email VARCHAR(255) NULL,
  phone VARCHAR(30) NULL,
  email_valid BOOLEAN NOT NULL DEFAULT TRUE,
  phone_valid BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL,
  UNIQUE KEY uq_customer_email (email),
  INDEX ix_customer_created (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS consents (
  consent_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id VARCHAR(20) NOT NULL,
  channel ENUM('EMAIL','SMS') NOT NULL,
  status ENUM('OPTED_IN','OPTED_OUT','UNKNOWN') NOT NULL,
  effective_at DATETIME NOT NULL,
  withdrawn_at DATETIME NULL,
  source VARCHAR(60) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_consent_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  INDEX ix_consent_latest (customer_id, channel, effective_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sessions (
  session_id VARCHAR(30) PRIMARY KEY,
  customer_id VARCHAR(20) NOT NULL,
  device_type ENUM('DESKTOP','MOBILE','TABLET') NOT NULL,
  started_at DATETIME NOT NULL,
  ended_at DATETIME NULL,
  CONSTRAINT fk_session_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  INDEX ix_session_customer (customer_id, started_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS carts (
  cart_id VARCHAR(30) PRIMARY KEY,
  customer_id VARCHAR(20) NOT NULL,
  session_id VARCHAR(30) NOT NULL,
  status ENUM('ACTIVE','ABANDONED','RECOVERY_PENDING','RECOVERED','EXPIRED','SUPPRESSED','PURCHASED') NOT NULL,
  -- status ENUM('ACTIVE','ABANDONED','RECOVERY_PENDING','RECOVERED','EXPIRED','SUPPRESSED') NOT NULL,
  currency CHAR(3) NOT NULL DEFAULT 'INR',
  cart_total DECIMAL(12,2) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL,
  last_activity_at DATETIME NOT NULL,
  abandoned_at DATETIME NULL,
  recovered_at DATETIME NULL,
  closed_at DATETIME NULL,
  CONSTRAINT fk_cart_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  CONSTRAINT fk_cart_session FOREIGN KEY (session_id) REFERENCES sessions(session_id),
  INDEX ix_cart_status_activity (status,last_activity_at),
  INDEX ix_cart_customer (customer_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cart_lines (
  cart_line_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  cart_id VARCHAR(30) NOT NULL,
  sku VARCHAR(30) NOT NULL,
  product_name VARCHAR(150) NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  updated_at DATETIME NOT NULL,
  CONSTRAINT fk_cartline_cart FOREIGN KEY (cart_id) REFERENCES carts(cart_id),
  CONSTRAINT ck_cartline_quantity CHECK (quantity > 0),
  INDEX ix_cartline_cart (cart_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS campaigns (
  campaign_id VARCHAR(30) PRIMARY KEY,
  campaign_name VARCHAR(120) NOT NULL,
  channel ENUM('EMAIL','SMS') NOT NULL,
  variant ENUM('A','B','C') NOT NULL,
  target_audience VARCHAR(120) NOT NULL,
  scheduled_at DATETIME NOT NULL,
  status ENUM('DRAFT','SCHEDULED','RUNNING','COMPLETED','CANCELLED') NOT NULL,
  created_at DATETIME NOT NULL,
  INDEX ix_campaign_schedule (scheduled_at,status)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS message_templates (
  template_id VARCHAR(40) PRIMARY KEY,
  campaign_id VARCHAR(30) NOT NULL,
  channel ENUM('EMAIL','SMS') NOT NULL,
  subject VARCHAR(200) NULL,
  body TEXT NOT NULL,
  CONSTRAINT fk_template_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS send_attempts (
  send_id VARCHAR(30) PRIMARY KEY,
  campaign_id VARCHAR(30) NOT NULL,
  template_id VARCHAR(40) NOT NULL,
  customer_id VARCHAR(20) NOT NULL,
  cart_id VARCHAR(30) NOT NULL,
  channel ENUM('EMAIL','SMS') NOT NULL,
  status ENUM('SEND_ATTEMPTED','SENT','DELIVERED','BOUNCED','OPENED','CLICKED','FAILED','SUPPRESSED') NOT NULL,
  attempted_at DATETIME NOT NULL,
  event_at DATETIME NULL,
  failure_reason VARCHAR(120) NULL,
  recovery_link VARCHAR(500) NULL,
  CONSTRAINT fk_send_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
  CONSTRAINT fk_send_template FOREIGN KEY (template_id) REFERENCES message_templates(template_id),
  CONSTRAINT fk_send_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  CONSTRAINT fk_send_cart FOREIGN KEY (cart_id) REFERENCES carts(cart_id),
  INDEX ix_send_customer_time (customer_id,attempted_at),
  INDEX ix_send_cart (cart_id),
  INDEX ix_send_campaign (campaign_id,status)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS orders (
  order_id VARCHAR(30) PRIMARY KEY,
  customer_id VARCHAR(20) NOT NULL,
  cart_id VARCHAR(30) NOT NULL,
  order_status ENUM('COMPLETED','CANCELLED','REFUNDED') NOT NULL,
  order_total DECIMAL(12,2) NOT NULL,
  ordered_at DATETIME NOT NULL,
  CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  CONSTRAINT fk_order_cart FOREIGN KEY (cart_id) REFERENCES carts(cart_id),
  UNIQUE KEY uq_order_cart (cart_id),
  INDEX ix_order_customer_time (customer_id,ordered_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_lines (
  order_line_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_id VARCHAR(30) NOT NULL,
  sku VARCHAR(30) NOT NULL,
  product_name VARCHAR(150) NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_orderline_order FOREIGN KEY (order_id) REFERENCES orders(order_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS attributions (
  attribution_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_id VARCHAR(30) NOT NULL,
  customer_id VARCHAR(20) NOT NULL,
  cart_id VARCHAR(30) NOT NULL,
  campaign_id VARCHAR(30) NOT NULL,
  send_id VARCHAR(30) NOT NULL,
  model ENUM('LAST_TOUCH_7D') NOT NULL DEFAULT 'LAST_TOUCH_7D',
  attributed_at DATETIME NOT NULL,
  attributed_revenue DECIMAL(12,2) NOT NULL,
  reason VARCHAR(255) NOT NULL,
  CONSTRAINT fk_attr_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
  CONSTRAINT fk_attr_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  CONSTRAINT fk_attr_cart FOREIGN KEY (cart_id) REFERENCES carts(cart_id),
  CONSTRAINT fk_attr_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
  CONSTRAINT fk_attr_send FOREIGN KEY (send_id) REFERENCES send_attempts(send_id),
  UNIQUE KEY uq_attribution_order (order_id),
  INDEX ix_attr_campaign (campaign_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS audit_decisions (
  decision_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id VARCHAR(20) NULL,
  cart_id VARCHAR(30) NULL,
  channel ENUM('EMAIL','SMS') NULL,
  decision ENUM('ELIGIBLE','SUPPRESSED','BLOCKED') NOT NULL,
  reason_code VARCHAR(80) NOT NULL,
  detail VARCHAR(500) NULL,
  decided_at DATETIME NOT NULL,
  INDEX ix_decision_cart (cart_id,decided_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cart_events (
  event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  cart_id VARCHAR(30) NOT NULL,
  event_type ENUM('CREATED','ITEM_ADDED','QUANTITY_UPDATED','ITEM_REMOVED','ABANDONED','RECOVERED','CLOSED') NOT NULL,
  event_at DATETIME NOT NULL,
  details JSON NULL,
  CONSTRAINT fk_cartevent_cart FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS anomaly_issues (
  issue_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  issue_type VARCHAR(80) NOT NULL,
  ground_truth VARCHAR(120) NOT NULL,
  expected_decision VARCHAR(120) NOT NULL,
  actual_decision VARCHAR(120) NOT NULL,
  affected_entity_id VARCHAR(50) NOT NULL,
  description TEXT NOT NULL,
  detected_at DATETIME NOT NULL
) ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS send_events (
    event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    send_id VARCHAR(30) NOT NULL,
    event_type ENUM(
        'SENT',
        'DELIVERED',
        'OPENED',
        'CLICKED',
        'BOUNCED'
    ) NOT NULL,
    event_at DATETIME NOT NULL,
    provider_event_id VARCHAR(100) NULL,
    event_metadata JSON NULL,

    CONSTRAINT fk_send_event_attempt
        FOREIGN KEY (send_id)
        REFERENCES send_attempts(send_id),

    UNIQUE KEY uq_provider_event (provider_event_id),

    INDEX ix_send_event_send (send_id),
    INDEX ix_send_event_type_time (event_type, event_at)
) ENGINE=InnoDB;
