// Download each planned WAV from Mega, upload to private R2 ocho-masters, append {key,size,crc} to manifest.jsonl (resumable).
import { File } from 'megajs'
import fs from 'fs'
import zlib from 'zlib'
const plan=JSON.parse(fs.readFileSync('plan.json')), ACC=process.env.CLOUDFLARE_ACCOUNT_ID, TOK=process.env.CLOUDFLARE_API_TOKEN
const done=new Set(fs.existsSync('manifest.jsonl')?fs.readFileSync('manifest.jsonl','utf8').split('\n').filter(Boolean).map(l=>JSON.parse(l).key):[])
const roots={}; async function node(x){if(!roots[x.link]){const f=File.fromURL(x.link);await f.loadAttributes();const m={};(function walk(n,p){const path=p?p+'/'+n.name:n.name;if(n.directory)(n.children||[]).forEach(c=>walk(c,path));else m[path]=n})(f,'');roots[x.link]=m}return roots[x.link][x.path]}
const todo=plan.filter(x=>!done.has(x.key)); let i=0
async function put(key,buf){const u=`https://api.cloudflare.com/client/v4/accounts/${ACC}/r2/buckets/ocho-masters/objects/${key.split('/').map(encodeURIComponent).join('/')}`
  const r=await fetch(u,{method:'PUT',headers:{Authorization:'Bearer '+TOK,'Content-Type':'audio/wav','User-Agent':'ocho'},body:buf}); if(!r.ok)throw new Error('upload '+r.status+' '+(await r.text()).slice(0,150))}
async function worker(){while(i<todo.length){const x=todo[i++]
  for(let a=1;a<=8;a++){try{const n=await node(x);const buf=await n.downloadBuffer({maxConnections:4})
    const crc=zlib.crc32(buf); await put(x.key,buf)
    fs.appendFileSync('manifest.jsonl',JSON.stringify({key:x.key,size:buf.length,crc})+'\n'); console.log(new Date().toISOString(),'ok',x.key,buf.length); break
  }catch(e){console.log('err',a,x.key,String(e.message).slice(0,150)); await new Promise(r=>setTimeout(r,Math.min(a*a,30)*60000))}}}}
await Promise.all([0,1,2].map(worker)); console.log('DONE', fs.readFileSync('manifest.jsonl','utf8').split('\n').filter(Boolean).length)
