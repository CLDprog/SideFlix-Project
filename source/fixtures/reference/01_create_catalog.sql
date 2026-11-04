-- Sideflix : adaptation de 01_create_merch_db.sql (TD 2).
-- Donnees fictives. Executer dans la base sideflix uniquement.
-- Aucun DROP : conserver les TD et les autres bases.
\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE IF NOT EXISTS public.catalog (
    content_id       text PRIMARY KEY,
    title            text NOT NULL,
    content_type     text NOT NULL CHECK (content_type IN
        ('film', 'short_film', 'documentary', 'reportage', 'series_episode')),
    duration_seconds integer NOT NULL CHECK (duration_seconds > 0),
    updated_at       timestamptz NOT NULL DEFAULT clock_timestamp()
);

-- Meme principe que merch.touch_updated_at() dans le TD 2.
CREATE OR REPLACE FUNCTION public.touch_catalog_updated_at() RETURNS trigger AS $$
BEGIN
    NEW.updated_at := clock_timestamp();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER catalog_touch BEFORE UPDATE ON public.catalog
    FOR EACH ROW EXECUTE FUNCTION public.touch_catalog_updated_at();

-- En cas de relance, ne pas ecraser les modifications deja faites.
INSERT INTO public.catalog (content_id, title, content_type, duration_seconds, updated_at)
VALUES
    ('A', 'Les Lumieres du quartier', 'film',           3600, '2026-10-29 12:00:00+00'),
    ('B', 'Dernier Metro',           'short_film',     1200, '2026-10-29 12:00:00+00'),
    ('C', 'Au fil du fleuve',        'documentary',    2700, '2026-10-29 12:00:00+00'),
    ('D', 'Les Artisans de demain',  'reportage',      1800, '2026-10-29 12:00:00+00'),
    ('E', 'Hors Cadre - S01E01',     'series_episode', 1500, '2026-10-29 12:00:00+00'),
    ('F', 'La Route des collines',   'film',           5400, '2026-10-29 12:00:00+00')
ON CONFLICT (content_id) DO NOTHING;

COMMIT;

SELECT content_id, title, content_type, duration_seconds, updated_at
FROM public.catalog ORDER BY content_id;
