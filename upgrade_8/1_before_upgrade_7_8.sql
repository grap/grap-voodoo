-- Move fields from pos_tax to grap_change_account_move_line
-- To allow to uninstall correctly pos_tax
UPDATE ir_model_data
SET module = 'grap_change_account_move_line'
WHERE
    module = 'pos_tax'
    AND model='ir.model.fields';

-- Disable all ir cron
UPDATE ir_cron
SET active = false
where id != 1;

-- Delete obsolete Tiles
DELETE
FROM tile_tile
WHERE model_id in (
    SELECT id
    FROM ir_model
    WHERE model in ('stock.picking.in', 'stock.picking.out')
    );

-- Delete all tiles
DELETE
FROM tile_tile;

-- Delete draft inventories;
delete
FROM stock_inventory
WHERE state = 'draft';

-- update ir sequence because OpenUpgrade try to recreate one, generating an error...
update ir_sequence_type set code='stock.orderpoint.openupgrade_7_8' where code = 'stock.orderpoint';

-- Pre create field stock_inventory_line.theoretical_qty
ALTER TABLE stock_inventory_line ADD COLUMN "theoretical_qty" NUMERIC DEFAULT 0.0;

-- clean cash_control value
update account_journal set cash_control = false where type='bank';
update account_journal set cash_control = true where type='cash' and active=true;

-- Clean invalid stock move uom
UPDATE stock_move sm
set product_uom = pt.uom_id
FROM product_uom uom_sm,  product_product pp, product_template pt, product_uom uom_pt
WHERE uom_sm.id = sm.product_uom
AND sm.product_id = pp.id
AND pt.id = pp.product_tmpl_id
AND uom_pt.id = pt.uom_id
AND uom_pt.category_id != uom_sm.category_id;
