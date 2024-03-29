CREATE TABLE user
(
    id          VARCHAR(36) PRIMARY KEY NOT NULL,
    first_name  VARCHAR(150)            NOT NULL,
    last_name   VARCHAR(150)            NOT NULL,
    role        VARCHAR(36),
    email       VARCHAR(200) UNIQUE KEY NOT NULL,
    password    VARCHAR(200),
    mobile      VARCHAR(15),
    gender      VARCHAR(10),
    dob         DATE,
    district_id VARCHAR(36),
    org_id      VARCHAR(36),
    updated_by  VARCHAR(36)             NOT NULL,
    updated_at  DATETIME                NOT NULL,
    created_by  VARCHAR(36)             NOT NULL,
    created_at  DATETIME                NOT NULL
);

CREATE TABLE zone
(
    id         VARCHAR(36) PRIMARY KEY NOT NULL,
    name       VARCHAR(75)             NOT NULL,
    updated_by VARCHAR(36)             NOT NULL,
    updated_at DATETIME                NOT NULL,
    created_by VARCHAR(36)             NOT NULL,
    created_at DATETIME                NOT NULL,
    CONSTRAINT fk_zone_ref_updated_by FOREIGN KEY (updated_by) REFERENCES user (id) ON DELETE CASCADE,
    CONSTRAINT fk_zone_ref_created_by FOREIGN KEY (created_by) REFERENCES user (id) ON DELETE CASCADE
);

CREATE TABLE district
(
    id         VARCHAR(36) PRIMARY KEY NOT NULL,
    name       VARCHAR(75)             NOT NULL,
    zone_id    VARCHAR(36)             NOT NULL,
    updated_by VARCHAR(36)             NOT NULL,
    updated_at DATETIME                NOT NULL,
    created_by VARCHAR(36)             NOT NULL,
    created_at DATETIME                NOT NULL,
    CONSTRAINT fk_district_ref_zone_id FOREIGN KEY (zone_id) REFERENCES zone (id) ON DELETE CASCADE,
    CONSTRAINT fk_district_ref_updated_by FOREIGN KEY (updated_by) REFERENCES user (id) ON DELETE CASCADE,
    CONSTRAINT fk_district_ref_created_by FOREIGN KEY (created_by) REFERENCES user (id) ON DELETE CASCADE
);

CREATE TABLE organization
(
    id          VARCHAR(36) PRIMARY KEY NOT NULL,
    title       VARCHAR(100)            NOT NULL,
    code        VARCHAR(12) UNIQUE KEY  NOT NULL,
    org_type    VARCHAR(25)             NOT NULL,
    district_id VARCHAR(36),
    pre_registration BIGINT DEFAULT 0 NOT NULL,
    vos_completed BIGINT DEFAULT 0 NOT NULL,
    group_formation BIGINT DEFAULT 0 NOT NULL,
    idea_submissions BIGINT DEFAULT 0 NOT NULL,
    updated_by  VARCHAR(36)             NOT NULL,
    updated_at  DATETIME                NOT NULL,
    created_by  VARCHAR(36)             NOT NULL,
    created_at  DATETIME                NOT NULL,
    CONSTRAINT fk_organization_ref_district_id FOREIGN KEY (district_id) REFERENCES district (id) ON DELETE CASCADE,
    CONSTRAINT fk_organization_ref_updated_by FOREIGN KEY (updated_by) REFERENCES user (id) ON DELETE CASCADE,
    CONSTRAINT fk_organization_ref_created_by FOREIGN KEY (created_by) REFERENCES user (id) ON DELETE CASCADE
);


CREATE TABLE user_org_link
(
    id           VARCHAR(36) PRIMARY KEY NOT NULL,
    user_id      VARCHAR(36)             NOT NULL,
    org_id       VARCHAR(36)             NOT NULL,
    visited      BOOLEAN DEFAULT FALSE   NOT NULL,
    pta          VARCHAR(255),
    alumni       VARCHAR(255),
    association  VARCHAR(255),
    whatsapp     VARCHAR(255),
    participants BIGINT  DEFAULT 0,
    created_by   VARCHAR(36)             NOT NULL,
    created_at   DATETIME                NOT NULL,
    visited_at   DATETIME,
    CONSTRAINT fk_user_org_link_ref_user_id FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_org_link_ref_org_id FOREIGN KEY (org_id) REFERENCES organization (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_org_link_ref_created_by FOREIGN KEY (created_by) REFERENCES user (id) ON DELETE CASCADE
);

ALTER TABLE user
    ADD CONSTRAINT fk_user_ref_org_id FOREIGN KEY (org_id) REFERENCES organization (id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_user_ref_district_id FOREIGN KEY (district_id) REFERENCES district (id) ON DELETE CASCADE;


-- ALTER SCRIPTS 

-- 1

ALTER TABLE organization
    ADD COLUMN pre_registration BIGINT DEFAULT 0 NOT NULL AFTER district_id,
    ADD COLUMN vos_completed BIGINT DEFAULT 0 NOT NULL AFTER pre_registration,
    ADD COLUMN group_formation BIGINT DEFAULT 0 NOT NULL AFTER vos_completed,
    ADD COLUMN idea_submissions BIGINT DEFAULT 0 NOT NULL AFTER group_formation;

-- 2

ALTER TABLE user_org_link
    ADD COLUMN orientation BOOLEAN DEFAULT FALSE AFTER participants,
    ADD COLUMN is_scheduled BOOLEAN DEFAULT FALSE AFTER orientation,
    ADD COLUMN orientation_date DATETIME AFTER orientation,
    ADD COLUMN scheduled_date DATETIME AFTER orientation_date;