# Brand name is always "Wreck The Room™" (verb uses like "wreck the room you've outgrown" stay lowercase).
import sys,re,glob,os
root=sys.argv[1];n=0
files=glob.glob(root+'/src/*.html')+glob.glob(root+'/src/*.js')+glob.glob(root+'/build*.py')
for f in files:
    s=open(f,encoding='utf8').read();o=s
    s=s.replace('Wreck the Room','Wreck The Room')
    s=re.sub(r'Wreck The Room(?!™|<sup>|&trade;|\\u2122)','Wreck The Room™',s)
    if s!=o:
        n+=1;open(f,'w',encoding='utf8').write(s);print(os.path.basename(f),s.count('Wreck The Room'))
print('files',n)
