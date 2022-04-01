from brownie import network
import pytest
from scripts.deploy_lottery import deploy_lottery
from scripts.helper_scripts import (
    LOCAL_DEVELOPMENT_ENVIRONMENTS,
    get_account,
    fund_with_link,
)
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_DEVELOPMENT_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntryFees()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntryFees()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntryFees()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
