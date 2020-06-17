# standinManager
standinManager is a tool for Maya to change massively properties in StandIn nodes.

<img src="https://github.com/AlbertoGZ-dev/standinManager/blob/master/standinManagerUI.png"></img>


## Setup

#### Manual installation

Place the *standinManager.py* and *\_\_init\_\_.py* files in a folder named *standinManager* in your Maya scripts directory and create a python shelf button with the following code:

```python
from standinManager import standinManager

try:
    md_win.close()
except:
    pass
md_win = standinManager.standinManager(parent=standinManager.getMainWindow())
md_win.show()
md_win.raise_()
```
