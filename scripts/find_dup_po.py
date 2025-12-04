from collections import defaultdict
p=r'C:/Users/talga/Desktop/DJshop1/locale/en/LC_MESSAGES/django.po'
ids=defaultdict(list)
with open(p,encoding='utf-8') as f:
    lines=f.readlines()
for i,l in enumerate(lines,1):
    if l.strip().startswith('msgid '):
        s=l.strip()[6:]
        ids[s].append(i)
for k,v in ids.items():
    if len(v)>1:
        print(k, v)
print('done')
