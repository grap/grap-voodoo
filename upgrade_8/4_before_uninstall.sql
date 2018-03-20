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

-- INITIALIZATION : sale_food
UPDATE product_category
SET is_food = false;

UPDATE product_category
SET is_food = true
WHERE id not in (
      223   /* Revente / DIVERS / DIVERS */
    , 232   /* Matières Premières / DIVERS */

    , 150   /* Revente / animaux /                      DIVERS animaux */
    , 97    /* Revente / animaux /                      nourriture */
    , 191   /* Revente / artisanat /                    DIVERS artisanat */
    , 146   /* Revente / contenants & emballages /      bocaux */
    , 147   /* Revente / contenants & emballages /      DIVERS contenants & emballages */
    , 145   /* Revente / contenants & emballages /      sacs */
    , 86    /* Revente / contenants & emballages /      Seaux */
    , 123   /* Revente / jardinierie /                  graines */
    , 158   /* Revente / papeterie & presse /           DIVERS papeterie & presse */
    , 156   /* Revente / papeterie & presse /           livres */
    , 154   /* Revente / papeterie & presse /           papeterie */
    , 114   /* Revente / papeterie & presse /           presse */
    , 160   /* Revente / ustensiles /                   DIVERS ustensiles */
    , 152   /* Revente / ustensiles /                   ustensiles de cuisine */
    , 87    /* Revente / hygiène /                      huiles essentielles */
    , 6     /* Revente / hygiène /                      savons & shampoings */
    , 115   /* Revente / hygiène /                      cosmétiques */
    , 113   /* Revente / hygiène /                      bébé */
    , 100   /* Revente / hygiène /                      DIVERS hygiène */
    , 196   /* Revente / hygiène /                      hygiène féminine */
    , 195   /* Revente / hygiène /                      soin de la personne */
    , 92    /* Revente / entretien /                    DIVERS entretien */
    , 229   /* Revente / Surgelé /                      DIVERS surgelé */
    , 248   /* Spécial / DIVERS /                       Consigne Clients & Fournisseurs */
    , 187   /* Spécial / DIVERS /                       DIVERS */
);

UPDATE product_product pp
    SET is_food = pc.is_food
FROM product_template pt, product_category pc
WHERE pp.product_tmpl_id = pt.id
AND pt.categ_id = pc.id;

UPDATE product_product pp
SET state_id = rcd.state_id
FROM res_country_department rcd
WHERE rcd.id = pp.department_id;

-- INITIALIZATION : product_print_category
UPDATE res_company
    SET print_category_id = (SELECT res_id FROM ir_model_data where name = 'category_label_normal')
WHERE code in ('3PP', 'BSG', 'CDA', 'CHE', 'COU', 'CRB', 'EDC', 'KNL', 'LOC', 'MAM', 'PZI', 'RES');

UPDATE res_company
    SET print_category_id = (SELECT res_id FROM ir_model_data where name = 'category_label_big')
WHERE code in ('VEV');

UPDATE res_company
    SET print_category_id = (SELECT res_id FROM ir_model_data where name = 'category_label_small')
WHERE code in ('HAL');

UPDATE product_template pt
    SET print_category_id = rc.print_category_id
FROM res_company rc, product_product pp
WHERE rc.id = pt.company_id
AND pp.product_tmpl_id = pt.id
AND rc.print_category_id IS NOT null
AND pp.pricetag_state != '3';
