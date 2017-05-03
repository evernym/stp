from stp_core.crypto.util import randomSeed
from stp_core.loop.eventually import eventually
from stp_core.network.port_dispenser import genHa
from stp_core.test.helper import Printer, prepStacks, chkPrinted
from stp_zmq.test.helper import genKeys
from stp_zmq.zstack import ZStack


def testRestricted2ZStackCommunication(tdir, looper):
    """
    Create 2 ZStack and make them send and receive messages.
    Both stacks allow communication only when keys are shared
    :return:
    """
    names = ['Alpha', 'Beta']
    genKeys(tdir, names)
    alphaP = Printer(names[0])
    betaP = Printer(names[1])

    alpha = ZStack(names[0], ha=genHa(), basedirpath=tdir, msgHandler=alphaP.print,
                   restricted=True)
    beta = ZStack(names[1], ha=genHa(), basedirpath=tdir, msgHandler=betaP.print,
                  restricted=True)

    prepStacks(looper, alpha, beta, connect=True, useKeys=True)
    alpha.send({'greetings': 'hi'}, beta.name)
    beta.send({'greetings': 'hello'}, alpha.name)

    looper.run(eventually(chkPrinted, alphaP, {'greetings': 'hello'}))
    looper.run(eventually(chkPrinted, betaP, {'greetings': 'hi'}))


def testUnrestricted2ZStackCommunication(tdir, looper):
    """
    Create 2 ZStack and make them send and receive messages.
    Both stacks allow communication even when keys are not shared
    :return:
    """
    names = ['Alpha', 'Beta']
    alphaP = Printer(names[0])
    betaP = Printer(names[1])
    alpha = ZStack(names[0], ha=genHa(), basedirpath=tdir, msgHandler=alphaP.print,
                   restricted=False, seed=randomSeed())
    beta = ZStack(names[1], ha=genHa(), basedirpath=tdir, msgHandler=betaP.print,
                  restricted=False, seed=randomSeed())

    prepStacks(looper, alpha, beta, connect=True, useKeys=True)
    alpha.send({'greetings': 'hi'}, beta.name)
    beta.send({'greetings': 'hello'}, alpha.name)

    looper.run(eventually(chkPrinted, alphaP, {'greetings': 'hello'}))
    looper.run(eventually(chkPrinted, betaP, {'greetings': 'hi'}))


def testZStackSendMethodReturnsFalseIfDestinationIsUnknown(tdir, looper):
    """
    Checks: https://evernym.atlassian.net/browse/SOV-971
    1. Connect two stacks 
    2. Disconnect a remote from one side
    3. Send a message from disconnected remote
    Expected result: the stack's method 'send' should not 
        fail just return False
    """
    names = ['Alpha', 'Beta']
    genKeys(tdir, names)
    alphaP = Printer(names[0])
    betaP = Printer(names[1])

    alpha = ZStack(names[0], ha=genHa(), basedirpath=tdir,
                   msgHandler=alphaP.print, restricted=True)
    beta = ZStack(names[1], ha=genHa(), basedirpath=tdir,
                  msgHandler=betaP.print, restricted=True)
    prepStacks(looper, alpha, beta, connect=True, useKeys=True)
    # disconnect remote
    alpha.getRemote(beta.name).disconnect()
    # check send message returns False
    assert alpha.send({'greetings': 'hello'}, beta.name) is False

"""
TODO:
* Create ZKitStack, which should maintain a registry and method to check for any
disconnections and do reconnections if found.
* Need a way to run current tests against both stack types, or at least a way to
set a fixture parameter to do so.
* ZNodeStack
* ZClientStack
* test_node_connection needs to work with ZMQ
* test/pool_transactions package

"""