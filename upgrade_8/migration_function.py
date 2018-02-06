# -*- coding: utf-8 -*-
import os
import signal
import time
import traceback

from subprocess import call, Popen
from datetime import datetime

from migration_import import erppeek, psutil

from secret_configuration import (
    ODOO_FOLDER_BACKUP, ODOO_FOLDER_NORMAL, ODOO_FOLDER_UPGRADE,
    ODOO_LOCAL_URL,
    ODOO_EXTERNAL_DATABASE, ODOO_EXTERNAL_URL,
    ODOO_USER, ODOO_PASSWORD, USE_SUDO, LOG_FILE)

TEMPORARY_FOLDER = '/tmp/'
TEMPORARY_FILE_DB_LIST = '/tmp/xx_database_list'

ODOO_UPDATE_SCRIPT = "../bin/start_openerp --stop-after-init"\
    " -u {module_list} -d {database} --log-level {log_level}"

ODOO_RUN_SCRIPT = "../bin/start_openerp --log-level {log_level} --debug"

STEP_DICT = {
    1: {'name': 'upgrade_7_8', 'backup_db': True, 'clean_after': True},
    2: {'name': 'update', 'backup_db': True, 'clean_after': False},
    3: {'name': 'install', 'backup_db': False, 'clean_after': False},
    4: {'name': 'uninstall', 'backup_db': False, 'clean_after': False},
    5: {'name': 'orm_operation', 'backup_db': False, 'clean_after': True},
}


def _generate_command(command, user):
    if not USE_SUDO:
        return command
    elif not user:
        return 'sudo %s' % command
    else:
        return 'sudo su %s -c "%s"' % (user, command)


def _bash_execute(command, user=False, log=True):
    full_command = _generate_command(command, user)
    if log:
        _log("CALLING (Sync) %s" % full_command)
    try:
        call(full_command, shell=True)
    except Exception as e:
        _log("ERROR during the execution", e)
        return False
    return True


def _bash_subprocess(command, user=False, log=True):
    full_command = _generate_command(command, user)
    if log:
        _log("CALLING (async) %s" % full_command)
    try:
        res = Popen(full_command, shell=True)
    except Exception as e:
        _log("ERROR during the execution", e)
        return False
    return res


def manage_odoo_process(active=False):
    _log("%s Odoo Process" % ('Start' if active else 'Stop'))
    if active:
        _bash_execute("service odoo start")
    else:
        _bash_execute("service odoo stop")


def set_upgrade_mode(upgrade_mode):
    _log("Set Upgrade mode to %s" % upgrade_mode)
    if upgrade_mode and not os.path.isdir(ODOO_FOLDER_BACKUP):
        os.rename(ODOO_FOLDER_NORMAL, ODOO_FOLDER_BACKUP)
        os.rename(ODOO_FOLDER_UPGRADE, ODOO_FOLDER_NORMAL)
        os.mkdir(ODOO_FOLDER_UPGRADE)
    elif not upgrade_mode and os.path.isdir(ODOO_FOLDER_BACKUP):
        os.rmdir(ODOO_FOLDER_UPGRADE)
        os.rename(ODOO_FOLDER_NORMAL, ODOO_FOLDER_UPGRADE)
        os.rename(ODOO_FOLDER_BACKUP, ODOO_FOLDER_NORMAL)


def execute_sql_step_file(database, step):
    step_name = STEP_DICT[step]['name']
    sql_file = '%d_before_%s.sql' % (step, step_name)
    if os.path.exists(sql_file):
        return _bash_execute(
            "psql -f %s %s -o %szz_%s__output_%s" % (
                sql_file, database, TEMPORARY_FOLDER, database, sql_file),
            user='postgres')


def create_new_database(target_database, step):
    step_name = STEP_DICT[step]['name']
    _bash_execute(
        "psql -l -o %s" % TEMPORARY_FILE_DB_LIST, user='postgres', log=False)
    file_database_list = open(TEMPORARY_FILE_DB_LIST, 'r')
    content = ''.join(file_database_list.readlines())
    if step == 1:
        # found a name for the database to create
        found = True
        i = 1
        template_database = target_database
        while found:
            new_database = '%s_%s_current' % (target_database, str(i).zfill(3))
            found = ' %s ' % new_database in content
            i += 1

    else:
        template_database = '%s___%d_%s' % (target_database, step, step_name)
        new_database = '%s_current' % (target_database)
        if new_database in content:
            # Drop database
            _bash_execute("dropdb %s" % (new_database), user='postgres')

    _bash_execute(
        "createdb %s --template %s --owner odoo" % (
            new_database, template_database), user='postgres')

    _bash_execute("rm %s" % TEMPORARY_FILE_DB_LIST, log=False)
    return new_database


