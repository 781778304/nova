BEGIN TRANSACTION;
    CREATE TEMPORARY TABLE consoles_backup (
        created_at DATETIME,
        updated_at DATETIME,
        deleted_at DATETIME,
        deleted BOOLEAN,
        id INTEGER NOT NULL,
        instance_name VARCHAR(255),
        instance_id INTEGER NOT NULL,
        instance_uuid VARCHAR(36),
        password VARCHAR(255),
        port INTEGER,
        pool_id INTEGER,
        PRIMARY KEY (id)
    );

    INSERT INTO consoles_backup
        SELECT created_at,
               updated_at,
               deleted_at,
               deleted,
               id,
               instance_name,
               NULL,
               instance_uuid,
               password,
               port,
               pool_id
        FROM consoles;

    UPDATE consoles_backup
        SET instance_uuid=
            (SELECT id
                 FROM instances
                 WHERE consoles_backup.instance_uuid = instances.uuid
    );

    DROP TABLE consoles;

    CREATE TABLE consoles (
        created_at DATETIME,
        updated_at DATETIME,
        deleted_at DATETIME,
        deleted BOOLEAN,
        id INTEGER NOT NULL,
        instance_name VARCHAR(255),
        instance_id INTEGER NOT NULL,
        password VARCHAR(255),
        port INTEGER,
        pool_id INTEGER,
        PRIMARY KEY (id),
        FOREIGN KEY(instance_id) REFERENCES instances (id)
    );

    CREATE INDEX consoles_pool_id ON consoles(pool_id);

    INSERT INTO consoles
        SELECT created_at,
               updated_at,
               deleted_at,
               deleted,
               id,
               instance_name,
               instance_id,
               password,
               port,
               pool_id
        FROM consoles_backup;

    DROP TABLE consoles_backup;

COMMIT;