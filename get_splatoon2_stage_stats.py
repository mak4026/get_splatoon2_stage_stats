import yaml
import twitter
import re
from datetime import datetime
from collections import Counter

with open('config.yaml', 'r') as yml:
    config = yaml.load(yml)

api = twitter.Api(consumer_key=config['consumer_key'],
                  consumer_secret=config['consumer_secret'],
                  access_token_key=config['access_token_key'],
                  access_token_secret=config['access_token_secret'],
                  )


regex = r"(?P<date>\d+/\d+) (?P<time>\d+):\d+.*\n+▼ナワバリ\n.+\n+▼(?P<rule>.+)\n.+\n+▼.+\n.+"
matcher = re.compile(regex)

results = {t: Counter() for t in range(1, 25, 2)}


statuse = api.GetUserTimeline(screen_name='splatoon2_stage', count=200)

for _ in range(3):
    end = False
    for s in statuse:
        res = matcher.match(s.text)
        if res is None: continue # splat fest
        tweet_time = datetime.fromtimestamp(s.created_at_in_seconds)
        if datetime.strptime(config['start_date'], '%Y-%m-%d') <= tweet_time <= datetime.strptime(config['last_date'], '%Y-%m-%d'):
            time = int(res.group('time'))
            rule = res.group('rule')
            results[time][rule] += 1
        elif datetime.strptime(config['start_date'], '%Y-%m-%d') > tweet_time:
            end = True
            break
    if end:
        break
    else:
        max_id = min(statuse, key=lambda x: x.id).id-1
        statuse = api.GetUserTimeline(screen_name='splatoon2_stage', count=200, max_id=max_id)

print(config['start_date'])
print(config['last_date'])

import matplotlib.pyplot as plt
import numpy as np

w = 0.4
x = np.array(range(1,25,2))
y_area = np.array([r['ガチエリア'] for r in results.values()])
y_yagura = np.array([r['ガチヤグラ'] for r in results.values()])
y_hoko = np.array([r['ガチホコ'] for r in results.values()])
y_asari = np.array([r['ガチアサリ'] for r in results.values()])

plt.bar(x, y_area, width=w, label="area", align='center')
plt.bar(x+w, y_yagura, width=w, label='yagura', align='center')
plt.bar(x+2*w, y_hoko, width=w, label='hoko', align='center')
plt.bar(x+3*w, y_asari, width=w, label='asari', align='center')
plt.legend(loc="best")

plt.xticks(x + w*1.5, x)
plt.show()