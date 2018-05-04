golos-scripts
=============

This is a python scripts collection for golos blockchain network.

* `change_password.py` - change all account keys using random generated password or user-provided
* `generate_keypair.py` - just generate private and public keypair
* `transfer.py` - transfer some money to another account
* `transfer_to_vesting.py` - transfer GOLOS to vesting balance (Golos Power)
* `get_balance.py` - display account balances
* `get_balance_multi.py` - display balances of multiple accounts
* `estimate_upvote.py` - estimate author payout simulating someone's upvote
* `estimate_curator_rewards.py` - estimate real curators rewards
* `estimate_median_price.py` - look up current witnesses price feeds and calculate new expected median price
* `get_voting_power.py` - calculate current voting power of specified account
* `get_bandwidth.py` - calculate used bandwidth of the account. Can be used in scripting as monitoring tool (`-w 75 -q`)
* `get_vesting_withdraws.py` - find all vesting withdrawals with rates and dates
* `get_conversion_requests.py` - find all GBG conversion requests
* `create_account.py` - create child account
* `find_transfers.py` - scan account history to find transfers
* `withdraw_vesting.py` - withdraw from vesting balance of one account to specified account
* `withdraw_vesting_multi.py` - withdraw from vesting balance of multiple accounts to specified account

Requirements
------------

* golos node 0.17+

Installation using pipenv
-------------------------

1. Install [pipenv](https://docs.pipenv.org/).
2. Run the following code

```
pipenv install
```

How to use
----------

1. Prepare working environment using virtualenv (see above)
2. Copy `common.yml.example` to `common.yml` and change variables according to your needs
3. Run the scripts:

```
pipenv shell
./script.py
exit
```

or

```
pipenv run ./script.py
```
