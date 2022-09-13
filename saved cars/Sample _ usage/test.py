import os
import re
pattern = r'([0-9])+\.pkl'
listt = []
print(os.listdir())
print(sorted(os.listdir()))
for name in os.listdir():
    if re.match(pattern, name):
        listt.append(int(name[:len(name) - 4]))
print(listt)