def backup_database(database, step):
    step_name = STEP_DICT[step]['name']
    backup_db = STEP_DICT[step]['backup_db']
    if backup_db:
        backup = '%s___%d_%s' % (
            database.replace('_current', ''), step, step_name)
        # Search for previous backup
        _bash_execute(
            "psql -l -o %s" % TEMPORARY_FILE_DB_LIST, user='postgres',
            log=False)
        file_database_list = open(TEMPORARY_FILE_DB_LIST, 'r')
        content = file_database_list.readlines()
        found = ' %s ' % backup in ''.join(content)
        if found:
            # Drop previous backup
            _bash_execute("dropdb %s" % backup, user='postgres')
        # Backup Database
        _bash_execute(
            "createdb %s --template %s --owner odoo" % (
                backup, database), user='postgres')
        _bash_execute("rm %s" % TEMPORARY_FILE_DB_LIST, log=False)


def clean_database(database, step):
    if not STEP_DICT[step]['clean_after']:
        return
    _bash_execute(
        "psql -d %s -c 'VACUUM FULL;'" % database, user='postgres')
    _bash_execute(
        "psql -d %s -c 'REINDEX DATABASE %s;'" % (database, database),
        user='postgres')
    _bash_execute(
        "psql -d %s -c 'ANALYSE;'" % database, user='postgres')


def update_instance(database, module_list, log_level):
    _bash_execute(
        ODOO_UPDATE_SCRIPT.format(
            database=database, module_list=module_list, log_level=log_level),
        user='odoo')


def run_instance(log_level):
    res = _bash_subprocess(
        ODOO_RUN_SCRIPT.format(log_level=log_level), user='odoo')
    time.sleep(5)
    return res


def kill_process(process):
    parent = psutil.Process(process.pid)
    children_pids = [x.pid for x in parent.children(recursive=True)]
    pids = [process.pid] + children_pids
    _log("KILL Process(es) #%s" % (', '.join([str(pid) for pid in pids])))
    for pid in pids:
        _bash_execute("kill -9 %d" % pid)
    time.sleep(5)


def _connect_instance(url, database, login, password):
    try:
        openerp = erppeek.Client(url)
    except Exception as e:
        _log("ERROR : Connection to odoo instance '%s' failed" % url, e)
        return False
    try:
        openerp.login(
            login, password=password, database=database)
    except Exception as e:
        _log("ERROR : Authentication failed on %s with %s login" % (
            url, login), e)
        return False
    return openerp


def check_module_state(database, module_list_to_check):
    openerp = _connect_instance(
        ODOO_LOCAL_URL, database, ODOO_USER, ODOO_PASSWORD)
    # Initialize my_dict
    state_list = [
        'uninstallable', 'installed', 'to upgrade', 'to remove', 'to install']
    my_dict = {}
    for version in ['7', '8']:
        my_dict[version] = {}
        for state in state_list:
            my_dict[version][state] = []
    modules = openerp.IrModuleModule.browse([('state', '!=', 'uninstalled')])
    for module in modules:
        major_version = module.latest_version[0]
        my_dict[major_version][module.state].append(module.name)
    for major_version, sub_dict in my_dict.iteritems():
        _log("===============================================================")
        _log("Major Version %s" % major_version)
        for state, module_list in sub_dict.iteritems():
            _log("======= State '%s'" % state)
            _log(module_list)
    for module in module_list_to_check:
        if module not in my_dict['8']['installed']:
            raise Exception("module %s not in installed state" % module)


def install_modules(database, module_list):
    # Update module list
    openerp = _connect_instance(
        ODOO_LOCAL_URL, database, ODOO_USER, ODOO_PASSWORD)
    if not openerp:
        _log("FATAL : install process aborted")
        return
    _log("Update modules list...")
    openerp.IrModuleModule.update_list()

    # Install each module
    for module_name in module_list:
        openerp = _connect_instance(
            ODOO_LOCAL_URL, database, ODOO_USER, ODOO_PASSWORD)
        if not openerp:
            _log("FATAL : install process aborted")
            return
        modules = openerp.IrModuleModule.browse([('name', '=', module_name)])
        if len(modules) == 0:
            _log("ERROR : Module not found %s" % module_name)
        else:
            module = modules[0]
            if modules[0].state in ['uninstalled', 'to install']:
                _log("Installing... %s" % module.name)
                try:
                    openerp.IrModuleModule.button_immediate_install(
                        [module.id])
                except Exception as e:
                    _log("ERROR during '%s' installation" % module_name, e)
            else:
                _log("WARNING : '%s' module in '%s' state" % (
                    module.name, module.state))


