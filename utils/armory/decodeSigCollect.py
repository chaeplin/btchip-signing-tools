import os, sys, inspect
# Add ../../BitcoinArmory to path so it works as if we were importing it from the inside.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../BitcoinArmory")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from armoryengine.Transaction import *
from armoryengine.ArmoryUtils import binary_to_hex, hex_to_binary
import json
from distutils import util
import requests
import pprint
pp = pprint.PrettyPrinter(indent=2)

isTestnet = len(sys.argv) > 1 and sys.argv[1] == '--testnet'
testnetBroadcast = "https://tbtc.blockr.io/api/v1/tx/push"
mainnetBroadcast = "https://blockchain.info/pushtx"


# Broadcast tx using a web service.
def broadcastTx(rawTx):
  if isTestnet:
    r = requests.post(testnetBroadcast, data={'hex': rawTx})
    print "Transaction sent to blockr.io. Response:"
  else:
    r = requests.post(mainnetBroadcast, data={'tx': rawTx})
    print "Transaction sent to blockchain.info. Response:"
  print(r.text)


# We've had SIGCOLLECTs fail to broadcast from Armory. Recently we had one with multiple
# signed inputs completely fail with a `string index out of range` error in Armory.
#
# This tool takes in a SIGCOLLECT block and prints transaction details and a raw transaction that can be
# broadcast via bitcoind or any blockchain API like blockchain.info.
#
# You need to have the BitcoinArmory repo cloned in the root directory of the signer repo.
def decodeSigCollect():
  print "Paste your TXSIGCOLLECT below and press <enter>:\n"
  stopAt = "================================================================"
  SIGCOLLECT = ""
  for line in iter(raw_input, stopAt):
    SIGCOLLECT += line + "\n"

  SIGCOLLECT += stopAt

  a = UnsignedTransaction()
  tx = a.unserializeAscii(SIGCOLLECT)

  txJSON = tx.toJSONMap()

  pp.pprint(txJSON)
  print "\n"

  print "\nTransaction summary:\n"
  tx.pprint()
  tx.evaluateSigningStatus().pprint()
  print "\n"

  raw = binary_to_hex(tx.getSignedPyTx(doVerifySigs=False).serialize())
  if tx.evaluateSigningStatus().canBroadcast:
    confirmed = raw_input("Broadcast Transaction? [y/N]: ") or "false"
    if util.strtobool(confirmed):
      return broadcastTx(raw)
    else:
      print "Not broadcasting transaction."
  else:
    print "Transaction not complete."

  print "\nRaw Transaction:\n"
  print raw

  if isTestnet:
      print "\nBroadcast Transaction:\nhttp://tbtc.blockr.io/tx/push\n"
  else:
      print "\nBroadcast Transaction:\nhttps://blockchain.info/pushtx\n"

if __name__ == "__main__":
  decodeSigCollect()
