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
* `get_post.py` - get and print post/comment
* `get_voting_power.py` - calculate current voting power of specified account
* `get_bandwidth.py` - calculate used bandwidth of the account. Can be used in scripting as monitoring tool (`-w 75 -q`)
* `get_vesting_withdraws.py` - find all vesting withdrawals with rates and dates
* `get_conversion_requests.py` - find all GBG conversion requests
* `post.py` - publish post to the blockchain
* `create_account.py` - create child account
* `find_transfers.py` - scan account history to find transfers
* `find_rewards.py` - scan account history to find author or curation rewards
* `withdraw_vesting.py` - withdraw from vesting balance of one account to specified account
* `withdraw_vesting_multi.py` - withdraw from vesting balance of multiple accounts to specified account
* `delegate_vesting_shares.py` - script to delegate vesting shares
* `witness_approve.py` - vote for witness
* `witness_disapprove.py` - remove vote from witness

Requirements
------------

* golos node 0.18+

Installation via poetry
-----------------------

1. Install [poetry](https://python-poetry.org/docs/)
2. Run `poetry install` to install the dependencies
3. Copy `common.yml.example` to `common.yml` and change variables according to your needs
4. Now you're ready to run scripts:


```
poetry shell
./script.py
```

How to use
----------

1. Prepare working environment using virtualenv (see above)
2. Copy `common.yml.example` to `common.yml` and change variables according to your needs
