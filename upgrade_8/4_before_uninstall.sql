-- INITIALIZATION : account_invoice_supplierinfo_update
UPDATE account_invoice
SET supplierinfo_ok = false;

UPDATE account_invoice
SET supplierinfo_ok = true
WHERE type = 'in_invoice' and state in ('draft', 'verified');

--INITIALIZATION pos_multiple_control
UPDATE account_journal
SET bank_control = true
WHERE type = 'bank';

-- INITIALIZATION pos_order_to_sale_order
update pos_config set iface_create_draft_sale_order = false;
update pos_config set iface_create_confirmed_sale_order = false;

-- INITIALIZATION : pos_picking_load
UPDATE pos_config
SET iface_load_picking = false;

-- INITIALIZATION : product_uom_use_type
UPDATE product_uom
SET use_type = 'purchase';

UPDATE product_uom
SET use_type = 'sale' where name in ('01kg', '1PCE', 'Heure', 'Jour', 'km', 'Repas');

UPDATE product_uom_categ
set to_weigh = true
WHERE name = 'Weight';
