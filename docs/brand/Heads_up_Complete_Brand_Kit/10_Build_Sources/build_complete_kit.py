"""Assemble Heads up assets. Approved PNGs are byte-copied, never redrawn."""
from __future__ import annotations
import copy, json, hashlib, shutil, re, colorsys, importlib.util
from pathlib import Path
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import numpy as np, cv2
from PIL import Image, ImageCms
from lxml import etree as ET
import cairosvg
BASE=Path('/mnt/data/heads_up_completion_work');ROOT=Path('/mnt/data/Heads_up_Complete_Brand_Kit')
APP=BASE/'approved_png/Heads_up_Transparent_PNGs';LAY=BASE/'approved_layout/Heads_up_Tile_Boundary_Review'
ORIG=BASE/'original/heads_up_brand_package';VEC=BASE/'vector_lab'
SIZES=[16,20,24,32,40,48,57,60,64,72,76,80,87,96,114,120,128,144,152,167,180,192,256,384,512,1024,2048]
KINDS=['Main','Bright','Dark','Flat-Blue','Flat-White','Flat-Navy','Transparent-Light','Transparent-Dark','Monochrome-Black','Monochrome-White','Warning','Critical']
APPROVED=['Main','Warning','Critical']
STEMS=dict(zip(KINDS,['main','bright','dark','flat_blue','flat_white','flat_navy','on_light','on_dark','monochrome_black','monochrome_white','warning','critical']))
LEGACY={k:('transparent/'+STEMS[k] if k in KINDS[6:10] else STEMS[k]) for k in KINDS[:10]}
NS='http://www.w3.org/2000/svg';S=lambda t:f'{{{NS}}}{t}';SRGB=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
for f in ['01_Master','02_Icons','03_Favicons','04_Banners','05_Color_Palette','06_Documentation','07_Quality_Assurance','08_Source_Reference','09_Compatibility/heads_up_brand_package','10_Build_Sources']:(ROOT/f).mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save_png(im,path):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);a=np.array(im.convert('RGBA'));a[a[:,:,3]==0,:3]=0
 Image.fromarray(a).save(path,optimize=True,icc_profile=SRGB)
def render(svg,size):return Image.open(BytesIO(cairosvg.svg2png(bytestring=svg,output_width=size,output_height=size))).convert('RGBA')
spec=importlib.util.spec_from_file_location('transparency',APP/'04_Technical/build_transparent_pngs.py');trans=importlib.util.module_from_spec(spec);spec.loader.exec_module(trans)
xy=np.array(json.loads((APP/'04_Technical/tile-alpha-boundary.json').read_text())['contour_points_xy'])
masks={(shape,n):trans.alpha_mask(xy,n,shape=='Circle') for n in SIZES for shape in ['Rounded-Square','Circle']}
copy_records=[];webp_jobs=[]
for kind in KINDS:
 stem=STEMS[kind];folder=ROOT/'02_Icons'/kind;folder.mkdir(exist_ok=True);(folder/'Circle').mkdir(exist_ok=True)
 data=(VEC/f'{kind}.svg').read_bytes();(folder/f'{stem}.svg').write_bytes(data)
 svg=ET.fromstring(data);defs=svg.find(S('defs'));clip=ET.SubElement(defs,S('clipPath'),id='circular-display');ET.SubElement(clip,S('circle'),cx='544',cy='544',r='544')
 group=ET.Element(S('g'),{'clip-path':'url(#circular-display)'})
 for ch in list(svg):
  if ch.tag not in [S('defs'),S('title'),S('desc')]:svg.remove(ch);group.append(ch)
 svg.append(group);(folder/'Circle'/f'{stem}_circle.svg').write_bytes(ET.tostring(svg,xml_declaration=True,encoding='UTF-8'))
 high=None if kind in APPROVED else render(data,2048)
 for shape in ['Rounded-Square','Circle']:
  target_dir=folder if shape=='Rounded-Square' else folder/'Circle';suffix='' if shape=='Rounded-Square' else '_circle'
  for n in SIZES:
   dest=target_dir/f'{stem}{suffix}_{n}.png'
   if kind in APPROVED:
    source=APP/'01_Icons'/shape/kind/f'heads-up-{stem}{"-circle" if shape=="Circle" else ""}-{n}.png';shutil.copyfile(source,dest)
    copy_records.append({'source':str(source.relative_to(APP)),'destination':str(dest.relative_to(ROOT)),'sha256':sha(dest),'byte_identical':sha(source)==sha(dest)})
   else:
    resized=high.convert('RGBa').resize((n,n),Image.Resampling.LANCZOS).convert('RGBA');pix=np.array(resized)
    if kind not in KINDS[6:10]:
     from scipy.ndimage import distance_transform_edt
     alpha=np.array(masks[(shape,n)]);missing=(alpha>0)&(pix[:,:,3]==0)
     if missing.any():
      nearest=distance_transform_edt(pix[:,:,3]==0,return_distances=False,return_indices=True);pix[missing,:3]=pix[nearest[0][missing],nearest[1][missing],:3]
     pix[:,:,3]=alpha
    elif shape=='Circle':pix[:,:,3]=np.minimum(pix[:,:,3],np.array(masks[(shape,n)]))
    pix[pix[:,:,3]==0,:3]=0;save_png(Image.fromarray(pix),dest)
   webp_jobs.append((dest,dest.with_suffix('.webp')))
 if kind in APPROVED:
  native=folder/'Native';native.mkdir(exist_ok=True)
  for suffix in ['', '-circle']:
   src=APP/'02_Native_Assets'/f'heads-up-{stem}{suffix}-1088.png';shutil.copyfile(src,native/src.name)
 print('PNG and SVG assembled:',kind,flush=True)
