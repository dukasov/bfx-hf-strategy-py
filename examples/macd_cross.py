#!/usr/bin/env python3

import sys
import asyncio
sys.path.append('../')

from hfstrategy import Strategy
from bfxhfindicators import MACD

# Initialise strategy
strategy = Strategy(
  symbol='tBTCUSD',
  indicators={
    'macd': MACD([10, 26, 9]),
  },
  exchange_type=Strategy.ExchangeType.EXCHANGE,
  logLevel='INFO'
)

@strategy.on_enter
async def enter(update):
  macd = strategy.get_indicators()['macd']
  current = macd.v()
  previous = macd.prev()

  if not previous:
    return

  is_cross_over = (current['macd'] >= current['signal'] and 
                   previous['macd'] <= previous['signal'])
  is_crossed_under = (current['macd'] <= current['signal'] and
                      previous['macd'] >= previous['signal'])
  
  if is_crossed_under:
     await strategy.open_short_position_market(mtsCreate=update.mts, amount=1)
  elif is_cross_over:
     await strategy.open_long_position_market(mtsCreate=update.mts, amount=1)

@strategy.on_update_short
async def update_short(update, position):
  macd = strategy.get_indicators()['macd']
  if macd['macd'] > macd['signal']:
    await strategy.close_position_market(mtsCreate=update.mts)

@strategy.on_update_long
async def update_long(update, position):
  macd = strategy.get_indicators()['macd']
  if macd['macd'] < macd['signal']:
    await strategy.close_position_market(mtsCreate=update.mts)


from hfstrategy import Executor
exe = Executor(strategy, timeframe='1hr')

# Backtest offline
exe.offline(file='btc_candle_data.json')

# Backtest with data-backtest server
# import time
# now = int(round(time.time() * 1000))
# then = now - (1000 * 60 * 60 * 24 * 2) # 5 days ago
# exe.with_data_server(then, now)

# Execute live
# import os
# API_KEY=os.getenv("BFX_KEY")
# API_SECRET=os.getenv("BFX_SECRET")
# exe.live(API_KEY, API_SECRET)

# Backtest live
# exe.backtest_live()
