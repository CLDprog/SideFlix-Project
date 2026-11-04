\set ON_ERROR_STOP on
SET TIME ZONE 'UTC';
SELECT current_database() AS base, COUNT(*) AS contenus FROM public.catalog;
BEGIN;
DO $$
DECLARE previous_ts timestamptz; new_ts timestamptz;
BEGIN
    BEGIN
        INSERT INTO public.catalog VALUES ('TEST_NEG', 'Test', 'film', -1, clock_timestamp());
        RAISE EXCEPTION 'ECHEC : duree negative acceptee';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'OK : duree negative refusee';
    END;
    BEGIN
        INSERT INTO public.catalog VALUES ('A', 'Test doublon', 'film', 1, clock_timestamp());
        RAISE EXCEPTION 'ECHEC : cle primaire dupliquee acceptee';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'OK : doublon de cle primaire refuse';
    END;
    SELECT updated_at INTO STRICT previous_ts FROM public.catalog WHERE content_id='A';
    UPDATE public.catalog SET title = title || ' [TEST]' WHERE content_id='A'
        RETURNING updated_at INTO new_ts;
    IF new_ts <= previous_ts THEN RAISE EXCEPTION 'ECHEC : updated_at non actualise'; END IF;
    RAISE NOTICE 'OK : trigger updated_at actualise lors du changement de titre';
END;
$$;
ROLLBACK;
SELECT COUNT(*) AS contenus_apres_tests,
       COUNT(*) FILTER (WHERE title LIKE '%[TEST]%') AS titres_de_test_restants
FROM public.catalog;
