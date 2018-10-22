# coding: utf-8
from openerp.api import Environment


INSTALL = [
    'product_analytic',
    'account_invoice_pricelist_stock_account',
    'multi_search_product',
    'multi_search_partner',
    'product_category_product_qty',
]

UPDATE = [
    'account_invoice_pricelist',
    'product_margin_classification',
    'product_standard_price_tax_included',
    'stock_picking_quick_edit',
    'stock_picking_mass_change',
    'pos_invoicing',
    'account_export_ebp',
    'product_categ_search_complete_name',
    'account_move_change_number',
    'invoice_verified_state',
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
    # if INSTALL:
    #     session.install_modules(INSTALL)
    # if UPDATE:
    #     session.update_modules(UPDATE)

    # uninstall(session, ['account_invoice_pricelist_sale_stock'])
    # uninstall(session, ['product_improved_search'])
    # uninstall(session, ['product_category_improve'])

    # Extra Operation
    env = Environment(session.cr, 1, {})

    # refactoring of pos_invoicing
    # handle_field_renaming(
    #     env, logger, 'account.invoice', 'forbid_payment',
    #     'pos_pending_payment')

    # refactoring of account_export_ebp
    # handle_field_renaming(
    #     env, logger, 'account.move', 'exported_ebp_id',
    #     'ebp_export_id')

    # Uninstall Italian language
    # lang = env['res.lang'].search([('code', '=', 'it_IT')])
    # lang.active = False
    # lang.unlink()

    # Set multi_search_product
    # setting = env['base.config.settings'].create({
    #     'multi_search_product_separator': ':',
    #     'multi_search_partner_separator': ':',
    # })
    # setting.execute()

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
