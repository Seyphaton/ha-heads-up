"""File, alpha, geometry, cross-format, source-preservation and renderer QA."""
from __future__ import annotations
from pathlib import Path
from io import BytesIO
import json,re,hashlib,copy,struct
from collections import Counter
import numpy as np
from PIL import Image
from lxml import etree as ET
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen
from shapely.geometry import LinearRing
from skimage.metrics import structural_similarity
import cairosvg
from playwright.sync_api import sync_playwright

ROOT=Path('/mnt/data/Heads_up_Complete_Brand_Kit');WORK=Path('/mnt/data/heads_up_completion_work');QA=ROOT/'07_Quality_Assurance'
META=json.loads((WORK/'build_metadata.json').read_text());KINDS=META['variants'];STEMS=META['stems'];SIZES=META['sizes'];NS='http://www.w3.org/2000/svg';S=lambda t:f'{{{NS}}}{t}'
records=[];errors=[];warnings=[];svg_records=[];metrics=[];browser=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add_error(message):errors.append(message);print('ERROR',message,flush=True)
def composite(a,bg=0):
 a=np.asarray(a).astype(float);return a[:,:,:3]*(a[:,:,3:4]/255)+bg*(1-a[:,:,3:4]/255)
def summary_diff(a,b):
 x=composite(a);y=composite(b);delta=x-y
 return {'rgb_rmse_on_black_0_to_255':round(float(np.sqrt(np.mean(delta**2))),5),'mean_absolute_channel_error':round(float(np.mean(abs(delta))),5),'ssim_rgb_on_black':round(float(structural_similarity(x,y,channel_axis=2,data_range=255)),6),'maximum_channel_error':round(float(abs(delta).max()),3),'pixel_identical_rgba':bool(np.array_equal(a,b))}
# Per-file raster validation includes all compatibility mirrors and original-sized copies.
alpha_cache={}
for shape in ['', 'Circle/']:
 for n in SIZES:
  p=ROOT/'02_Icons/Main'/shape/f'main{"_circle" if shape else ""}_{n}.png';alpha_cache[(bool(shape),n)]=np.array(Image.open(p))[:,:,3]
for p in sorted(ROOT.rglob('*')):
 if not p.is_file() or p.suffix.lower() not in ['.png','.webp']:continue
 if '07_Quality_Assurance' in p.parts:continue
 rel=str(p.relative_to(ROOT))
 try:
  with Image.open(p) as im:
   im.load();a=np.array(im.convert('RGBA'));rec={'file':rel,'format':im.format,'dimensions':list(im.size),'mode':im.mode,'sha256':sha(p)}
   if rel.startswith(('02_Icons/','01_Master/','03_Favicons/','09_Compatibility/heads_up_brand_package/icons/','09_Compatibility/heads_up_brand_package/favicons/')):
    if im.mode!='RGBA':add_error(rel+': not RGBA')
    zero=a[:,:,3]==0
    rec.update({'transparent_exterior':bool(zero.any()),'corners_alpha_zero':bool(np.all(a[[0,0,-1,-1],[0,-1,0,-1],3]==0)),'hidden_rgb_zero':bool(np.all(a[zero,:3]==0)),'icc_profile_present':bool(im.info.get('icc_profile'))})
    if not rec['transparent_exterior'] or not rec['corners_alpha_zero'] or not rec['hidden_rgb_zero']:add_error(rel+': transparency specification failed')
    if rel.startswith('02_Icons/'):
     m=re.search(r'_(\d+)\.(png|webp)$',p.name)
     if m:
      n=int(m.group(1));rec['expected_dimensions']=[n,n]
      if list(im.size)!=[n,n]:add_error(rel+': dimensions mismatch')
      allowed=alpha_cache[('Circle' in p.parts,n)]
      outside=int(np.sum((allowed==0)&(a[:,:,3]>0)));rec['alpha_pixels_outside_actual_tile_or_circle']=outside
      if outside:add_error(rel+': alpha outside approved boundary')
    if p.suffix=='.webp' and p.with_suffix('.png').exists():
     original=np.array(Image.open(p.with_suffix('.png')).convert('RGBA'));exact=bool(np.array_equal(a,original));rec['lossless_png_rgba_match']=exact
     if not exact:add_error(rel+': lossless WebP mismatch')
   records.append(rec)
 except Exception as exc:add_error(rel+': '+repr(exc))
