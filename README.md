# ConnectBot
A simple bot that plays Connect Four

## How do I play this bot?
The bot is contained inside the Board class and was built to operate on IPython

Your best bet is opening up a Jupyter terminal and doing the following:
```python
import ConnectBot

B = ConnectBot.Board()

B.play()
```

The play method will take in two optional kwargs, player and difficulty. If player is set to 0 you take the first move, 1 you take the second move, -1 is for two human players. Difficulty is set to 3 by default and is computationally expensive above 4.
