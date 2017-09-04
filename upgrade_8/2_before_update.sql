-- Delete all views from 'product.product'
delete from ir_ui_view where model = 'product.product';

-- disable new useless stock locations
update  stock_location set active = false  where company_id is null;

-- drop link between "groupes" location and "activities" locations
update stock_location set location_id = null where location_id in (select id from stock_location where company_id = 2);
