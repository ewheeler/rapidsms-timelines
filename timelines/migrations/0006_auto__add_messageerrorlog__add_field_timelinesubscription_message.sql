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
    a.reporter_id,
    b.id as contact_id,
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

CREATE OR REPLACE FUNCTION timeline_subscriptions(contactid int, timeline text)
RETURNS INT AS $delim$
    DECLARE
    subs INT;
    tline INT;
    BEGIN
        SELECT id INTO tline FROM timelines_timeline WHERE name = timeline;
        IF NOT FOUND THEN
            RETURN 0;
        END IF;
        SELECT count(*) INTO subs FROM subscriptions_view
            WHERE contact_id = contactid AND timeline_id = tline;
        IF NOT FOUND THEN
            RETURN 0;
        END IF;
        RETURN subs;
    END;
$delim$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION no_of_confirmed_visits(contactid int)
RETURNS INT AS $delim$
    DECLARE
    cvisits INT;
    BEGIN
        SELECT count(*) INTO cvisits FROM timelines_occurrence
        WHERE subscription_id
            IN (SELECT id FROM subscriptions_view WHERE contact_id = contactid);
    IF NOT FOUND THEN
        RETURN 0;
    END IF;

    RETURN cvisits;
    END;
$delim$ LANGUAGE 'plpgsql';

DROP VIEW IF EXISTS performance_view;
CREATE VIEW performance_view AS
    SELECT
        *, timeline_subscriptions(id, 'ANC/PNC Advice') as advice_subs,
        timeline_subscriptions(id, 'New pregancy/Antenatal Care Visits') as preg_subs,
        timeline_subscriptions(id, 'New Birth/Postnatal Care Visits') as birth_subs ,
        no_of_confirmed_visits(id) as cvisits
    FROM
        reporters;
