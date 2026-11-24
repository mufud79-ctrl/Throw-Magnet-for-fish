# Side-by-side reference vs headless frames: python3 compare.py "<ref_pattern_with_%s>" out/<Name> ref_t1,ref_t2 my_t1,my_t2 out.png
import sys
from PIL import Image, ImageDraw
ref_pat, mine_dir, ref_times, mine_times, out = sys.argv[1], sys.argv[2], sys.argv[3].split(','), sys.argv[4].split(','), sys.argv[5]
pairs=[]
for rt, mt in zip(ref_times, mine_times):
    a=Image.open(ref_pat % rt).convert('RGB'); a=a.resize((300, int(300*a.height/a.width)))
    b=Image.open(f'{mine_dir}/f_{float(mt):.2f}.png').convert('RGB'); b=b.resize((300, int(300*b.height/b.width)))
    h=max(a.height,b.height); P=Image.new('RGB',(604,h),(0,0,0)); P.paste(a,(0,0)); P.paste(b,(304,0))
    d=ImageDraw.Draw(P); d.rectangle((0,0,64,14),fill=(0,0,0)); d.text((2,1),'REF '+rt,fill=(255,200,0)); d.rectangle((304,0,370,14),fill=(0,0,0)); d.text((306,1),'MINE '+mt,fill=(120,220,255))
    pairs.append(P)
cols=2; w=604; h=max(p.height for p in pairs); rows=(len(pairs)+cols-1)//cols
W=Image.new('RGB',(w*cols+8,h*rows+4*rows),(40,40,40))
for i,p in enumerate(pairs): W.paste(p,((i%cols)*(w+8),(i//cols)*(h+4)))
W.save(out)
