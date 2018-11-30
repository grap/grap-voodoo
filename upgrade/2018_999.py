# coding: utf-8
from openerp.api import Environment


INSTALL = [
    'mobile_app_purchase',
    'base_company_legal_info',
]

UPDATE = [
    'grap_l10n_fr',
    'stock_picking_mass_assign',
    'barcodes_generator_abstract',
]


def uninstall(session, modules):
    env = Environment(session.cr, 1, {})
    module_obj = env['ir.module.module']
    modules = module_obj.search([('name', 'in', modules)])
    modules.module_uninstall()


def run(session, logger):
    if INSTALL:
        session.install_modules(INSTALL)
    if UPDATE:
        session.update_modules(UPDATE)

    # env = Environment(session.cr, 1, {})
