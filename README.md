golos-scripts
=============

![test](https://github.com/bitfag/golos-scripts/workflows/test/badge.svg)
[![Documentation
Status](https://readthedocs.org/projects/golos-scripts/badge/?version=latest)](https://golos-scripts.readthedocs.io/en/latest/?badge=latest)

This is a python scripts collection for golos blockchain network.

For documentation on reusable parts, pleasee see [documentation on
reathedocs](https://golos-scripts.readthedocs.io/en/latest/).

* `donation.py` - make a donation for post
* `change_password.py` - change all account keys using random generated password or user-provided
* `calc_vesting_reward.py` - calculate profit from vesting holdings
* `inflation.py` - calculate current inflation or model long-term inflation
* `generate_keypair.py` - just generate private and public keypair
* `transfer.py` - transfer some money to another account
* `transfer_to_vesting.py` - transfer GOLOS to vesting balance (Golos Power)
* `get_balance.py` - display account balances
* `get_balance_multi.py` - display balances of multiple accounts
* `estimate_median_price.py` - look up current witnesses price feeds and calculate new expected median price
* `estimate_gbg_debt.py` - script to estimate system debt in GBG, see [ESTIMATE\_GBG\_DEBT](ESTIMATE_GBG_DEBT.md)
* `get_post.py` - get and print post/comment
* `get_props.py` - script to display global properties
* `get_median_props.py` - script to display current votable parameters
* `get_voting_power.py` - calculate current voting power of specified account
* `get_bandwidth.py` - calculate used bandwidth of the account. Can be used in scripting as monitoring tool (`-w 75 -q`)
* `get_vesting_withdraws.py` - find all vesting withdrawals with rates and dates
* `get_conversion_requests.py` - find all GBG conversion requests
* `get_feed_history.py` - script to obtain GBG price feed history
* `get_miner_queue.py` - script to display miner queue
* `get_median_voting.py` - get witnesses voting for a particular chain param
* `get_inflation_voting.py` - show voting for inflation targets properties
* `get_witness.py` - script to obtain current info for specified witness
* `get_witnesses.py` - script to display known witnesses, sorted by votes
* `post.py` - publish post to the blockchain
* `sea_biom.py` - print Golos Power for each sea habitant level
* `create_account.py` - create child account
* `find_transfers.py` - scan account history to find transfers
* `upvote.py` - upvote/downvote post or comment
* `withdraw_vesting.py` - withdraw from vesting balance of one account to specified account
* `withdraw_vesting_multi.py` - withdraw from vesting balance of multiple accounts to specified account
* `delegate_vesting_shares.py` - script to delegate vesting shares
* `witness_approve.py` - vote for witness
* `witness_disapprove.py` - remove vote from witness
* `update_witness.py` - script to manipulate witness data in the blockchain, see [UPDATE\_WITNESS](UPDATE_WITNESS.md)

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

Installation via pip
--------------------

With pip you can install *golosscripts* package, which provides various functions and helpers:

```
pip install golosscripts
```

How to use
----------

1. Prepare working environment using virtualenv (see above)
2. Copy `common.yml.example` to `common.yml` and change variables according to your needs
