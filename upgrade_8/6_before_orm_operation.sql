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
