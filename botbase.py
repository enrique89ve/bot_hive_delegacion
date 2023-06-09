
import datetime
import json

import sys
import datetime as dt
from beem.amount import Amount
from beem.utils import parse_time, formatTimeString, addTzInfo
from beem.instance import set_shared_steem_instance
from beem import Hive
from beem.snapshot import AccountSnapshot

import datetime
import time
from beem.account import Account
from beem.amount import Amount

from datetime import datetime, timedelta
from beem.account import Account
from beem.amount import Amount

import sys
import datetime as dt
from beem.amount import Amount
from beem.utils import parse_time, formatTimeString, addTzInfo
from beem.instance import set_shared_steem_instance
from beem import Hive
from beem.snapshot import AccountSnapshot
from beem.instance import set_shared_blockchain_instance
from beem.account import Account
from beem.amount import Amount
import re
from configparser import ConfigParser 




hived_nodes = [

  'https://api.deathwing.me',
  'https://anyx.io',
]

hive = Hive(node=hived_nodes)



#Read config.ini file
config_object = ConfigParser()
config_object.read("config.ini")

#Get user
userinfo = config_object["USERINFO"]

userpay = userinfo["userpay"] 

usermain = userinfo["useradm"] 


acc = Account(usermain, blockchain_instance = hive)


def delegado():

	hp_dele = acc.get_vesting_delegations()

	hp_vests = Amount("0 VESTS")

	for hp in hp_dele:


		hp_vests+= Amount(hp['vesting_shares'])












	hp_total_del =  hive.vests_to_hp(hp_vests)




	return hp_total_del





def getRewards():


	stop = datetime.utcnow() - timedelta(days=7)
	reward_vests = Amount("0 VESTS")
	for reward in acc.history_reverse(stop=stop, only_ops=["curation_reward"]):
		reward_vests+= Amount(reward['reward'])
	curation_rewards_HP =  hive.vests_to_hp(reward_vests)
	
	#print("Las recompensas de aliento de los últimos días son %.2f HP" % curation_rewards_HP)

	return curation_rewards_HP


def getRw():

	stop = datetime.utcnow() - timedelta(days=30)
	reward_vests = Amount("0 VESTS")
	for reward in acc.history_reverse(stop=stop, only_ops=["curation_reward"]):
		reward_vests += Amount(reward['reward'])
	curation_rewards_HP_7 = hive.vests_to_hp(reward_vests)
	
	#print("Las recompensas de aliento de los últimos días son %.2f HP" % curation_rewards_HP)

	return curation_rewards_HP_7


def gettotalhp():
	acc = Account(usermain, blockchain_instance = hive )
	hp = acc.get_steem_power(onlyOwnSP=False)

	return hp



def getapr():

	curation = (getRewards())
	hivep =  (gettotalhp())

	APR = curation * 52 / hivep

	aprt = float(APR) * 100

	return aprt

#Your last 7 days of curation * 52 / your total HIVE POWER = Curation APR





def gettotalhppropio():
	acc = Account(usermain, blockchain_instance = hive )
	hp = acc.get_steem_power(onlyOwnSP=True)

	return hp





def hp_efectivo():


	cor = float(delegado())
	hp =  float(gettotalhppropio())



	return hp - cor



def cura7():
  cur = acc.curation_stats()

  return cur
	