def webp_task(job):
 src,dest=job
 with Image.open(src) as im:im.save(dest,format='WEBP',lossless=True,exact=True,method=4,icc_profile=im.info.get('icc_profile',SRGB))
 return dest
with ThreadPoolExecutor(max_workers=4) as pool:
 for i,_ in enumerate(pool.map(webp_task,webp_jobs)):
  if (i+1)%108==0:print('Lossless WebP completed:',i+1,'/',len(webp_jobs),flush=True)
for src,dest in [('02_Icons/Main/main.svg','01_Master/heads-up-master.svg'),('02_Icons/Main/main_1024.png','01_Master/heads-up-master.png'),('02_Icons/Main/main_2048.png','01_Master/heads-up-master-2048.png'),('02_Icons/Main/Native/heads-up-main-1088.png','01_Master/heads-up-master-native-1088.png')]:shutil.copyfile(ROOT/src,ROOT/dest)
fav=ROOT/'03_Favicons'
for n in [16,32,48,64]:
 for fname in [f'favicon-{n}.png',f'favicon-{n}x{n}.png']:shutil.copyfile(ROOT/f'02_Icons/Main/main_{n}.png',fav/fname)
shutil.copyfile(ROOT/'02_Icons/Main/main.svg',fav/'favicon.svg')
for fname,n in [('apple-touch-icon.png',180),('android-chrome-192x192.png',192),('android-chrome-512x512.png',512)]:shutil.copyfile(ROOT/f'02_Icons/Main/main_{n}.png',fav/fname)
import struct
ico_frames=[(n,(ROOT/f'02_Icons/Main/main_{n}.png').read_bytes()) for n in [16,32,48,64,128,256]]
header=struct.pack('<HHH',0,1,len(ico_frames));offset=6+16*len(ico_frames);entries=[];payload=[]
for n,data in ico_frames:
 entries.append(struct.pack('<BBBBHHII',n if n<256 else 0,n if n<256 else 0,0,0,1,32,len(data),offset));payload.append(data);offset+=len(data)
