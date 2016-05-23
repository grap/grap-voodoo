# -*- coding: utf-8 -*-

def execute(session, sql):
    print ">>> Executing >>>\n %s\n" % (sql)
    session.cr.execute(sql)
    print "Done."

def update_module_list(session):
    print ">>> Updating module list >>>"
    module_update_obj = session._registry['base.module.update']
    module_update_obj.update_module(session.cr, session.uid, False)
    print "Done."

def install_modules(session, modules):
    for module in modules:
        print ">>> Installing Module %s >>>" % (module)
        session.install_modules([module])
        print "Done."

def update_modules(session, modules=['all']):
    if modules == ['all']:
        modules = ['base']
    for module in modules:
        print ">>> Updating Module %s >>>" % (module)
        session.update_modules([module])
        print "Done."

def uninstall_modules(session, modules):
    module_obj = session._registry['ir.module.module']
    for module in modules:
        print ">>> Uninstalling Module %s >>>" % (module)
        module_id = module_obj.search(
            session.cr, session.uid, [('name', '=', module)])
        module_obj.module_uninstall(session.cr, session.uid, module_id)
        print "Done."


def run(session, logger):
    update_module_list(session)

    # 1.1 Fix. Affect fiscal position to GRAP
    execute(session, """
    UPDATE account_fiscal_position
    SET company_id = 3 where company_id is Null;""")

    # Update Specific Module
    update_modules(session, ['account_fiscal_company'])

    # TODO Update all (for production only)
#    update_modules(session)
