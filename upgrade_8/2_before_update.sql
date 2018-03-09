-- ----------------------------------------------------------------------------
-- Post Migration Part
-- ----------------------------------------------------------------------------
-- disable new useless stock locations
UPDATE stock_location
SET active = false
WHERE company_id is null;

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


-- ----------------------------------------------------------------------------
-- Full Update Part
-- ----------------------------------------------------------------------------
-- Delete all views for given models to recreate from scratch
DELETE
FROM ir_ui_view
WHERE model in ('product.product', 'pos.config', 'pos.order');



