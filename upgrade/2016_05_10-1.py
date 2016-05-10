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
    update_modules(session, ['sale_food'])

    update_module_list(session)

    company_obj = session._registry['res.company']
    pricelist_obj = session._registry['product.pricelist']
    user_obj = session._registry['res.users']
    invoice_obj = session._registry['account.invoice']
    uid = 1

    pricelists = pricelist_obj.browse(
        session.cr, uid, pricelist_obj.search(session.cr, uid, []))

    pricelists_lst = {False: 'UNDEFINED'}
    for pricelist in pricelists:
        pricelists_lst[pricelist.id] = "%s - %s" % (
            pricelist.name, pricelist.company_id.code)

    # STEP1. Install new modules (Pricelist on Account)
    install_modules(session, ['invoice_pricelist'])

    # 1.1 Recover correct data from old module
    execute(session, """
    UPDATE account_invoice
    SET pricelist_id = partner_pricelist_id
    WHERE id IN (
        SELECT ai.id
        FROM account_invoice ai
        INNER JOIN product_pricelist ppl ON ppl.id = ai.partner_pricelist_id
        WHERE ai.company_id = ppl.company_id);""")

    # 1.2 Set to Null bad invoices
    execute(session, """
    UPDATE account_invoice
    SET pricelist_id = NULL
    WHERE id IN (
        SELECT ai.id
        FROM account_invoice ai
        INNER JOIN product_pricelist ppl ON ppl.id = ai.partner_pricelist_id
        WHERE ai.company_id != ppl.company_id);""")

    companies = company_obj.browse(
        session.cr, uid, company_obj.search(session.cr, uid, [('id', '=', 16)]))

    for company in companies:
        print "==============================================================="
        print "Working on %s (#%d)" % (company.name, company.id)
        # change company
        user_obj.write(session.cr, uid, 1, {'company_id': company.id})
        bad_invoices = invoice_obj.browse(
            session.cr, uid, invoice_obj.search(session.cr, uid, [
            ('pricelist_id', '=', False),
            ('company_id', '=', company.id)],
            order='date_invoice'))

        if len(bad_invoices):
            print "I found vla %d bad invoices." % (len(bad_invoices))
            
            count = 0
            for invoice in bad_invoices:
                if invoice.id == 29975:
                    import pdb; pdb.set_trace()
                count += 1
                new_pricelist_id = invoice_obj.get_partner_pricelist_id(
                    session.cr, uid, [invoice.id], '', '')[invoice.id]
                print "%d / %d. replace %s by %s" % (
                    count, len(bad_invoices), pricelists_lst[invoice.partner_pricelist_id.id], pricelists_lst[new_pricelist_id])
                invoice_obj.write(session.cr, uid, [invoice.id], {'pricelist_id': new_pricelist_id})

    # Uninstall obsolete module
    uninstall_modules(session, ['pos_sale_reporting'])

    # Reinstall correctly pos_sale_reporting
    install_modules(session, ['pos_sale_reporting'])

    update_modules(session)


###    # STEP2. Install new modules (Report Webkit)
###    session.install_modules(['sale_order_webkit', 'report_custom_filename'])
###    # TODO FIX header
