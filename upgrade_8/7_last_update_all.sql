-- ----------------------------------------------------------------------------
-- Stock Picking Part Right Part
-- ----------------------------------------------------------------------------

-- Affect picking type to the correct purchase order
UPDATE purchase_order po
SET picking_type_id = spt.id
FROM stock_picking_type spt, res_company rc
WHERE po.company_id = rc.id
AND spt.company_id = rc.id
AND spt.code = 'incoming'
AND spt.active = True;
