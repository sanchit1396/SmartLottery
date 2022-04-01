from brownie import Lottery, network, config, accounts, web3, exceptions
import pytest
from scripts.deploy_lottery import deploy_lottery

from scripts.helper_scripts import (
    LOCAL_DEVELOPMENT_ENVIRONMENTS,
    fund_with_link,
    get_account,
    get_contract,
)


def test_get_entry_fees():
    if network.show_active() not in LOCAL_DEVELOPMENT_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    expected_entrance_fee = web3.toWei(2.5, "ether")
    entrance_fee = lottery.getEntryFees()
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_DEVELOPMENT_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntryFees()})


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_DEVELOPMENT_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntryFees()})
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_DEVELOPMENT_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntryFees()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_DEVELOPMENT_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntryFees()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntryFees()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntryFees()})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
