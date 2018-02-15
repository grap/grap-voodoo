update pos_config set iface_create_draft_sale_order = false;
update pos_config set iface_create_confirmed_sale_order = false;

update account_journal set bank_control = true where type = 'bank';