def uninstall_modules(database, module_list):
    # Uninstall each module
    for module_name in module_list:
        openerp = _connect_instance(
            ODOO_LOCAL_URL, database, ODOO_USER, ODOO_PASSWORD)
        if not openerp:
            _log("FATAL : uninstall process aborted")
            return
        modules = openerp.IrModuleModule.browse([('name', '=', module_name)])
        if len(modules) == 0:
            _log("ERROR : Module not found %s" % module_name)
        else:
            module = modules[0]
            if modules[0].state not in ['uninstalled']:
                _log("Uninstalling... %s" % module.name)
                try:
                    openerp.IrModuleModule.module_uninstall([module.id])
                except Exception as e:
                    _log("ERROR during '%s' uninstallation" % module_name, e)
            else:
                _log("WARNING : '%s' module in '%s' state" % (
                    module.name, module.state))


def create_inventories(database):
    move_fields = 'product_id', 'product_uom', 'product_qty'

    # Connect to old database and new database
    old_openerp = _connect_instance(
        ODOO_EXTERNAL_URL, ODOO_EXTERNAL_DATABASE, ODOO_USER, ODOO_PASSWORD)

    # Load companies
    company_ids = old_openerp.ResCompany.search([
        ('code', '!=', 'GRP'),
        ('name', 'not ilike', 'ZZZ%'),
    ])

    for company_id in company_ids:
        new_openerp = _connect_instance(
            ODOO_LOCAL_URL, database, ODOO_USER, ODOO_PASSWORD)

        # Get Location
        locations = new_openerp.StockLocation.browse([
            ('company_id', '=', company_id),
            ('usage', '=', 'internal'),
            ('name', 'ilike', '%stock%'),
        ])

        if len(locations) != 1:
            _log(
                "ERROR - INVENTORY CANCELLED %d internal location(s)"
                " found for the company %d - %s" % (
                    len(locations), company.id, company.code))
            _log(', '.join([x.name for x in locations]))
            continue
        else:
            location = locations[0]

        # Get company
        company = new_openerp.ResCompany.browse(company_id)
        _log("Handling inventory for company #%d - %s" % (
            company.id, company.code))

        # Get Previous RAZ Inventory in old instance
        old_stock_inventories = old_openerp.StockInventory.search([
            ('company_id', '=', company_id),
            ('name', 'ilike', '%Inventaire Premigration V8%'),
            ('state', '=', 'done'),
        ], order='date desc')

        if not len(old_stock_inventories):
            _log("INFO. %s company skipped. No RAZ Inventory Found." % (
                company.code))
            continue

        if len(old_stock_inventories) > 0:
            _log(
                "WARNING. %d inventories found for %s."
                " Taking the last one" % (
                    len(old_stock_inventories), company.code))

        old_stock_inventory = old_openerp.StockInventory.browse(
            [('id', '=', old_stock_inventories[0])])

        old_move_ids = [x.id for x in old_stock_inventory.move_ids[0]]

        move_ids = old_openerp.StockMove.search([
            ('id', 'in', old_move_ids), ('location_id', '=', location.id)])

        if not len(move_ids):
            _log("INFO. %s company skipped. No moves found." % (
                company.code))
            continue
        # Load Data in old instance
        _log("Loading Data for %d moves" % len(move_ids))
        products_data = old_openerp.StockMove.read(move_ids, move_fields)
        _log("Loaded")

        not_null_product_qty = 0
        for product_data in products_data:
            if product_data['product_qty'] > 0:
                not_null_product_qty += 1
        if not not_null_product_qty:
            _log("INFO. %s company skipped. No products with quantity." % (
                company.code))
            continue
        _log("%d products data loaded. %d have not null quantity" % (
            len(products_data), not_null_product_qty))

        # Switch user in new company
        user = new_openerp.ResUsers.browse([1])
        user.write({'company_id': company_id})

        # Load Data in new instance
        new_product_ids = new_openerp.ProductProduct.search([
            ('company_id', '=', company_id),
            '|', ('active', '=', True), ('active', '=', False)])

        # Eventually cancel pending inventories
        pending_inventories = new_openerp.StockInventory.browse([
            ('company_id', '=', company_id),
            ('state', '=', 'confirm'),
        ])
        for pending_inventory in pending_inventories:
            _log(
                "WARNING, cancelling pending inventory #%d - %s (%s)" % (
                    pending_inventory.id, pending_inventory.name,
                    pending_inventory.date))
            pending_inventory.action_cancel_draft()

        # Create inventories in new instance
        stock_inventory = new_openerp.StockInventory.create({
            'name': '%s - Inventaire Post Migration V8' % (company.code),
            'location_id': location.id,
            'filter': 'partial',
            'company_id': company_id,
        })
        stock_inventory.prepare_inventory()

        # Add lines
        line_vals = []
        for product_data in products_data:
            if product_data['product_id'][0] not in new_product_ids:
                # TODO set ERROR in production
                _log(
                    "WARNING - product %d ignored because not found"
                    " for the company %d - %s" % (
                        product_data['product_id'][0],
                        company.id, company.code))
                continue
            if product_data['product_qty'] > 0:
                line_val = {
                    'partner_id': False,
                    'product_id': product_data['product_id'][0],
                    'product_uom_id': product_data['product_uom'][0],
                    'prod_lot_id': False,
                    'package_id': False,
                    'product_qty': product_data['product_qty'],
                    'location_id': location.id,
                }
                line_vals.append([0, 0, line_val])
        _log(
            "writing %d inventory lines for %s ..." % (
                len(line_vals), company.code))
        try:
            stock_inventory.write({'line_ids': line_vals})
        except Exception as e:
            _log(
                "WARNING, inventory failed for company %s."
                " Retrying product per product" % company.code, e)
            count = 0
            for line_val in line_vals:
                count += 1
                try:
                    stock_inventory.write({'line_ids': [line_val]})
                except Exception as e:
                    _log(
                        "WARNING, inventory line failed for a product"
                        "line_val" + str(line_val))
        stock_inventory.action_done()

