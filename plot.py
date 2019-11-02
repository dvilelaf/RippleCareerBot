import datetime
import re
from matplotlib import pyplot as plt


idListRegex = r'^\[(\d*, )*\d*\]$'

with open('log.txt', 'r') as fil:
    lines = fil.readlines()
    lines = [i.replace('\n', '') for i in lines]

times = []
idList = []

for i in range(len(lines)-1):
    try:
        time = datetime.datetime.strptime(lines[i], '%a %b %d %H:%M:%S %Z %Y')
        if re.match(idListRegex, lines[i+1]):
            times.append(time)
            ids = lines[i+1].replace('[', '').replace(']', '').replace(' ','').split(',')
            if len(ids) == 1 and ids[0] == '':
                idList.append([])
            else:
                idList.append(ids)
            i += 1
    except ValueError:
        pass

data = {}

for i in range(len(times)):
    date = datetime.datetime.strptime(times[i].strftime('%a %b %d %Y'), '%a %b %d %Y')

    if date in data:
        data[date] += len(idList[i])
    else:
        data[date] = len(idList[i])

print(sum(data.values()))

plt.figure()
plt.bar(data.keys(), data.values())
plt.yticks([0, 1, 2, 3, 4, 5])
plt.show()