print('Raster files validated:',len(records),flush=True)
# SVG structure, local references and exact shared geometry.
geometry=json.loads((ROOT/'10_Build_Sources/geometry.json').read_text());allowed={'svg','defs','title','desc','linearGradient','stop','clipPath','path','rect','g','mask','circle'}
for p in sorted((ROOT/'02_Icons').rglob('*.svg')):
 rel=str(p.relative_to(ROOT));tree=ET.parse(str(p));svg=tree.getroot();ids={e.get('id') for e in svg.iter() if e.get('id')};refs=[];bad=[]
 for e in svg.iter():
  local=ET.QName(e).localname
  if local not in allowed:bad.append(local)
  for attr,value in e.attrib.items():
   refs.extend(re.findall(r'url\(#([^\)]+)\)',value))
   if attr.endswith('href') and not value.startswith('#'):bad.append('external reference '+value)
  if e.tag==S('path'):
   pen=RecordingPen()
   try:
    parse_path(e.get('d'),pen)
    for op,pts in pen.value:
     for point in pts:
      if point is not None and not np.isfinite(point).all():raise ValueError('Nonfinite path')
   except Exception as exc:bad.append('invalid path: '+repr(exc))
 shared=True
 for k in ['house','bell','clapper']:
  paths=svg.xpath('//*[@id=$id]',id=k)
  if len(paths)!=1 or paths[0].get('d')!=geometry[k]:shared=False
 missing=sorted(set(refs)-ids)
 if bad or missing or not shared or svg.get('viewBox')!='0 0 1088 1088':add_error(rel+': SVG structural/geometry validation failed')
 svg_records.append({'file':rel,'xml_valid':True,'viewBox':svg.get('viewBox'),'embedded_images':len(svg.findall('.//'+S('image'))),'external_references_or_unsupported_elements':bad,'unresolved_local_references':missing,'identical_approved_trace_paths':shared,'bytes':p.stat().st_size,'sha256':sha(p)})
