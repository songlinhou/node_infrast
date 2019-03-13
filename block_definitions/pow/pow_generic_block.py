import utils
import json


class PoWGenericBlock:
  def __init__(self,height,prev_hash,nounce=0):

    """
    Assign values to this block instance.

    the attributes are:
    
    1. height <int>:starting from 1
    2. prev_hash <str>:value of the hash of the previous block
    3. nounce <int>: starting from 0. The value to be computed.
    4. transactions <list>: a list of transactions
    """
    self.height = height
    self.prev_hash = prev_hash
    self.nounce = nounce
    self.transactions = [] # type should be PoWGenericTransaction

  def add_transaction(self,transaction):
    """
    append a new transaction to this block.
    """
    if type(transaction) != PoWGenericTransaction:
      raise Exception('TYPEERROR','transaction should be type of "PoWGenericTransaction" but got {}'.format(type(transaction)))
    if not transaction.is_validation_passed():
      print 'The transaction is not valid. Skipped...'
      return
    self.transactions.append(transaction)

  def __str__(self):
    transaction_list = [tx.to_dict() for tx in self.transactions]
    content = {
      'height':self.height,
      'prev_hash':self.prev_hash,
      'nounce':self.nounce,
      'transactions':transaction_list
    }
    return json.dumps(content)
  
  def to_dict(self):
    transaction_list = [tx.to_dict() for tx in self.transactions]
    content = {
      'height':self.height,
      'prev_hash':self.prev_hash,
      'nounce':self.nounce,
      'transactions':transaction_list
    }
    return content
    



class PoWGenericTransaction:
  def __init__(self,initiator,tx_timestamp,sender,receiver,amount,fromNodeID,timestamp):
    """
    initiator: the name of the node who firstly initiate this transaction
    tx_timestamp: when this transaction is fristly initiated
    sender: the name of the node who made the transfer
    receiver: the name of the node who receive the transfer
    amount: the money in transfer
    fromNodeID: who pass this transaction to me
    timestamp: the timestamp of this transaction being added.
    """
    self.initiator = initiator
    self.tx_timestamp = tx_timestamp
    self.sender = sender
    self.receiver = receiver
    self.amount = amount
    self.fromNodeID = fromNodeID
    self.timestamp = timestamp


  def is_validation_passed(self):
    if not utils.is_non_empty_str(self.initiator):
      return False
    tx_timestamp = utils.get_timestamp_from_str(self.tx_timestamp)
    if tx_timestamp == None:
      return False
    if not utils.is_non_empty_str(self.sender):
      return False
    if not utils.is_non_empty_str(self.receiver):
      return False
    if not utils.is_non_negative_int(self.amount):
      return False
    if not utils.is_non_empty_str(self.fromNodeID):
      return False
    timestamp = utils.get_timestamp_from_str(self.timestamp)
    if timestamp == None:
      return False
    return True
  def __str__(self):
    content = {
      'initiator':self.initiator,
      'tx_timestamp':self.tx_timestamp,
      'sender':self.sender,
      'receiver':self.receiver,
      'amount':self.amount,
      'fromNodeID':self.fromNodeID,
      'timestamp':self.timestamp
    }
    return json.dumps(content)
  def to_dict(self):
    content = {
      'initiator':self.initiator,
      'tx_timestamp':self.tx_timestamp,
      'sender':self.sender,
      'receiver':self.receiver,
      'amount':self.amount,
      'fromNodeID':self.fromNodeID,
      'timestamp':self.timestamp
    }
    return content