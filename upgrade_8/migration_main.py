# -*- coding: utf-8 -*-
from optparse import OptionParser

from migration_function import (
    manage_odoo_process, set_upgrade_mode, backup_database,
    create_new_database, execute_sql_step_file, update_instance,
    run_instance, kill_process, install_modules, uninstall_modules, _log,
    clean_database, create_inventories, check_module_state,
    STEP_DICT)

from migration_configuration import\
    INSTALL_MODULE_LIST, UNINSTALL_MODULE_LIST, CHECK_MODULE_LIST


# ---------------
# -- Options Part
# ---------------

parser = OptionParser()
parser.add_option(
    "-s", "--step", dest="step", default='1', help="Step to begin:\n"
    "1: 'OpenUpgrade' Step(Default value)\n"
    "2: 'Update All with OCB' Step\n"
    "3: 'Install New Modules' Step\n"
    "4: 'Uninstall Obsolete Modules' Step\n"
    "5: 'ORM operation' Step\n")
parser.add_option(
    "-d", "--database", dest="database",
    help="Database to use:\n"
    "If step == 1, a new database will be created, templated by the"
    " database defined in this option\n"
    "If step != 1, the database used will be the database named"
    " {database_arg}_{step_name}")
parser.add_option(
    "-l", "--log-level", dest="log_level", default='info',
    help="Log Level to use:\n"
    "debug : DEBUG\n"
    "info : INFO (Default Value)\n"
    "warn : WARNING\n"
    "error : ERROR\n"
    "critical : CRITICAL")
(options, args) = parser.parse_args()
target_step = int(options.step)
if not options.database:
    raise Exception("Target Database not defined")
target_database = str(options.database)
if int(target_step) not in STEP_DICT.keys():
    raise Exception("Invalid value 'step'")
target_log_level = options.log_level


# ----------------
# -- Function Part
# ----------------

def run_step(step, database, backup_step):
    step_name = STEP_DICT[step]['name']
    _log("*******************************************************************")
    _log("******** Running Step #%d : %s ********" % (step, step_name))
    _log("*******************************************************************")
    if backup_step:
        # Backup current database
        backup_database(database, step)

    # run SQL Script
    execute_sql_step_file(database, step)

    if step == 1:
        # Upgrade with OpenUpgrade
        set_upgrade_mode(True)
        update_instance(database, 'all', target_log_level)

        # Check if update is OK, otherwise, quit
        proc = run_instance(target_log_level)
        try:
            check_module_state(database, CHECK_MODULE_LIST)
        except Exception as e:
            _log("ERROR during the execution", e)
            raise e
        finally:
            kill_process(proc)

    elif step == 2:
        # Update With OCB
        set_upgrade_mode(False)
        update_instance(database, 'all', target_log_level)

    elif step == 3:
        # Install New Modules
        set_upgrade_mode(False)
        proc = run_instance(target_log_level)
        try:
            install_modules(database, INSTALL_MODULE_LIST)
        except Exception as e:
            _log("ERROR during the execution", e)
        finally:
            kill_process(proc)

    elif step == 4:
        # Uninstall Obsolete Modules
        set_upgrade_mode(False)
        proc = run_instance(target_log_level)
        try:
            uninstall_modules(database, UNINSTALL_MODULE_LIST)
        except Exception as e:
            _log("ERROR during the execution", e)
        finally:
            kill_process(proc)

    elif step == 5:
        # Create Inventories, to populate quants
        set_upgrade_mode(False)
        proc = run_instance(target_log_level)
        try:
            create_inventories(database)
        except Exception as e:
            _log("ERROR during the execution", e)
        finally:
            kill_process(proc)

    # Clean Database
    clean_database(database, step)

# ------------
# -- Main Part
# ------------

# Stop Odoo Service
manage_odoo_process(False)

if '_current' in target_database:
    # Use the target database. (could be instable, but avoid to rerun all
    # the process)
    current_database = target_database
else:
    # Create current database, based on the option database
    current_database = create_new_database(target_database, target_step)

# Do not backup fort the first step
backup_step = False

while target_step <= max(STEP_DICT.keys()):
    run_step(target_step, current_database, backup_step)
    backup_step = True
    target_step += 1

# start Odoo Service
manage_odoo_process(True)
