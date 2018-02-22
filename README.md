golos-scripts
=============

This is a python scripts collection for golos blockchain network.

* `change_password.py` - change all account keys using random generated password or user-supplied
* `transfer.py` - transfer some money to another account
* `transfer_to_vesting.py` - transfer GOLOS to vesting balance (Golos Power)
* `get_balance.py` - display account balances
* `get_balance_multi.py` - display balances of multiple accounts
* `estimate_upvote.py` - estimate author payout simulating someone's upvote
* `get_votnig_power.py` - calculate current voting power of specified account
* `get_bandwidth.py` - calculate used bandwidth of the account. Can be used in scripting as monitoring tool (`-w 75 -q`)
* `estimate_median_price.py` - look up current witnesses price feeds and calculate new expected median price

To use in virtualenv
--------------------

```
mkdir venv
virtualenv -p python3 venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```
