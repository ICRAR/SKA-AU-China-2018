-- This file contains the obscore view 
--
-- To update this view:
-- * rename this file with a new timestamp so flyway will re-run it on deploy
-- * make required changes to this file.


-- ObsCore v1.0 compliant view of the CASDA observations and their data products
DROP VIEW IF EXISTS public.obscore;


CREATE VIEW public.obscore (
    dataproduct_type,
	calib_level,
	obs_collection,
	obs_id,
	obs_publisher_did,
	access_url,
	access_format,
	access_estsize,
	target_name,
	s_ra,
	s_dec,
	s_fov,
	s_region,
	s_resolution,
	t_min,
	t_max,
	t_exptime,
	t_resolution,
	em_min,
	em_max,
	em_res_power,
	o_ucd,
	pol_states,
	facility_name,
	instrument_name,
	
	dataproduct_subtype,
	em_ucd,
	em_unit,
	em_resolution,
	s_resolution_min,
	s_resolution_max,
	s_ucd,
	s_unit,
	thumbnail_id,
	released_date,
	quality_level) AS

	-- Advertise catalogues via obs_core
	select null, 2, 'shaoska', 'observation', dp.file_id, 
	'#{baseUrl}/RETREIVE?fileid=' || dp.file_id, 'application/x-votable+xml', CAST(0 AS BIGINT), 
	null, null, null, null, null, null::double precision, 
	null, null, 0, null::double precision, 
	null, null, null::double precision, 
	'phot.flux.density', null, null, null,
--	'catalogue.'||lower(replace(c.catalogue_type,'_', '.')),
	'catalogue',
	'em.wl', 'm', null::double precision, null::double precision, null::double precision, 'pos.eq', 'deg', null::bigint, 
	null, null
	from public.data_product dp
	where dp.dataproduct_type = 'CATALOGUE' AND dp.deposit_state = 'DEPOSITED'
	
    ORDER BY 4, 5;
  
COMMENT ON VIEW public.obscore is 'An implementation of the Observation Data Model Core Components \
    to allow generic querying of the availability of SHAO SKA data products.';
  
  