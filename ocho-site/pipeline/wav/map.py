# Map Mega WAV paths (wavs.json from list.mjs) to the MP3 names in ocho-audio -> plan.json for dl.mjs.
import sys,json,os,urllib.request,collections
sys.argv=['x','/nonexistent']
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))
import tracks
acc=os.environ['CLOUDFLARE_ACCOUNT_ID'];tok=os.environ['CLOUDFLARE_API_TOKEN']
keys=set();cur=None
while True:
    u=f"https://api.cloudflare.com/client/v4/accounts/{acc}/r2/buckets/ocho-audio/objects?per_page=1000&prefix=OCHO-"+(f"&cursor={cur}" if cur else "")
    r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"Authorization":"Bearer "+tok,"User-Agent":"ocho"})))
    keys|={o['key'] for o in r['result']}
    ri=r.get('result_info') or {}; cur=ri.get('cursor')
    if not ri.get('is_truncated'):break
wavs=json.load(open('wavs.json'));plan=[];miss=[];seen=collections.Counter()
for w in wavs:
    src=os.path.splitext(w['path'].split('/')[-1])[0]
    base,label=tracks.split_version(src)
    fn=f"{tracks.slug(base)}{'--'+tracks.slug(label) if label else ''}"
    k=f"{w['alb']}/{fn}.mp3"
    if k in keys: plan.append(dict(w,key=f"{w['alb']}/{fn}.wav",mp3=k)); seen[k]+=1
    else: miss.append(w['path'])
dup=[k for k,c in seen.items() if c>1]
nomaster=sorted(keys-set(seen))
json.dump(plan,open('plan.json','w'))
print('plan',len(plan),'unmatched wav',len(miss),'dup',len(dup),'mp3 without wav',len(nomaster))
print('unmatched sample',miss[:8]);print('dups',dup[:5]);print('nomaster',nomaster[:10])