(fav/'favicon.ico').write_bytes(header+b''.join(entries)+b''.join(payload))
manifest={'name':'Heads up','short_name':'Heads up','description':'Smart notifications for Home Assistant','start_url':'./','scope':'./','display':'standalone','background_color':'#031124','theme_color':'#031124','icons':[{'src':f'android-chrome-{n}x{n}.png','sizes':f'{n}x{n}','type':'image/png','purpose':'any'} for n in [192,512]]}
(fav/'site.webmanifest').write_text(json.dumps(manifest,indent=2)+'\n')
print('FAVICONS COMPLETE',flush=True)
# Banner: keep the complete supplied source and constrain modifications to the icon.
ban=ROOT/'04_Banners';banner_path=Path('/mnt/data/image.png');shutil.copyfile(banner_path,ban/'heads-up-banner-supplied-original-1774x887.png')
banner=Image.open(banner_path).convert('RGBA');old=np.array(banner)[:,:,:3].copy();x0,y0,n=209,236,360
new=Image.open(ROOT/'02_Icons/Main/Native/heads-up-main-1088.png').convert('RGBA').convert('RGBa').resize((n,n),Image.Resampling.LANCZOS).convert('RGBA');newa=np.array(new)[:,:,3]
region=np.zeros(old.shape[:2],np.uint8);roi=old[230:602,203:575];bright=((roi[:,:,1]>125)&(roi[:,:,2]>150)).astype(np.uint8)
ncomp,ll,st,_=cv2.connectedComponentsWithStats(bright);idx=max(range(1,ncomp),key=lambda i:st[i,4]);cc=(ll==idx).astype(np.uint8)
contours,_=cv2.findContours(cc,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);filled=np.zeros_like(cc);cv2.drawContours(filled,contours,-1,1,-1);filled=cv2.dilate(filled,np.ones((3,3),np.uint8));region[230:602,203:575]=filled
cover=np.zeros_like(region);cover[y0:y0+n,x0:x0+n]=(newa>=250).astype(np.uint8);remove=(region>0)&(cover==0)
clean=cv2.inpaint(old,remove.astype(np.uint8),5,cv2.INPAINT_TELEA);updated=Image.fromarray(clean).convert('RGBA');updated.alpha_composite(new,(x0,y0))
updated.save(ban/'heads-up-github-updated-native-1774x887.png',icc_profile=SRGB);updated.resize((1280,640),Image.Resampling.LANCZOS).save(ban/'heads-up-github-1280x640.png',icc_profile=SRGB)
banner.resize((1280,640),Image.Resampling.LANCZOS).save(ban/'heads-up-github-original-1280x640.png',icc_profile=SRGB)
for file in [ban/'heads-up-github-1280x640.png',ban/'heads-up-github-updated-native-1774x887.png']:Image.open(file).save(file.with_suffix('.webp'),lossless=True,exact=True,method=4,icc_profile=SRGB)
changes=np.any(np.array(updated)[:,:,:3]!=old,axis=-1);yy,xx=np.where(changes);box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
report={'source_file':'heads-up-banner-supplied-original-1774x887.png','source_sha256':sha(banner_path),'source_dimensions':[1774,887],'changed_pixels_native':int(changes.sum()),'change_bounds_xyxy_native':box,'declared_icon_region_xyxy':[203,230,575,602],'changes_outside_declared_icon_region':int(changes[:230].sum()+changes[602:].sum()+changes[230:602,:203].sum()+changes[230:602,575:].sum()),'title_subtitle_underline_curves_unchanged_outside_icon_region':True,'delivery_dimensions':[1280,640],'resize':'Lanczos, original 2:1 canvas; no layout changes','source_supplied_separately_from_original_zip':True}
# Preserve original tokens and original gradient definitions; add named severity tokens.
pal=ROOT/'05_Color_Palette';(pal/'Original').mkdir(exist_ok=True)
for src in (ORIG/'palettes').iterdir():shutil.copyfile(src,pal/'Original'/src.name)
original=json.loads((ORIG/'palettes/colors.json').read_text())
usage={'primary_blue':'Original Flat Blue background.','electric_blue':'Original supporting electric-blue brand token.','cyan':'Original cyan accent and Transparent Light gradient endpoint.','deep_navy':'Original Flat Navy background.','midnight':'Original Dark gradient stop and manifest surface.','ice':'Original light-blue supporting tone.','white':'Original white foreground and flat surface.','surface':'Original supporting light surface.','subtle':'Original subtle light surface.','success':'Original semantic success token.','warning':'Original semantic warning token; unchanged.','alert':'Original semantic alert token; unchanged.','info':'Original semantic information token.'}
added={'warning_orange':'#FFAC12','dark_amber':'#482000','light_amber':'#FFE39A','warning_accent':'#F59E0B','critical_red':'#FF3042','dark_red':'#B9001C','light_red':'#FFF9F8','critical_accent':'#EF4444'}
new_usage={'warning_orange':'Approved Warning badge gradient endpoint.','dark_amber':'Approved Warning exclamation mark and dot.','light_amber':'Approved Warning badge gradient start.','warning_accent':'Existing warning semantic token reused for the extended palette.','critical_red':'Approved Critical badge gradient start.','dark_red':'Approved Critical badge gradient endpoint.','light_red':'Approved Critical badge border, exclamation mark and dot.','critical_accent':'Existing alert semantic token reused for the extended palette.'}
def record(name,value,origin,usage):
 rgb=tuple(int(value[i:i+2],16) for i in [1,3,5]);h,l,s=colorsys.rgb_to_hls(*(v/255 for v in rgb))
 return {'name':name,'hex':value.upper(),'rgb':list(rgb),'hsl':{'h':round(h*360,2),'s':round(s*100,2),'l':round(l*100,2)},'intended_usage':usage,'origin':origin}
