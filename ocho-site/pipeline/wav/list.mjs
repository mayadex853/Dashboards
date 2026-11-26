// List master WAVs (mixes only) in the Mega shares -> wavs.json. Run from a scratch dir with megajs installed.
import { File } from 'megajs'
import fs from 'fs'
const links=[['https://mega.nz/folder/0bt1wJaL#8dYr_WZLa_bTmCp2PwHjYA',null],['https://mega.nz/folder/cfVUDJBK#8tUY_0BjEDZbPUKMtC2hEA','OCHO-0008'],['https://mega.nz/folder/QaNwhK7K#syGHwI_BboIaU14-a6uvgg','OCHO-0014']]
const skip=/stem|export all|backup|archive|\/z_|\/mp3\/|dry|wet/i, out=[]
for(const [u,alb] of links){const f=File.fromURL(u); await f.loadAttributes()
  ;(function walk(n,p){const path=p?p+'/'+n.name:n.name; if(n.directory)(n.children||[]).forEach(c=>walk(c,path)); else if(/\.wav$/i.test(path)&&!skip.test(path)){const parts=path.split('/');out.push({link:u,path,size:n.size,alb:alb||parts[1].slice(0,9)})}})(f,'')}
fs.writeFileSync('wavs.json',JSON.stringify(out)); console.log(out.length, (out.reduce((a,x)=>a+x.size,0)/1e9).toFixed(1)+'GB')
