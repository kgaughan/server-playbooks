CREATE TABLE domains (
    domain_id INTEGER      NOT NULL PRIMARY KEY AUTOINCREMENT,
    domain    VARCHAR(128) NOT NULL,

    CONSTRAINT unique_domain UNIQUE (domain)
);

CREATE TABLE users (
    user_id   INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
    domain_id INTEGER     NOT NULL,
    local     VARCHAR(64) NOT NULL,

    CONSTRAINT unique_email UNIQUE (domain_id, local),
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id) ON DELETE CASCADE
);

CREATE TABLE aliases (
    alias_id      INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
    src_domain_id INTEGER     NOT NULL,
    src_local     VARCHAR(64) NOT NULL,
    dest_user_id  INTEGER     NOT NULL,

    CONSTRAINT unique_alias UNIQUE (src_domain_id, src_local),
    FOREIGN KEY (src_domain_id) REFERENCES domains(domain_id) ON DELETE CASCADE,
    FOREIGN KEY (dest_user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
