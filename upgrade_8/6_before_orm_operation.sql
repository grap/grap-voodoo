-- ----------------------------------------------------------------------------
-- Access Right Part
-- ----------------------------------------------------------------------------

-- Give Access to 'Manage multiple Locations' only for admin users
DELETE
FROM res_groups_users_rel
WHERE gid = (
        SELECT res_id
        FROM ir_model_data
        WHERE name ='group_locations' limit 1)
    AND uid IN (
        SELECT id FROM res_users
        WHERE login NOT IN (
            'sylvain.legal@grap.coop',
            'sylvain.legal2@grap.coop',
            'quentin.dupont@grap.coop',
            'quentin.dupont2@grap.coop',
            'admin@grap.coop')
        );

-- Give Access to 'Manage SQL Request' for admin users
INSERT INTO res_groups_users_rel (uid, gid)
    SELECT
        uid,
        (
        SELECT res_id
        FROM ir_model_data
        WHERE module = 'sql_request_abstract'
        AND name = 'group_sql_request_manager'
        ) as gid
    FROM res_groups_users_rel
    WHERE gid IN (
        SELECT res_id
        FROM ir_model_data WHERE module = 'base' AND name = 'group_no_one')
    AND uid not in (1);

-- ----------------------------------------------------------------------------
-- New Behaviour Part
-- ----------------------------------------------------------------------------

-- Due to better inheritance in pos_multiple_control, internal_account_id
-- no should be set for all cash and bank journals.
UPDATE account_journal
SET internal_account_id = default_debit_account_id
WHERE
    active = true
    AND type IN ('cash', 'bank');

-- ----------------------------------------------------------------------------
-- Various Part
-- ----------------------------------------------------------------------------

-- Change filter of stock.inventory
UPDATE ir_filters
SET domain = '[(''state'', ''in'', [''draft'', ''confirm''])]',
name = 'En brouillon ou en cours'
WHERE name = 'En brouillon'
and model_id = 'stock.inventory';

-- fix access right for creating customer from Point Of Sale
INSERT INTO res_company_users_rel
(SELECT 
    rc.id as cid,
    4 as user_id
FROM res_company rc
WHERE rc.id not in (select cid from res_company_users_rel where user_id = 4));
