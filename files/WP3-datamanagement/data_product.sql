-- A data product in the archive (e.g catalog, image cube) --

CREATE TABLE public.data_product (  
id               BIGSERIAL PRIMARY KEY,
file_id   VARCHAR ( 255 ),
dataproduct_type VARCHAR ( 255 ),
deposit_state VARCHAR(255),
last_modified  TIMESTAMP DEFAULT now()
);