import time
import json
from beem import Hive
from beem.account import Account
from beem.instance import set_shared_blockchain_instance
from datetime import datetime, timedelta
from dateutil.parser import parse
from sql import save_max_op_count,  get_saved_max_op_count, save_results_to_db
import sql
import configparser


config = configparser.ConfigParser()
config.read('config.ini')

user = config.get('base', 'account_name')
if user is None:
    raise ValueError(f'Falta la variable requerida "account_name" en el archivo de configuración: {config.filename}')

max_ops_per_request = config.getint('base', 'max_ops_per_request', fallback=1000)
nodes = [node.strip() for node in config.get('base', 'nodes', fallback='https://hive-api.arcange.eu,https://api.hive.blog,https://anyx.io').split(',')]
dias = config.getint('base', 'days', fallback=7)


def get_next_api_url():
    node_list = nodes
    while True:
        for api_url in node_list:
            yield api_url

next_api_url = get_next_api_url()


all_results_obtained = False
def switch_hive_node():
    global all_results_obtained
    if not all_results_obtained:
        api_url = next(next_api_url)
        print(f"Switching to new Hive API node: {api_url}")
        hive_instance = Hive(node=api_url)
        set_shared_blockchain_instance(hive_instance)

switch_hive_node()


def get_max_op_count(account_name):
    hive_instance = Hive()  # Asegúrese de que esto esté utilizando el nodo API correcto
    account = Account(account_name, blockchain_instance=hive_instance)
    max_op_count = account.virtual_op_count()
    return max_op_count

def get_hp_delegations(account_name):
    hive_instance = Hive()
     # Asegúrese de que esto esté utilizando el nodo API correcto
    account = Account(account_name, blockchain_instance=hive_instance)

    max_op_count = get_max_op_count(account_name)
    saved_max_op_count = get_saved_max_op_count()
    print (f" Tiene una cantidad de op: {max_op_count}")
    stop_value = 1 if saved_max_op_count is None else saved_max_op_count

    
    if stop_value == max_op_count:
        #print(f"No hay nada que ejectutar {account_name}.")
        #return []


    results = {}
    ops_processed = 0

    ### Ingresa la fecha filtro

    days_stop =  dias
    cutoff_date = datetime.utcnow() - timedelta(days=days_stop)

    for operation in account.history_reverse(start=max_op_count, stop=stop_value, use_block_num=False):
        if ops_processed >= 1000:
            ops_processed = 0
            switch_hive_node()
            hive_instance = Hive()  ### utilizando el nodo API correcto
            account = Account(account_name, blockchain_instance=hive_instance)

        if operation["type"] == "delegate_vesting_shares":
            if operation["delegatee"] == account_name:
                vests = float(operation["vesting_shares"]["amount"])
                vests = round(float(vests), 4)
                mvests = vests / 1000000
                timestamp =  parse(operation["timestamp"])
                if timestamp >= cutoff_date:
                    continue

                

    
                
                
                hp = hive_instance.vests_to_hp(mvests, use_stored_data=True) 
                
                current_delegation = {
                    "Delegador": operation["delegator"],
                    "HP delegado": round(hp, 2),
                    "Fecha": operation["timestamp"]
                }

                if hp != 0:
                    if operation["delegator"] in results:
                        existing_delegation = results[operation["delegator"]]
                        if existing_delegation["Fecha"] < current_delegation["Fecha"]:
                            results[operation["delegator"]] = current_delegation
                    else:
                        results[operation["delegator"]] = current_delegation

        ops_processed += 1

    return list(results.values())




if __name__ == "__main__":
    sql.init_db()
    account_name = user # Reemplace con el nombre de la cuenta de Hive que desea consultar
    
    attempts = 0

    max_op_count = get_max_op_count(account_name)

    max_attempts = 3
    while not all_results_obtained and attempts < max_attempts:
        try:
            hp_delegations = get_hp_delegations(account_name)
            save_max_op_count(max_op_count)
            if hp_delegations:
                all_results_obtained = True
                print(json.dumps(hp_delegations, indent=2))
                save_results_to_db(hp_delegations)  # Guarda los resultados en la base de datos
            else:
                attempts += 1
                print(f"Attempt {attempts}: No results obtained")

            
        except Exception as e:
            print(f"Error: {e}")

        if not all_results_obtained:
            time.sleep(3)
            switch_hive_node()
    if attempts >= max_attempts:
        print("Se consó.")
    print("Proceso finalizado. Todos los resultados han sido obtenidos.")