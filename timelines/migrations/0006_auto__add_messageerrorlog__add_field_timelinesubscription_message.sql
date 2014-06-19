DROP VIEW IF EXISTS reporters;
CREATE VIEW reporters AS
    SELECT
        a.id, a.name, a.created_on,
        b.identity,
        c.village, c.facility
    FROM
        rapidsms_contact a,
        rapidsms_connection b,
        timelines_reporter c
    WHERE
        a.id = b.contact_id
        AND
        c.contact_id = a.id;

DROP VIEW IF EXISTS messages_view;
CREATE VIEW messages_view AS
SELECT
    a.id,
    b.name,
    c.identity,
    d.facility,
    d.village,
    a.date,
    a.text,
    a.direction

FROM
    messagelog_message a,
    rapidsms_contact b,
    rapidsms_connection c,
    timelines_reporter d
WHERE
    a.contact_id = b.id
    AND
    a.connection_id = c.id
    AND
    a.contact_id = d.contact_id;

DROP VIEW IF EXISTS subscriptions_view;
CREATE VIEW subscriptions_view AS
SELECT
    a.id,
    a.timeline_id,
    a.pin,
    a.created_on,
    a."start",
    a."end",
    d.facility,
    d.village,
    d.role,
    c.identity,
    b.name,
    e.text

FROM
    timelines_timelinesubscription a,
    rapidsms_contact b,
    rapidsms_connection c,
    timelines_reporter d,
    messagelog_message e

WHERE
    (a.reporter_id = d.id AND (d.contact_id = b.id))
    AND
    a.message_id = e.id
    AND
    a.connection_id = c.id;

