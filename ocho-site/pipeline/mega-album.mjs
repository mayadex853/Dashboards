// Same as ../mega/process.mjs for a single-album share link: mixes only, output into ../mega/out/<ALBUM-ID>/
import { File } from 'megajs'
import fs from 'fs'
import { execFileSync } from 'child_process'
const [,,URL,ALB]=process.argv, OUT='../mega/out/'
const f=File.fromURL(URL); await f.loadAttributes()
const all=[]; (function walk(n,p){const path=p?p+'/'+n.name:n.name; if(n.directory)(n.children||[]).forEach(c=>walk(c,path)); else all.push([path,n])})(f,'')
const skip=/stem|export all|backup|archive|\/z_|\/mp3\/|dry|wet/i
for(const [p,n] of all.filter(([p])=>/\.csv$/i.test(p)&&/OCHO_00\d\d( \(\d\))?\.csv$/.test(p))){fs.mkdirSync('../mega/meta/apm',{recursive:true});fs.writeFileSync('../mega/meta/apm/'+ALB+'__'+p.split('/').pop(),await n.downloadBuffer())}
const sel=all.filter(([p])=>/\.wav$/i.test(p)&&!skip.test(p))
let i=0
async function worker(w){while(i<sel.length){const [p,n]=sel[i++]; const k=ALB+'/'+p.split('/').slice(1).join('__').replace(/\.wav$/i,'').replace(/[^\p{L}\p{N}_ ().-]/gu,'_')
  const mp3=OUT+k+'.mp3',pk=OUT+k+'.json'; if(fs.existsSync(mp3)&&fs.existsSync(pk))continue; fs.mkdirSync(OUT+ALB,{recursive:true})
  for(let a=1;a<=6;a++){try{const buf=await n.downloadBuffer({maxConnections:4}); const wav=`tmp_${ALB}_${w}.wav`; fs.writeFileSync(wav,buf)
    execFileSync('ffmpeg',['-v','error','-y','-i',wav,'-ac','2','-ar','44100','-b:a','192k',mp3])
    const dur=+execFileSync('ffprobe',['-v','error','-show_entries','format=duration','-of','csv=p=0',wav]).toString().trim()
    fs.writeFileSync(pk,JSON.stringify({src:'x/'+p,dur:+dur.toFixed(2),peaks:[]})); fs.unlinkSync(wav); console.log(new Date().toISOString(),'ok',k); break
  }catch(e){console.log('err',a,k,String(e.message).slice(0,120)); await new Promise(r=>setTimeout(r,a*a*60000))}}}}
await Promise.all([0,1,2].map(worker)); console.log('DONE')
