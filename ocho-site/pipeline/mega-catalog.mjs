// Download selected master WAVs from Mega, encode 192k MP3 + waveform peaks, delete the WAV.
import { File } from 'megajs'
import fs from 'fs'
import { execFileSync } from 'child_process'
const URL=process.argv[2], PAR=+(process.argv[3]||3)
const sel=JSON.parse(fs.readFileSync('selected.json'))
const isAlt=n=>/(\(.*(mix|instrumental|no brass).*\)|_)/i.test(n.replace(/^\d+ /,''))
sel.sort((a,b)=>isAlt(a.path.split('/').pop())-isAlt(b.path.split('/').pop())||a.path.localeCompare(b.path))
const f=File.fromURL(URL); await f.loadAttributes()
const nodes={}; (function walk(n,p){const path=p?p+'/'+n.name:n.name; if(n.directory)(n.children||[]).forEach(c=>walk(c,path)); else nodes[path]=n})(f,'')
const key=p=>{const parts=p.split('/');return parts[1].slice(0,9)+'/'+parts.slice(2).join('__').replace(/\.wav$/i,'').replace(/[^\p{L}\p{N}_ ().-]/gu,'_')}
let i=0
async function worker(w){
  while(i<sel.length){const x=sel[i++]; const k=key(x.path), mp3='out/'+k+'.mp3', pk='out/'+k+'.json'
    if(fs.existsSync(mp3)&&fs.existsSync(pk))continue
    fs.mkdirSync('out/'+k.split('/')[0],{recursive:true})
    for(let a=1;a<=6;a++){try{
      const buf=await nodes[x.path].downloadBuffer({maxConnections:4}); const wav=`tmp_${w}.wav`; fs.writeFileSync(wav,buf)
      execFileSync('ffmpeg',['-v','error','-y','-i',wav,'-ac','2','-ar','44100','-b:a','320k','-id3v2_version','3',mp3])
      const pcm=execFileSync('ffmpeg',['-v','error','-i',wav,'-ac','1','-ar','2000','-f','s16le','-'],{maxBuffer:1<<28})
      const s=new Int16Array(pcm.buffer,pcm.byteOffset,pcm.length>>1), N=800, step=Math.max(1,Math.floor(s.length/N)), peaks=[]
      for(let b=0;b<N;b++){let m=0;for(let j=b*step;j<Math.min(s.length,(b+1)*step);j++){const v=Math.abs(s[j]);if(v>m)m=v}peaks.push(m)}
      const mx=Math.max(1,...peaks); fs.writeFileSync(pk,JSON.stringify({src:x.path,dur:+(s.length/2000).toFixed(2),peaks:peaks.map(v=>Math.round(v/mx*100))}))
      fs.unlinkSync(wav); console.log(new Date().toISOString(),'ok',k); break
    }catch(e){console.log('err',a,k,String(e.message).slice(0,120)); await new Promise(r=>setTimeout(r,a*a*60000))}}
  }
}
await Promise.all([...Array(PAR)].map((_,w)=>worker(w)))
console.log('DONE')
