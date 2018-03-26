-- ----------------------------------------------------------------------------
-- Migration Part
-- ----------------------------------------------------------------------------

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
WHERE id != 1;

-- Delete all tiles
DELETE
FROM tile_tile;

-- Delete draft inventories;
DELETE
FROM stock_inventory
WHERE state = 'draft';

-- update ir sequence because OpenUpgrade try to recreate one, generating an error...
UPDATE ir_sequence_type
SET code='stock.orderpoint.openupgrade_7_8'
WHERE code = 'stock.orderpoint';

-- Clean invalid stock move uom
UPDATE stock_move sm
set product_uom = pt.uom_id
FROM product_uom uom_sm,  product_product pp, product_template pt, product_uom uom_pt
WHERE uom_sm.id = sm.product_uom
AND sm.product_id = pp.id
AND pt.id = pp.product_tmpl_id
AND uom_pt.id = pt.uom_id
AND uom_pt.category_id != uom_sm.category_id;

-- clean cash_control value
UPDATE account_journal
SET cash_control = false
WHERE type='bank';

UPDATE account_journal
SET cash_control = true
WHERE
    type='cash'
    AND active=true;

-- ----------------------------------------------------------------------------
-- New Fields Part - Fast Creation
-- ----------------------------------------------------------------------------
-- FAST CREATION - odoo.stock
ALTER TABLE stock_inventory_line
ADD COLUMN theoretical_qty NUMERIC DEFAULT 0.0;

-- FAST CREATION - product_margin_classification
ALTER TABLE product_template
ADD COLUMN theoretical_price NUMERIC DEFAULT 0.0;

ALTER TABLE product_template
ADD COLUMN theoretical_difference NUMERIC DEFAULT 0.0;

ALTER TABLE product_template
ADD COLUMN margin_state CHAR DEFAULT 'ok';

-- FAST CREATION - product_print_category
ALTER TABLE product_template
ADD COLUMN to_print bool DEFAULT False;

-- FAST CREATION - pos_default_empty_image
ALTER TABLE product_product ADD COLUMN has_image bool DEFAULT False;

UPDATE product_product
SET has_image = true
WHERE product_tmpl_id in (
    SELECT id
    FROM product_template
    WHERE image is not null);

-- FAST CREATION - intercompany_trade_account
ALTER TABLE account_invoice
ADD COLUMN intercompany_trade bool DEFAULT False;

UPDATE account_invoice ai
SET intercompany_trade = rp.intercompany_trade
FROM res_partner rp
WHERE ai.partner_id = rp.id;

ALTER TABLE account_invoice_line
ADD COLUMN intercompany_trade bool DEFAULT False;

UPDATE account_invoice_line ail
SET intercompany_trade = ai.intercompany_trade
FROM account_invoice ai
WHERE ail.invoice_id = ai.id;

-- ----------------------------------------------------------------------------
-- XML ID Part - Move from module to another
-- ----------------------------------------------------------------------------
-- Move from 'sale_food' (grap-odoo-business) to 'grap_qweb_report' (odoo-addons-grap)
UPDATE ir_model_data
SET module='grap_qweb_report'
WHERE module='sale_food'
AND model in ('ir.model', 'ir.model.fields')
AND (name like 'field_product_pricetag_type%' or name in('model_product_pricetag_type', 'field_res_company_pricetag_color', 'field_product_product_pricetag_type_id'));

-- Move from 'grap_print_product' (odoo-addons-grap) to 'product_ean13_image' (grap-odoo-incubator)
UPDATE ir_model_data
SET module='product_ean13_image'
WHERE module='grap_print_product'
AND model in ('ir.model.fields')
AND name in('field_product_product_ean13_image');
