# SheepBox
Helpful Autodesk Maya related tools to help speed up my workflow

# Installation
- Clone this repo to your ./Documents/maya/ folder.
- Run `internalVar -usd` inside of a mel line within Maya.
This will give you the location of your UserSetup.py file.
- Add these lines to the userSetup.py file:
```python
import os
import sys

home = os.path.expanduser("~")
sys.path.append(os.path.join(home, 'maya', 'SheepBox', 'scripts'))
print('Added SheepBox')
```
- Within Maya, you'll now be able to run `import SheepBox` on launch and have access to the tools.
