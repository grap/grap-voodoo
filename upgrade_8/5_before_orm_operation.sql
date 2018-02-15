-- Fast creation of product_product.has_image (2/2)
ALTER TABLE product_product ADD COLUMN has_image bool DEFAULT False;

UPDATE product_product
    SET has_image = true
    WHERE product_tmpl_id in (
        SELECT id
        FROM product_template
        WHERE image is not null);

delete from res_groups_users_rel
where gid = (
        SELECT res_id
        FROM ir_model_data
        WHERE name ='group_locations' limit 1)
    and uid in (
        SELECT id FROM res_users
        WHERE login not in ('sylvain.legal@grap.coop', 'sylvain.legal2@grap.coop', 'quentin.dupont@grap.coop', 'quentin.dupont2@grap.coop', 'admin@grap.coop'));


update account_journal set internal_account_id = default_debit_account_id where active = true and type in ('cash', 'bank');
