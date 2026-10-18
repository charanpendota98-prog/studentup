import sys,json
from PIL import Image
name=sys.argv[1]; j=json.load(open(f'/tmp/shots/{name}.parts.json'))
dpr=j['dpr']; vh=j['vh']; sh=j['sh']; parts=j['parts']
W=Image.open(parts[0]).width; out=Image.new('RGB',(W,int(sh*dpr)),'white')
for i,f in enumerate(parts):
    im=Image.open(f); y=i*vh
    if y+vh>sh: # last part: browser clamps scroll; crop top
        off=int((y+vh-sh)*dpr); im=im.crop((0,off,W,im.height)); y=sh-vh+ (y+vh-sh)
        out.paste(im,(0,int((sh-im.height/dpr)*dpr)))
    else: out.paste(im,(0,int(y*dpr)))
out.save(f'/tmp/shots/{name}')
seg=int(sys.argv[2]) if len(sys.argv)>2 else 2600; i=0; y=0; h=out.height
base=name.replace('.png','')
while y<h:
    c=out.crop((0,y,W,min(y+seg,h))); c=c.resize((c.width//2,c.height//2)) if dpr==2 else c; c.save(f'/tmp/shots/{base}_{i}.png'); y+=seg; i+=1
print(out.size,i)