def create_tiles(database):
    # Connect to old database and new database
    old_openerp = _connect_instance(
        ODOO_EXTERNAL_URL, ODOO_EXTERNAL_DATABASE, ODOO_USER, ODOO_PASSWORD)

    new_openerp = _connect_instance(
        ODOO_LOCAL_URL, database, ODOO_USER, ODOO_PASSWORD)
    old_tiles = old_openerp.TileTile.browse([])
    for old_tile in old_tiles:
        old_model = old_tile.model_id.model
        if old_tile.id in (13, 14, 42, 43, 72) or 'Balance Facture Frs' in old_tile.name:
            _log(
                "INFO tile %d skipped. Big tile. about invoices. %s" % (
                    old_tile.id, old_model))
            continue
        if not len(new_openerp.IrModel.browse([('model', '=', old_model)])):
            _log(
                "INFO tile %d skipped. Model '%s' not found" % (
                    old_tile.id, old_model))
            continue
        if not old_tile.action_id:
            _log(
                "WARNING tile %d skipped. Old Action undefined" % (
                    old_tile.id))
            continue
        if not len(new_openerp.IrActionsAct_window.browse(
                [('id', '=', old_tile.action_id.id)])):
            _log(
                "WARNING tile %d skipped. Action %d not found" % (
                    old_tile.id, old_tile.action_id.id))
            continue
        if old_tile.field_id and not len(new_openerp.irModelFields.browse(
                [('id', '=', old_tile.field_id.id)])):
            _log(
                "WARNING tile %d skipped. Field %d not found" % (
                    old_tile.id, old_tile.field_id.id))
            continue
        new_vals = {
            'sequence': old_tile.sequence,
            'name': old_tile.name,
            'domain': old_tile.domain,
            'model_id': old_tile.model_id.id,
            'user_id': old_tile.user_id and old_tile.user_id.id or False,
            'action_id': old_tile.action_id.id,
            'background_color': old_tile.color,
            'font_color': old_tile.font_color,
            'primary_function': 'count',
        }
        if old_tile.field_function:
            new_vals.update({
                'secondary_function': old_tile.field_function,
                'secondary_field_id': old_tile.field_id.id,
            })
        new_openerp.TileTile.create(new_vals)



def _log(text, error=False):
    try:
        res = '%s - %s' % (
            datetime.today().strftime("%d-%m-%y - %H:%M:%S"), text)
        # Log in File
        file = open(LOG_FILE, 'a')
        file.write(res + '\n')
        # Classical Stdout
        print res
        if error:
            file.write(error)
            print error
            traceback.print_stack()
    except:
        pass
