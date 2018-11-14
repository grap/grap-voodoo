# coding: utf-8
from openerp.api import Environment


INSTALL = [
    'account_invoice_pricelist_stock_account',
    'product_analytic',
    'product_category_product_qty',
    'multi_search_partner',
    'multi_search_product',
]

UPDATE = [
    'account_export_ebp',
    'account_invoice_pricelist',
    'account_move_change_number',
    'product_margin_classification',
    'invoice_verified_state',
    'pos_invoicing',
    'product_categ_search_complete_name',
    'product_standard_price_tax_included',
    'sale_line_change_custom',
    'stock_picking_quick_edit',
    'stock_picking_mass_change',
    'recurring_consignment',
]


def uninstall(session, modules):
    env = Environment(session.cr, 1, {})
    module_obj = env['ir.module.module']
    modules = module_obj.search([('name', 'in', modules)])
    modules.module_uninstall()


def handle_field_renaming(env, logger, model_name, old_name, new_name):
    model = env['ir.model'].search([('model', '=', model_name)])[0]
    tiles = env['tile.tile'].search([
        ('model_id', '=', model.id),
        '|', ('domain', 'ilike', "'%s'" % old_name),
        ('domain', 'ilike', '"%s"' % old_name)])
    if tiles:
        logger.info("UPGRADE: change domain of %s for %d tiles" % (
            model_name, len(tiles)))
        for tile in tiles:
            tile.domain = tile.domain.replace(
                "'%s'" % (old_name), "'%s'" % (new_name)).replace(
                    '"%s"' % (old_name), '"%s"' % (new_name))

    filters = env['ir.filters'].search([
        ('model_id', '=', model_name),
        '|', ('domain', 'ilike', "'%s'" % old_name),
        ('domain', 'ilike', '"%s"' % old_name)])
    if filters:
        logger.info("UPGRADE: change domain of %s for %d filters" % (
            model_name, len(filters)))
        for filter in filters:
            filter.domain = filter.domain.replace(
                "'%s'" % (old_name), "'%s'" % (new_name)).replace(
                    '"%s"' % (old_name), '"%s"' % (new_name))


def run(session, logger):
    if INSTALL:
        session.install_modules(INSTALL)
    if UPDATE:
        session.update_modules(UPDATE)

    uninstall(session, ['account_invoice_pricelist_sale_stock'])
    uninstall(session, ['product_improved_search'])
    # FIXME Don't know why
    # uninstall(session, ['product_category_improve'])

    # refactoring of pos_invoicing
    env = Environment(session.cr, 1, {})

    # handle_field_renaming(
    #     env, logger, 'account.invoice', 'forbid_payment',
    #     'pos_pending_payment')

    # # refactoring of account_export_ebp
    # handle_field_renaming(
    #     env, logger, 'account.move', 'exported_ebp_id',
    #     'ebp_export_id')

    # # Uninstall Italian language
    # lang = env['res.lang'].search([('code', '=', 'it_IT')])
    # lang.active = False
    # lang.unlink()

    # FIXME Don't know why
    # # Set multi_search_product
    # setting = env['base.config.settings'].create({
    #     'multi_search_product_separator': ':',
    #     'multi_search_partner_separator': ':',
    # })
    # setting.execute()

    # FIXME Don't know why
    # fix consignors
    # products = env['product.product'].search(
    #     [('consignor_partner_id', '!=', False)])
    # for product in products:
    #     if len(product.seller_ids) != 1:
    #         logger.info("UPGRADE: Fix sellers ids for #%d #%d - %s" % (
    #             product.company_id.id, product.id, product.name))
    #         product.onchange_consignor_partner_id_variant()

    # clean obsolete models
    try:
        wizard = env['cleanup.purge.wizard.model'].create({})
        wizard.purge_all()
    except:
        pass

    try:
        wizard = env['cleanup.purge.wizard.table'].create({})
        wizard.purge_all()
    except:
        pass

    try:
        wizard = env['cleanup.purge.wizard.column'].create({})
        for line in wizard.purge_line_ids:
            if 'x_bi_sql_view' in line.model_id.model:
                pass
            elif line.name in [
                    'openupgrade_legacy_8_0_account_id',
                    'openupgrade_legacy_8_0_prodlot_id',
                    'openupgrade_legacy_8_0_tracking_id']:
                pass
            else:
                line.purge()
    except:
        pass
