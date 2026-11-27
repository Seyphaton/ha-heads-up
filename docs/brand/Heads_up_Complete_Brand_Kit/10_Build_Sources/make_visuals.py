"""Render contact sheets from the actual packaged icon exports, not mockups."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import numpy as np
ROOT=Path('/mnt/data/Heads_up_Complete_Brand_Kit');W=Path('/mnt/data/heads_up_completion_work');QA=ROOT/'07_Quality_Assurance';QA.mkdir(exist_ok=True)
KINDS=['Main','Bright','Dark','Flat-Blue','Flat-White','Flat-Navy','Transparent-Light','Transparent-Dark','Monochrome-Black','Monochrome-White','Warning','Critical']
STEMS=dict(zip(KINDS,['main','bright','dark','flat_blue','flat_white','flat_navy','on_light','on_dark','monochrome_black','monochrome_white','warning','critical']))
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(n,b=False):return ImageFont.truetype(BOLD if b else REG,n)
BG='#081427';TEXT='#F5F8FF';MUTED='#B7C6DC'
def checker(n,unit=16,dark=False):
 y,x=np.indices((n,n));v=np.where((x//unit+y//unit)%2,35 if dark else 246,26 if dark else 226).astype('uint8');return Image.fromarray(np.repeat(v[:,:,None],3,axis=2))
def icon(k,n,circle=False):
 stem=STEMS[k];p=ROOT/'02_Icons'/k
 if circle:p=p/'Circle'/f'{stem}_circle_{n}.png'
 else:p=p/f'{stem}_{n}.png'
 return Image.open(p).convert('RGBA')
def on_background(im,k,n=None):
 n=n or im.width;bg=checker(n,dark=k in ['Transparent-Dark','Monochrome-White']);bg.paste(im,(0,0),im);return bg
# A: each icon is exactly 512 px on this proof.
board=Image.new('RGB',(2312,2010),BG);d=ImageDraw.Draw(board)
d.text((42,28),'Heads up | Complete variant family',font=font(38,True),fill=TEXT)
d.text((42,84),'Actual 512 px exports. Checkerboard is a proof surface only; it is not part of the icons.',font=font(22),fill=MUTED)
for i,k in enumerate(KINDS):
 x=44+(i%4)*568;y=150+(i//4)*610
 board.paste(on_background(icon(k,512),k),(x,y))
 d.text((x+256,y+532),k,font=font(25,True),fill=TEXT,anchor='mt')
 caption='Approved raster retained' if k in ['Main','Warning','Critical'] else 'Original palette + approved geometry'
 d.text((x+256,y+572),caption,font=font(17),fill=MUTED,anchor='mt')
board.save(QA/'variant-contact-sheet.png');board.resize((1156,1005),Image.Resampling.LANCZOS).save(QA/'variant-contact-sheet-preview.png')
# B: native resolution; two surface contexts, not enlarged substitutes.
board=Image.new('RGB',(1600,1980),BG);d=ImageDraw.Draw(board)
d.text((34,24),'Heads up | Native small-size review',font=font(34,True),fill=TEXT)
d.text((34,76),'16 / 32 / 48 / 64 px are displayed at their native pixel sizes. A 128 px reference follows.',font=font(20),fill=MUTED)
for col,n in enumerate([16,32,48,64,128]):d.text((370+col*205,124),f'{n} px',font=font(19,True),fill=TEXT,anchor='mt')
d.text((1450,124),'Circle 64 px',font=font(19,True),fill=TEXT,anchor='mt')
for i,k in enumerate(KINDS):
 y=162+i*144;d.text((34,y+32),k,font=font(21,True),fill=TEXT)
 for j,n in enumerate([16,32,48,64,128]):
  cx=370+j*205
  if n<=64:
   for dx,dark in [(-43,False),(43,True)]:
    im=icon(k,n);bg=checker(78,unit=13,dark=dark);bg.paste(im,((78-n)//2,(78-n)//2),im);board.paste(bg,(cx+dx-39,y+1))
  else:
   im=icon(k,n);board.paste(on_background(im,k),(cx-64,y-18))
 im=icon(k,64,True);bg=checker(78,unit=13);bg.paste(im,(7,7),im);board.paste(bg,(1411,y+1))
d.text((34,1910),'At 16-32 px, do not rely on the exclamation mark alone. Provide a severity text label.',font=font(22),fill=MUTED)
board.save(QA/'small-size-contact-sheet.png')
# C: exact 4x magnification of actual 512 px bell details.
selected=['Main','Bright','Dark','Warning','Critical','Transparent-Light','Transparent-Dark','Monochrome-White']
board=Image.new('RGB',(2960,1980),BG);d=ImageDraw.Draw(board)
d.text((36,24),'Heads up | Bell geometry - 400% pixel inspection',font=font(34,True),fill=TEXT)
d.text((36,76),'Crops from actual 512 px PNGs, enlarged exactly 4x with nearest-neighbor sampling.',font=font(22),fill=MUTED)
for i,k in enumerate(selected):
 x=36+(i%4)*730;y=160+(i//4)*900
 im=icon(k,512).crop((167,184,349,396));im=im.resize((728,848),Image.Resampling.NEAREST)
 bg=Image.new('RGB',im.size,'#14243C' if k in ['Transparent-Dark','Monochrome-White'] else '#F1F4F8');bg.paste(im,(0,0),im);board.paste(bg,(x,y))
 d.text((x+364,y-40),k,font=font(24,True),fill=TEXT,anchor='mt')
board.save(QA/'bell-geometry-contact-sheet.png')
# Loop proof: approved PNG versus reconstructed SVG.
board=Image.new('RGB',(1540,1150),BG);d=ImageDraw.Draw(board)
d.text((34,24),'Heads up | Loop and crown - source / SVG',font=font(34,True),fill=TEXT)
d.text((34,76),'1024 px renders, 4x pixel magnification. RGB differences do not imply a different outline.',font=font(20),fill=MUTED)
for j,k in enumerate(['Main','Warning','Critical']):
 for row,im in enumerate([icon(k,1024),Image.open(W/'vector_lab'/f'{k}-1024.png').convert('RGBA')]):
  x=34+j*500;y=170+row*475;crop=im.crop((455,372,575,472)).resize((480,400),Image.Resampling.NEAREST)
  bg=Image.new('RGB',crop.size,'#152136');bg.paste(crop,(0,0),crop);board.paste(bg,(x,y));d.text((x,y-34),k+(' - approved PNG' if row==0 else ' - SVG render'),font=font(21,True),fill=TEXT)
board.save(QA/'loop-400-percent.png')
# D: original ZIP, current approved master, overlay and absolute difference.
original=Image.open(W/'original/heads_up_brand_package/icons/main/main_512.png').convert('RGBA');approved=icon('Main',512)
board=Image.new('RGB',(2224,900),BG);d=ImageDraw.Draw(board)
d.text((34,24),'Heads up | Original source and approved final master',font=font(34,True),fill=TEXT)
d.text((34,76),'Later user approvals superseded the ZIP artwork. This is not presented as a bell-only pixel edit.',font=font(21),fill=MUTED)
ref=on_background(original,'Main');cur=on_background(approved,'Main');overlay=Image.blend(ref,cur,.5);diff=ImageChops.difference(ref,cur)
for i,(label,img) in enumerate([('Original ZIP Main',ref),('Approved final Main PNG',cur),('50% overlay',overlay),('Absolute difference',diff)]):
 x=34+i*550;board.paste(img,(x,170));d.text((x,130),label,font=font(22,True),fill=TEXT)
d.text((34,728),'Intentional approval changes: open loop, rounded clapper, symmetrical house without overhang, luminous tile.',font=font(22),fill=MUTED)
d.text((34,772),'Final PNGs preserve the approved later layout. Original source files are retained separately and are not current assets.',font=font(21),fill=MUTED)
board.save(QA/'original-vs-corrected.png')
# Approved raster vs vector at 512, with amplified difference.
board=Image.new('RGB',(1670,1900),BG);d=ImageDraw.Draw(board)
d.text((34,24),'Heads up | Approved PNG and vector reconstruction',font=font(32,True),fill=TEXT)
d.text((34,76),'Columns: approved PNG / rendered SVG / RGB difference x4. The original PNGs are retained unchanged.',font=font(20),fill=MUTED)
for i,k in enumerate(['Main','Warning','Critical']):
 y=170+i*565;d.text((34,y-36),k,font=font(24,True),fill=TEXT)
 a=on_background(icon(k,512),k);b=on_background(Image.open(W/'vector_lab'/f'{k}-512.png').convert('RGBA'),k)
 diff=Image.fromarray(np.minimum(np.abs(np.array(a).astype(int)-np.array(b).astype(int))*4,255).astype('uint8'))
 for j,im in enumerate([a,b,diff]):board.paste(im,(34+j*550,y))
board.save(QA/'approved-vs-vector.png')
# Circle and alpha proof for the approved trio on light and dark backgrounds.
board=Image.new('RGB',(1660,1300),BG);d=ImageDraw.Draw(board)
d.text((34,24),'Heads up | Tile-boundary circular and transparency proof',font=font(30,True),fill=TEXT)
d.text((34,76),'Circles are inscribed in the actual luminous tile. No outer canvas padding is used.',font=font(22),fill=MUTED)
for j,k in enumerate(['Main','Warning','Critical']):
 x=52+j*540;d.text((x+256,124),k,font=font(28,True),fill=TEXT,anchor='mt')
 for row,circular in enumerate([False,True]):
  y=180+row*540;im=icon(k,512,circular);bg=checker(512,dark=row==1);bg.paste(im,(0,0),im);board.paste(bg,(x,y))
board.save(QA/'circular-and-transparency-proof.png')
# Banner proof uses source and modified native at identical scale.
orig=Image.open(ROOT/'04_Banners/heads-up-banner-supplied-original-1774x887.png').convert('RGB');new=Image.open(ROOT/'04_Banners/heads-up-github-updated-native-1774x887.png').convert('RGB')
board=Image.new('RGB',(1280,1390),BG);d=ImageDraw.Draw(board)
d.text((28,20),'Heads up | Banner restoration',font=font(30,True),fill=TEXT)
d.text((28,66),'Only the icon region changes. Typography, underline, curves and text placement are preserved.',font=font(19),fill=MUTED)
for y,lab,im in [(145,'Supplied source',orig),(785,'Updated master icon',new)]:
 d.text((28,y-34),lab,font=font(22,True),fill=TEXT);board.paste(im.resize((1200,600),Image.Resampling.LANCZOS),(40,y))
board.save(QA/'banner-before-after.png')
print('Visual contact sheets complete.',flush=True)