colors=[record(k,v,'original colors.json',usage[k]) for k,v in original.items()];source_colors={};source_gradients={}
for p in sorted((ORIG/'icons').rglob('*.svg')):
 tree=ET.parse(str(p));source_gradients[str(p.relative_to(ORIG))]=[{'id':g.get('id'),'attributes':dict(g.attrib),'stops':[dict(e.attrib) for e in g]} for g in tree.findall('.//'+S('linearGradient'))]
 for value in re.findall(r'#[0-9A-Fa-f]{6}',p.read_text()):source_colors.setdefault(value.upper(),[]).append(str(p.relative_to(ORIG)))
for value,files in source_colors.items():
 if value not in [v.upper() for v in original.values()]:colors.append(record('source_svg_'+value[1:].lower(),value,'original SVG literal','Original SVG paint; used in '+', '.join(sorted(set(files)))+'.'))
for k,v in added.items():colors.append(record(k,v,'approved severity badge or retained semantic token',new_usage[k]))
(pal/'colors.json').write_text(json.dumps({'product_name':'Heads up','original_tokens':original,'added_severity_tokens':added,'definitions':colors,'original_svg_gradients':source_gradients,'note':'Original tokens and source SVG stop definitions are preserved. Approved luminous raster surfaces contain continuous color fields. Reconstructed vector gradient stops are in the SVGs and build sources.'},indent=2)+'\n')
css=['/* Heads up. Original values preserved. Usage definitions: colors.json. */',':root {']
for c in colors:css.append(f"  --heads-up-{c['name'].replace('_','-')}: {c['hex']}; /* RGB {','.join(map(str,c['rgb']))}; HSL {c['hsl']['h']} {c['hsl']['s']}% {c['hsl']['l']}% */")
css.append('}');(pal/'colors.css').write_text('\n'.join(css)+'\n')
rows=(len(colors)+3)//4;svg=ET.Element(S('svg'),nsmap={None:NS},viewBox=f'0 0 1200 {130+rows*120}',width='1200',height=str(130+rows*120));ET.SubElement(svg,S('rect'),x='0',y='0',width='1200',height=str(130+rows*120),fill='#F5F7FA')
t=ET.SubElement(svg,S('text'),x='32',y='50',fill='#0A1D3C',attrib={'font-family':'sans-serif','font-size':'30','font-weight':'700'});t.text='Heads up | Color palette'
t=ET.SubElement(svg,S('text'),x='32',y='85',fill='#42556E',attrib={'font-family':'sans-serif','font-size':'16'});t.text='Original values retained. Severity palette added. Full RGB, HSL and usage definitions: colors.json'
for i,c in enumerate(colors):
 x=32+(i%4)*292;y=116+(i//4)*120;ET.SubElement(svg,S('rect'),x=str(x),y=str(y),width='260',height='55',rx='6',fill=c['hex'],stroke='#B7C6DC',attrib={'stroke-width':'0.5'})
 for dy,text,size in [(79,c['name'],14),(101,c['hex'],15)]:
  e=ET.SubElement(svg,S('text'),x=str(x),y=str(y+dy),fill='#0A1D3C',attrib={'font-family':'sans-serif','font-size':str(size)});e.text=text
(pal/'palette.svg').write_bytes(ET.tostring(svg,xml_declaration=True,encoding='UTF-8'));cairosvg.svg2png(url=str(pal/'palette.svg'),write_to=str(pal/'palette.png'))
# Retain source evidence and original-path compatibility mirror.
shutil.copyfile('/mnt/data/Heads_Up_Full_Brand_Package(2).zip',ROOT/'08_Source_Reference/ORIGINAL_Brand_Package_UNMODIFIED.zip')
shutil.copyfile(APP/'04_Technical/tile-alpha-boundary.json',ROOT/'10_Build_Sources/tile-alpha-boundary.json')
for p in ['geometry.json','foreground-gradients.json','background-gradients.json','build_vectors.py']:shutil.copyfile(VEC/p,ROOT/'10_Build_Sources'/p)
shutil.copyfile(APP/'04_Technical/build_transparent_pngs.py',ROOT/'10_Build_Sources/build_transparent_pngs.py');shutil.copyfile(__file__,ROOT/'10_Build_Sources/build_complete_kit.py')
for kind in ['warning','critical']:shutil.copyfile(LAY/'04_Technical'/f'{kind}-badge.svg',ROOT/'10_Build_Sources'/f'{kind}-badge.svg')
legacyroot=ROOT/'09_Compatibility/heads_up_brand_package';mapping=[]
for kind,rel in LEGACY.items():
 origdir=ORIG/'icons'/rel;dest=legacyroot/'icons'/rel;dest.mkdir(parents=True,exist_ok=True)
 for p in origdir.iterdir():
  canonical=ROOT/'02_Icons'/kind/p.name
  if canonical.exists():shutil.copyfile(canonical,dest/p.name);mapping.append({'original':str(p.relative_to(ORIG)),'canonical':str(canonical.relative_to(ROOT)),'compatibility':str((dest/p.name).relative_to(ROOT))})
for p in (ORIG/'favicons').iterdir():
 dest=legacyroot/'favicons'/p.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(fav/p.name,dest);mapping.append({'original':str(p.relative_to(ORIG)),'canonical':str((fav/p.name).relative_to(ROOT)),'compatibility':str(dest.relative_to(ROOT))})
(legacyroot/'palettes').mkdir(exist_ok=True)
for p in (ORIG/'palettes').iterdir():shutil.copyfile(p,legacyroot/'palettes'/p.name)
(legacyroot/'README.md').write_text('# Heads up - Compatibility layout\n\nOriginal icon and favicon paths retained with current geometry. Original palette files unchanged. See ../../06_Documentation/README.md for scope and release status.\n')
(ROOT/'06_Documentation/LEGACY_PATH_MAP.json').write_text(json.dumps(mapping,indent=2)+'\n')
(ROOT/'07_Quality_Assurance/approved-png-preservation.json').write_text(json.dumps({'files':copy_records,'all_byte_identical':all(x['byte_identical'] for x in copy_records)},indent=2)+'\n')
(ROOT/'07_Quality_Assurance/banner-validation.json').write_text(json.dumps(report,indent=2)+'\n')
(BASE/'build_metadata.json').write_text(json.dumps({'sizes':SIZES,'variants':KINDS,'stems':STEMS,'legacy':LEGACY,'approved_png_copies':len(copy_records),'webp_files':len(webp_jobs),'palette_definitions':len(colors),'banner':report},indent=2)+'\n')
print('ASSEMBLY COMPLETE',flush=True)
