-- Delete new create stock picking type
DELETE
FROM stock_picking_type
WHERE company_id is null and name='PoS Orders';

-- Disable stock_picking_type internal
UPDATE stock_picking_type
SET active=false
WHERE id not in (
        SELECT picking_type_id
        FROM stock_picking
        GROUP BY picking_type_id)
    AND active = true
    AND name = 'Internal Transfers';

-- Disable stock picking type from inactive PoS config
UPDATE stock_picking_type
SET active=false
WHERE id IN (
        SELECT picking_type_id
        FROM pos_config
        WHERE state != 'active');

-- Disable fucking 3PP picking type
update stock_picking_type set active=false where company_id = 1 and warehouse_id != 1;

-- Fast creation of product_product.has_image (1/2)
ALTER TABLE product_product ADD COLUMN has_image bool DEFAULT False;

UPDATE product_product
    SET has_image = true
    WHERE product_tmpl_id in (
        SELECT id
        FROM product_template
        WHERE image is not null);


-- Fast creation of the module product_template.to_print
ALTER TABLE product_template ADD COLUMN to_print bool DEFAULT False;

