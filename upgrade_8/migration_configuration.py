# -*- coding: utf-8 -*-

INSTALL_MODULE_LIST = [
    'web_sheet_full_width',
    'stock_picking_mass_action',
    'pos_default_empty_image',
    'product_supplierinfo_tree_price_info',
    'web_ckeditor4',
    'web_favicon',
    'web_clean_navbar',
    'web_graph_sort',
    'web_graph_improved',
    'web_group_expand',
    'web_invalid_tab',
    'web_offline_warning',
    'web_invalid_tab',
    'web_switch_company_warning',
    'bi_sql_editor',
    'pos_order_to_sale_order',
    'account_invoice_merge_purchase',
    'account_invoice_supplierinfo_update',
    'account_invoice_supplierinfo_update_discount',
    'purchase_supplier_rounding_method',
    'product_margin_classification',
    'stock_disable_barcode_interface',
    'product_supplierinfo_tree_price_info',
    'pos_pricelist',
    'pos_multiple_control',
    'grap_pos_change_sale_move',
    'grap_pos_change_payment_move',
    'web_hide_db_manager_link',
    'l10n_fr_siret',
    'stock_picking_type_image',
    'grap_qweb_report',
    'pos_pricelist_fiscal_company',
    'stock_picking_backorder_strategy',
    'pos_cash_move_reason',
    'pos_to_weight_by_product_uom',
    'product_sale_taxe_price_included',
    'product_uom_use_type',

    # REPLACE
    # account_product_fiscal_classification
    #   (replace product_tax_group)
    # product_standard_price_tax_included
    #   (replace product_standard_price_vat_incl)

    # A TESTER
    # 'purchase_add_product_supplierinfo'
    # 'account_invoice_line_price_subtotal_gross'
    # 'base_mail_bcc',
    # 'product_replenishment_cost',
    # 'pos_order_load',

    # # FIXME / later
    # # > en conflit avec invoice_pricelist.
    # 'account_invoice_pricelist',
    # 'account_invoice_pricelist_sale',
    # 'account_invoice_pricelist_sale_stock',

    # # > Init values.
    # 'grap_standard_price

    # # > Later, when grap_standard_price will be installed.
    # 'pos_margin',
    # 'invoice_margin',

]

UNINSTALL_MODULE_LIST = [
    'pos_tax',
    'process',
    'account_delete_move_null_amount',
    'account_mass_drop_moves',
    'account_merge_moves_by_patterns',
    'account_move_period_date_conform',
    'account_tax_update',
    'auth_generate_password',
    'grap_reporting',
    'intercompany_trade_purchase_discount',
    'intercompany_trade_purchase_order_reorder_lines',
    'intercompany_trade_sale_order_dates',
    'manage_accounts_integrity',
    'mobile_app_inventory',
    'module_parent_dependencies',
    'pos_backup_draft_orders',
    'pos_both_mode',
    'pos_improve_header',
    'pos_improve_images',
    'pos_improve_posbox',
    'pos_keep_draft_orders',
    'pos_remove_default_partner',
    'pos_second_header',
    'pos_street_market',
    'product_average_consumption',
    'product_get_cost_field',
    'product_stock_cost_field_report',
    'purchase_compute_order',
    'purchase_compute_order_pos',
    'purchase_compute_order_sale',
    'sale_fiscal_company',
    'sale_reporting',
    'stock_picking_mass_assign',
    'web_confirm_window_close',
    'web_popup_large',
    'pos_multiple_cash_control',
    'grap_change_account_move_line',
    'stock_inventory_sum_duplicates',
    'grap_change_print',
]

CHECK_MODULE_LIST = ['point_of_sale']
