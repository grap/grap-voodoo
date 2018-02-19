-- Delete all views from 'product.product'
delete from ir_ui_view where model = 'product.product';
delete from ir_ui_view where model = 'pos.config';
delete from ir_ui_view where model = 'pos.order';

-- disable new useless stock locations
update  stock_location set active = false  where company_id is null;

-- COMMENTED, because seems to break stock location parent concept.
---- drop link between groupes location and activities locations
--update stock_location set location_id = null where location_id in (select id from stock_location where company_id = 2);


ALTER TABLE product_template ADD COLUMN theoretical_price NUMERIC DEFAULT 0.0;
ALTER TABLE product_template ADD COLUMN theoretical_difference NUMERIC DEFAULT 0.0;
ALTER TABLE product_template ADD COLUMN margin_state CHAR DEFAULT 'ok';



