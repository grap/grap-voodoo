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