print('Canonical SVG files validated:',len(svg_records),flush=True)
# Sample each closed cubic outline for self-intersections, separately from valid holes.
curve_checks=[]
for name,d in geometry.items():
 pen=RecordingPen();parse_path(d,pen);sub=[];contours=[];last=None
 for op,points in pen.value:
  if op=='moveTo':
   if sub:contours.append(sub)
   last=np.array(points[0],float);sub=[last]
  elif op=='lineTo':last=np.array(points[0],float);sub.append(last)
  elif op=='curveTo':
   p0=last;p1,p2,p3=map(lambda v:np.array(v,float),points)
   for t in np.linspace(0,1,12)[1:]:sub.append((1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3)
   last=p3
  elif op=='closePath':
   if sub:sub.append(sub[0]);contours.append(sub);sub=[]
 if sub:contours.append(sub)
 for i,points in enumerate(contours):
  pts=[]
  for point in points:
   if not pts or np.linalg.norm(point-pts[-1])>1e-5:pts.append(point)
  simple=LinearRing(pts).is_simple
  curve_checks.append({'component':name,'contour':i,'sampled_points':len(pts),'sampled_outline_simple':simple})
  if not simple:add_error(name+': sampled curve self-intersection')
# Raster foreground clearance from the actual tight-tile circular boundary.
clearances=[]
y,x=np.indices((1088,1088));rad=np.hypot(x+.5-544,y+.5-544)
for kind in ['Main','Warning','Critical']:
 svg=ET.parse(str(ROOT/'02_Icons'/kind/f'{STEMS[kind]}.svg')).getroot()
 masks=[]
 for target in ['house-and-bell','severity-badge']:
  item=svg.xpath('//*[@id=$id]',id=target)
  if not item:continue
  root=ET.Element(S('svg'),nsmap={None:NS},viewBox='0 0 1088 1088',width='1088',height='1088')
  root.append(copy.deepcopy(svg.find(S('defs'))));root.append(copy.deepcopy(item[0]))
  rgba=np.array(Image.open(BytesIO(cairosvg.svg2png(bytestring=ET.tostring(root),output_width=1088,output_height=1088))).convert('RGBA'));m=rgba[:,:,3]>0
  clipped=int(np.sum(m&(rad>544)));margin=float(544-rad[m].max());masks.append(m)
  clearances.append({'variant':kind,'element':target,'pixels_outside_tight_tile_circle':clipped,'minimum_clearance_native_px':round(margin,4),'minimum_clearance_at_1024_px':round(margin*1024/1088,4)})
  if clipped:add_error(kind+'/'+target+': circular clipping')
 if len(masks)==2 and np.any(masks[0]&masks[1]):add_error(kind+': severity overlaps house/bell')
# Original-color preservation applies to nine restored styles, not to the approved replacement Main surface.
orig=WORK/'original/heads_up_brand_package';style_checks=[]
for kind in KINDS[:10]:
 if kind=='Main':continue
 rel=META['legacy'][kind];stem=STEMS[kind];source=ET.parse(str(orig/'icons'/rel/f'{stem}.svg')).getroot();out=ET.parse(str(ROOT/'02_Icons'/kind/f'{stem}.svg')).getroot()
 good=True
 for grad in source.find(S('defs')):
  found=out.xpath('//*[@id=$id]',id=grad.get('id'))
  good=good and len(found)==1 and dict(found[0].attrib)==dict(grad.attrib) and [dict(c.attrib) for c in found[0]]==[dict(c.attrib) for c in grad]
 sourcebg=source.find(S('rect'))
 if sourcebg is not None:good=good and out.xpath('//*[@id="background"]')[0].get('fill')==sourcebg.get('fill')
 style_checks.append({'variant':kind,'original_gradient_definitions_and_background_paint_preserved':good})
 if not good:add_error(kind+': original paint mismatch')
colors=json.loads((ROOT/'05_Color_Palette/colors.json').read_text());original_colors=json.loads((orig/'palettes/colors.json').read_text());palette_ok=colors['original_tokens']==original_colors
if not palette_ok:add_error('Original palette changed')
# ICO frames and manifest references.
ico=Image.open(ROOT/'03_Favicons/favicon.ico');frames=sorted(ico.ico.sizes());ico_ok=True
for wh in frames:
 a=np.array(ico.ico.getimage(wh).convert('RGBA'));b=np.array(Image.open(ROOT/f'02_Icons/Main/main_{wh[0]}.png').convert('RGBA'));ico_ok=ico_ok and np.array_equal(a,b)
manifest=json.loads((ROOT/'03_Favicons/site.webmanifest').read_text());manifest_ok=all((ROOT/'03_Favicons'/e['src']).is_file() for e in manifest['icons'])
if not ico_ok or not manifest_ok:add_error('Favicon package validation failed')
# Every variant is compared against a direct SVG render at all required QA sizes.
(QA/'Rendered_SVG').mkdir(exist_ok=True)
for kind in KINDS:
 stem=STEMS[kind];svgpath=ROOT/'02_Icons'/kind/f'{stem}.svg';data=svgpath.read_bytes()
 for n in [16,32,48,64,512]:
  if n==512:
   source=WORK/'vector_lab'/f'{kind}-512.png';im=Image.open(source).convert('RGBA')
  else:im=Image.open(BytesIO(cairosvg.svg2png(bytestring=data,output_width=n,output_height=n))).convert('RGBA')
  out=QA/'Rendered_SVG'/f'{stem}-svg-{n}.png';im.save(out)
  ref=Image.open(ROOT/'02_Icons'/kind/f'{stem}_{n}.png').convert('RGBA');m=summary_diff(np.array(ref),np.array(im));m.update({'variant':kind,'size_px':n,'comparison':'packaged PNG vs direct SVG rasterization','interpretation':'informational fidelity metric; PNG is not asserted pixel-identical to SVG'})
  metrics.append(m)
 if kind in ['Main','Warning','Critical']:
  im=Image.open(WORK/'vector_lab'/f'{kind}-1024.png').convert('RGBA');im.save(QA/'Rendered_SVG'/f'{stem}-svg-1024.png');ref=Image.open(ROOT/'02_Icons'/kind/f'{stem}_1024.png').convert('RGBA');m=summary_diff(np.array(ref),np.array(im));m.update({'variant':kind,'size_px':1024,'comparison':'approved PNG vs vector reconstruction'});metrics.append(m)
 print('Cross-format checked:',kind,flush=True)
# Independent rendering engine: inline the exact self-contained SVG source in Chromium.
(QA/'Browser_Renders').mkdir(exist_ok=True)
with sync_playwright() as pw:
 browser_process=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--force-color-profile=srgb'])
 page=browser_process.new_page(viewport={'width':512,'height':512},device_scale_factor=1)
 browser_version=browser_process.version
 for kind in KINDS:
  stem=STEMS[kind];text=(ROOT/'02_Icons'/kind/f'{stem}.svg').read_text().split('?>',1)[-1]
  page.set_content('<html><head><style>html,body{margin:0;padding:0;background:transparent}svg{display:block;width:512px;height:512px}</style></head><body>'+text+'</body></html>')
  page.evaluate('() => new Promise(requestAnimationFrame)')
  dest=QA/'Browser_Renders'/f'{stem}-chromium-512.png';page.screenshot(path=str(dest),omit_background=True)
  a=np.array(Image.open(dest).convert('RGBA'));b=np.array(Image.open(QA/'Rendered_SVG'/f'{stem}-svg-512.png').convert('RGBA'));m=summary_diff(a,b);m.update({'variant':kind,'size_px':512,'comparison':'Chromium vs CairoSVG'});browser.append(m)
  if m['rgb_rmse_on_black_0_to_255']>5:add_error(kind+': substantial cross-renderer discrepancy')
  # Also exercise the circular SVG itself, not just PNG masks.
  text=(ROOT/'02_Icons'/kind/'Circle'/f'{stem}_circle.svg').read_text().split('?>',1)[-1]
  page.set_content('<html><head><style>html,body{margin:0;padding:0;background:transparent}svg{display:block;width:512px;height:512px}</style></head><body>'+text+'</body></html>');page.evaluate('() => new Promise(requestAnimationFrame)')
  page.screenshot(path=str(QA/'Browser_Renders'/f'{stem}-circle-chromium-512.png'),omit_background=True)
 browser_process.close()
print('Browser checks complete',flush=True)
# Per-file approved PNG source checks and original-path completeness.
copy_report=json.loads((QA/'approved-png-preservation.json').read_text());copies_ok=all(sha(ROOT/f['destination'])==f['sha256'] and f['byte_identical'] for f in copy_report['files'])
legacyroot=ROOT/'09_Compatibility/heads_up_brand_package';missing_legacy=[str(p.relative_to(orig)) for p in orig.rglob('*') if p.is_file() and not (legacyroot/p.relative_to(orig)).exists()]
if missing_legacy:add_error('Missing original compatibility paths: '+str(missing_legacy))
banner=json.loads((QA/'banner-validation.json').read_text())
if banner['changes_outside_declared_icon_region']!=0:add_error('Banner has changes outside icon region')
warnings=[
 'Main, Warning and Critical SVGs are gradient reconstructions from the approved raster; original source vectors for that luminous artwork do not exist in the uploaded ZIP. They are not pixel-identical to the approved PNGs.',
 'The approved Main/Warning/Critical 2048 px PNGs are upscaled from 1088 px raster masters, not newly recovered vector detail.',
 'At 16-32 px, severity punctuation is not a reliable sole indicator. Use visible severity text and an accessible name.',
 'Original Bright and Transparent Light colors are preserved; contrast depends on host background. Prefer Flat Navy or monochrome variants for demanding small-size contrast.',
 'Manifest icon purpose is any, not maskable. The tested circle is the actual tile-inscribed circle, not every OS adaptive-icon safe zone.',
 'No live Home Assistant, iOS, Android or Firefox/Safari integration certification was performed.',
 'Complex luminous SVGs are larger than flat SVGs. Use PNG/WebP for routine small UI delivery or serve SVG with transport compression.'
]
result={'status':'PASS' if not errors else 'FAIL','scope':'Automated asset integrity and rendering checks; not independent human review or live-platform certification.','errors':errors,'limitations':warnings,'canonical_icon_variants':KINDS,'delivery_sizes':SIZES,'raster_files_validated':len(records),'canonical_svg_files_validated':len(svg_records),'lossless_webp_pairs_checked':sum('lossless_png_rgba_match' in r for r in records),'approved_png_files_preserved_byte_exact':len(copy_report['files']) if copies_ok else False,'original_named_colors_unchanged':palette_ok,'original_paths_missing':missing_legacy,'original_variant_styles':style_checks,'ico_frames':frames,'ico_matches_size_specific_approved_pngs':bool(ico_ok),'webmanifest_local_references_valid':manifest_ok,'webmanifest_maskable_claimed':any('maskable' in e['purpose'] for e in manifest['icons']),'circle_clearance':clearances,'curve_integrity':curve_checks,'svg_files':svg_records,'cross_format_metrics':metrics,'browser_renderer':{'name':'Chromium','version':browser_version,'method':'Exact asset SVG markup rendered inline at 512 px, plus circular SVGs.'},'cross_renderer_metrics':browser,'banner':banner,'files':records}
(QA/'technical-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'errors':errors,'rasters':len(records),'svg':len(svg_records),'pairs':result['lossless_webp_pairs_checked']}),flush=True)
