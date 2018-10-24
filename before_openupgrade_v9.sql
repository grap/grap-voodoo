-- [General]
-- Drop the uninstalled module product_barcode_generator, because
-- openupgrade try to rename it into barcodes_generator_product
-- that has been backported by GRAP in v8.
DELETE
FROM ir_module_module
WHERE name = 'product_barcode_generator';

-- [product]
-- Drop obsolete constraint on product_supplierinfo created on
-- antiguous version, and not dropped.
ALTER TABLE product_supplierinfo
DROP CONSTRAINT product_supplierinfo_psi_product_name_uniq;
