#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 17:58:00 2019

@author: MacBook
"""

def reply_ping_with_pong(state):
  """
  state:{
          version: int,
          timestamp: str,
          fromID: str,
          toID: str,
        }
  """
  return "pong: receive from {} at {}".format(state['fromID'],state['timestamp'])