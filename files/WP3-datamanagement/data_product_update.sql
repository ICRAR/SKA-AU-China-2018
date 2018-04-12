-- A data product in the archive (e.g catalog, image cube) --

ALTER TABLE public.data_product
ADD COLUMN s_ra DOUBLE PRECISION,
ADD COLUMN s_dec DOUBLE PRECISION,
ADD COLUMN obs_id VARCHAR(20),
--ADD COLUMN s_region SPOLY,
ADD COLUMN object_name VARCHAR(80),
ADD COLUMN project VARCHAR(80);
