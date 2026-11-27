"""Export approved Heads up raster layouts with a tightly traced alpha boundary.

Usage:
    python build_transparent_pngs.py --source-zip Heads_up_Tile_Boundary_Review.zip \
        --original-zip 'Heads_Up_Full_Brand_Package(2).zip' --output Heads_up_Transparent_PNGs

Requires Python 3, Pillow, NumPy, SciPy. No artwork is generatively redrawn.
"""
from __future__ import annotations
import argparse
from io import BytesIO
from pathlib import Path
import hashlib
import json
import re
import shutil
import zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageCms
from scipy.ndimage import map_coordinates, gaussian_filter1d, distance_transform_edt, binary_dilation, label
from scipy.signal import savgol_filter

BOX = (82, 75, 1170, 1163)
D = 1088
KINDS = ('Main', 'Warning', 'Critical')
ROOTNAME = 'Heads_up_Tile_Boundary_Review'
CORE = (300-82-6, 220-75-6, 950-82+6, 912-75+6)
BADGE = (660-82, 845-75, 660-82+220, 845-75+220)
REQUIRED_SIZES = [16,20,24,32,40,48,64,72,96,120,128,144,152,167,180,192,256,384,512,1024,2048]
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def font(n: int, bold: bool = False):
    return ImageFont.truetype(BOLD if bold else REG, n)

def trace_boundary(full: np.ndarray):
    count = 4096
    angles = np.arange(count)/count*2*np.pi
    ux, uy = np.cos(angles), np.sin(angles)
    square_r = (D/2)/np.maximum(np.abs(ux),np.abs(uy))
    radius = square_r[:,None]*np.linspace(.72,1.06,600)[None,:]
    cx, cy = (BOX[0]+BOX[2])/2, (BOX[1]+BOX[3])/2
    xs = cx+ux[:,None]*radius-.5
    ys = cy+uy[:,None]*radius-.5
    # The cyan rim has a well-defined outward drop in its green channel.
    g = map_coordinates(full[:,:,1].astype(float),[ys,xs],order=1,mode='nearest')
    g = gaussian_filter1d(g,1.2,axis=1)
    outward_gradient = np.gradient(g,axis=1)/(radius[:,1:2]-radius[:,:1])
    edge_idx = outward_gradient.argmin(axis=1)
    raw = radius[np.arange(count),edge_idx]
    radii = savgol_filter(raw,61,3,mode='wrap')
    xy = np.c_[D/2+ux*radii, D/2+uy*radii]
    return xy, radii

def alpha_mask(xy: np.ndarray, size: int, circular: bool) -> Image.Image:
    # BOX resampling is area coverage, not a ringing filter. No halo is added.
    ss = 16 if size <= 96 else 8 if size <= 512 else 4
    k = size*ss
    m = Image.new('L',(k,k),0)
    scale = k/D
    ImageDraw.Draw(m).polygon([(float(x*scale),float(y*scale)) for x,y in xy],fill=255)
    if circular:
        circle = Image.new('L',(k,k),0)
        ImageDraw.Draw(circle).ellipse((0,0,k-1,k-1),fill=255)
        from PIL import ImageChops
        m = ImageChops.darker(m,circle)
    return m.resize((size,size),Image.Resampling.BOX)

def native_rgba(rgb: np.ndarray, mask: Image.Image):
    a = np.asarray(mask)
    rgba = np.dstack([rgb.copy(),a])
    partial = (a>0)&(a<255)
    # Remove old matte contamination only on partial-coverage edge pixels.
    indices = distance_transform_edt(a<255,return_distances=False,return_indices=True)
    rgba[partial,:3] = rgb[indices[0][partial],indices[1][partial]]
    rgba[a==0,:3] = 0
    return Image.fromarray(rgba), int(partial.sum())

def export_rgba(native: Image.Image, size: int, mask: Image.Image):
    if size == D:
        out = native.copy()
    else:
        # Premultiplied-alpha resizing avoids blending the removed canvas into edges.
        out = native.convert('RGBa').resize((size,size),Image.Resampling.LANCZOS).convert('RGBA')
    p = np.asarray(out).copy()
    a = np.asarray(mask)
    missing = (a>0)&(p[:,:,3]==0)
    if missing.any():
        good = p[:,:,3]>0
        inds = distance_transform_edt(~good,return_distances=False,return_indices=True)
        p[missing,:3] = p[inds[0][missing],inds[1][missing],:3]
    p[:,:,3] = a
    p[a==0,:3] = 0
    return Image.fromarray(p),int(missing.sum())

def make_checker(w: int,h: int,unit: int=16):
    yy,xx=np.indices((h,w))
    v=np.where(((xx//unit+yy//unit)%2)==0,225,246).astype(np.uint8)
    return Image.fromarray(np.repeat(v[:,:,None],3,axis=2))

def check_png(path: Path, expected_mask: Image.Image, native_rgb=None, kind=None):
    with Image.open(path) as im:
        im.load()
        assert im.format=='PNG' and im.mode=='RGBA'
        p=np.asarray(im)
        a=p[:,:,3]
        assert np.array_equal(a,np.asarray(expected_mask))
        assert all(int(v)==0 for v in [a[0,0],a[0,-1],a[-1,0],a[-1,-1]])
        assert np.all(p[a==0,:3]==0)
        assert np.any(a==0) and np.any(a==255)
        support=a>0
        connected=label(support)[1]
        assert connected==1
        opaque=a==255
        aa=a>0
        # Antialiasing is at most a one-pixel band around the >=50% silhouette.
        external=int(np.sum(aa & ~binary_dilation(a>=128,iterations=1)))
        assert external==0
        result={'path':str(path),'dimensions_px':list(im.size),'mode':im.mode,
                'fully_transparent_pixels':int((a==0).sum()),
                'opaque_pixels':int(opaque.sum()),'antialiased_pixels':int(((a>0)&(a<255)).sum()),
                'corners_fully_transparent':True,'hidden_rgb_cleared':True,
                'nontransparent_components':connected,'alpha_outside_one_pixel_edge_band':external,
                'sha256':sha(path)}
        if native_rgb is not None:
            x0,y0,x1,y1=CORE
            assert np.all(a[y0:y1,x0:x1]==255)
            assert np.array_equal(p[y0:y1,x0:x1,:3],native_rgb[y0:y1,x0:x1])
            result['guarded_house_and_bell_region_unchanged']=True
            if kind != 'Main':
                x0,y0,x1,y1=BADGE
                assert np.all(a[y0:y1,x0:x1]==255)
                assert np.array_equal(p[y0:y1,x0:x1,:3],native_rgb[y0:y1,x0:x1])
                result['complete_badge_layer_region_unchanged']=True
            assert np.array_equal(p[opaque,:3],native_rgb[opaque])
            result['all_fully_opaque_source_rgb_pixels_unchanged']=True
        return result

def make_proofs(root: Path):
    qa=root/'03_Visual_QA'
    qa.mkdir(exist_ok=True)
    n=256
    board=Image.new('RGB',(1720,1170),'#F2F4F8');d=ImageDraw.Draw(board)
    d.text((40,26),'Heads up | Transparent PNG exports',font=font(34,True),fill='#14243C')
    d.text((40,78),'Approved artwork. Transparent outside the tile or circle; no outer canvas or halo.',font=font(22),fill='#42556E')
    for j,kind in enumerate(KINDS):
        x=90+j*540
        d.text((x+255,125),kind,font=font(25,True),fill='#14243C',anchor='mt')
        d.text((x+124,163),'Rounded square',font=font(18),fill='#42556E',anchor='mt')
        d.text((x+389,163),'Circle',font=font(18),fill='#42556E',anchor='mt')
        for i,context in enumerate(('Checkerboard','White','Dark')):
            y=200+i*302
            for q,shape in enumerate(('Rounded-Square','Circle')):
                px=x+q*265
                bg=make_checker(n,n) if context=='Checkerboard' else Image.new('RGB',(n,n),'#FFFFFF' if context=='White' else '#101827')
                stem=f'heads-up-{kind.lower()}' + ('-circle' if shape=='Circle' else '')
                icon=Image.open(root/f'01_Icons/{shape}/{kind}/{stem}-{n}.png').convert('RGBA')
                bg.paste(icon,(0,0),icon)
                board.paste(bg,(px,y))
            d.text((x,y+265),context,font=font(18),fill='#42556E')
    d.text((40,1127),'Backgrounds shown here are test surfaces only. They are not embedded in the exported icon files.',font=font(20),fill='#42556E')
    board.save(qa/'transparency-on-backgrounds.png')
    small=Image.new('RGB',(1700,1280),'#F2F4F8');ds=ImageDraw.Draw(small)
    ds.text((32,24),'Native-size PNG checks',font=font(31,True),fill='#14243C')
    ds.text((32,69),'Actual pixel dimensions. Every export shown on both white and dark surfaces.',font=font(20),fill='#42556E')
    for col,size in enumerate((16,32,48,64,128)):
        ds.text((200+col*290+138,110),f'{size} px',font=font(18),fill='#42556E',anchor='mt')
    for ki,kind in enumerate(KINDS):
        for sh,shape in enumerate(('Rounded-Square','Circle')):
            y=147+(ki*2+sh)*175
            ds.text((32,y+40),kind,font=font(23,True),fill='#14243C')
            ds.text((32,y+75),'Tile' if sh==0 else 'Circle',font=font(20),fill='#42556E')
            for col,size in enumerate((16,32,48,64,128)):
                x=200+col*290
                stem=f'heads-up-{kind.lower()}'+('-circle' if sh else '')
                ic=Image.open(root/f'01_Icons/{shape}/{kind}/{stem}-{size}.png')
                for c,bc in enumerate(('#FFFFFF','#101827')):
                    ds.rectangle((x+c*138,y,x+(c+1)*138-1,y+143),fill=bc)
                    small.paste(ic,(x+c*138+(138-size)//2,y+(144-size)//2),ic)
    ds.text((32,1220),'At 16-32 px, severity should also be stated in text; retained badge pixels do not guarantee readable punctuation.',font=font(19),fill='#42556E')
    small.save(qa/'native-size-checks.png')
    # Standalone checkerboard strip for the main response.
    strip=Image.new('RGB',(1130,465),'#F2F4F8');z=ImageDraw.Draw(strip)
    z.text((30,20),'Heads up | True transparency',font=font(29,True),fill='#14243C')
    for j,kind in enumerate(KINDS):
        x=30+j*375
        z.text((x+160,68),kind,font=font(22,True),fill='#14243C',anchor='mt')
        bg=make_checker(320,320,20)
        im=Image.open(root/f'01_Icons/Rounded-Square/{kind}/heads-up-{kind.lower()}-1024.png').resize((320,320),Image.Resampling.LANCZOS)
        bg.paste(im,(0,0),im);strip.paste(bg,(x,102))
    z.text((30,438),'Checkerboard is a preview surface only. Exported PNG corners are transparent.',font=font(16),fill='#42556E')
    strip.save(qa/'transparent-png-preview.png')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-zip',type=Path,required=True)
    parser.add_argument('--original-zip',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    root=args.output;root.mkdir(parents=True,exist_ok=True)
    tech=root/'04_Technical';tech.mkdir(exist_ok=True)
    (root/'02_Native_Assets').mkdir(exist_ok=True)
    sizes=set(REQUIRED_SIZES)
    if args.original_zip:
        with zipfile.ZipFile(args.original_zip) as z:
            for name in z.namelist():
                m=re.search(r'/icons/main/main_(\d+)\.png$',name)
                if m:sizes.add(int(m.group(1)))
    sizes=sorted(sizes)
    with zipfile.ZipFile(args.source_zip) as z:
        full_data=z.read(f'{ROOTNAME}/00_Reference/main-approved-native.png')
        full=np.asarray(Image.open(BytesIO(full_data)).convert('RGB'))
        source_rgb={}
        source_hashes={}
        for kind in KINDS:
            data=z.read(f'{ROOTNAME}/01_Tile_Layouts/heads-up-{kind.lower()}-tile-1088.png')
            source_rgb[kind]=np.asarray(Image.open(BytesIO(data)).convert('RGB'))
            source_hashes[kind]=hashlib.sha256(data).hexdigest()
    assert full.shape==(1254,1254,3)
    assert all(v.shape==(D,D,3) for v in source_rgb.values())
    xy,radii=trace_boundary(full)
    (tech/'tile-alpha-boundary.json').write_text(json.dumps({'coordinate_system':'approved tight tile, 1088 x 1088','source_canvas_crop_xyxy':BOX,'contour_points_xy':xy.round(5).tolist(),'note':'Transparency-only raster rim trace; not a vector icon master.'},indent=2))
    icc=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    records=[]
    edge_counts={}
    for circular in (False,True):
        shape='Circle' if circular else 'Rounded-Square'
        masks={n:alpha_mask(xy,n,circular) for n in [*sizes,D]}
        for kind in KINDS:
            dest=root/f'01_Icons/{shape}/{kind}';dest.mkdir(parents=True,exist_ok=True)
            native,count=native_rgba(source_rgb[kind],masks[D])
            edge_counts[f'{shape}/{kind}']=count
            stem=f'heads-up-{kind.lower()}'+('-circle' if circular else '')
            native_path=root/'02_Native_Assets'/f'{stem}-1088.png'
            if not native_path.exists():
                native.save(native_path,icc_profile=icc,compress_level=4)
            rec=check_png(native_path,masks[D],source_rgb[kind],kind)
            rec['path']=str(native_path.relative_to(root));records.append(rec)
            for size in sizes:
                out,missing=export_rgba(native,size,masks[size])
                path=dest/f'{stem}-{size}.png'
                if not path.exists():
                    out.save(path,icc_profile=icc,compress_level=4)
                rec=check_png(path,masks[size]);rec['path']=str(path.relative_to(root))
                if size>=1024: print(shape,kind,size,'complete',flush=True)
                rec['resampled_edge_color_fill_pixels']=missing;records.append(rec)
    make_proofs(root)
    if Path(__file__).resolve() != (tech/'build_transparent_pngs.py').resolve():
        shutil.copyfile(__file__,tech/'build_transparent_pngs.py')
    report={'status':'Approved raster layouts exported as RGBA PNGs; transparency checks passed. Not full brand-kit or vector certification.',
      'approved_review_zip_sha256':sha(args.source_zip),'source_tile_sha256':source_hashes,
      'source_canvas_px':[1254,1254],'approved_tile_crop_xyxy':BOX,'native_tile_size_px':D,
      'output_sizes_px':sizes,'native_references_also_exported_at_px':D,
      'icon_png_count':len(records),'variants':list(KINDS),'shapes':['Rounded-Square','Circle'],
      'boundary_method':'4096 radial samples of the outward green-channel rim edge; 61-sample periodic Savitzky-Golay smoothing of alpha contour only. Interior artwork not redrawn.',
      'circle_method':'Circle inscribed in the approved 1088 px tile, intersected with tile alpha to exclude any exterior pixels at tangencies.',
      'additional_outer_padding':False,'background_or_outer_halo_embedded':False,
      'edge_antialiasing':'Area-coverage alpha, no blur or ringing; premultiplied-alpha RGB resampling.',
      'fully_transparent_pixel_rgb':[0,0,0],'native_partial_alpha_pixel_counts':edge_counts,
      'guarded_core_rectangle_xyxy':CORE,'badge_layer_rectangle_xyxy':BADGE,
      'native_guarded_core_alpha':255,'native_opaque_interior_rgb_changes':0,
      'native_badge_position_or_size_changes':0,
      'limitations':['Approved source is raster; 2048 px files are resampled from the 1088 px tile, not new vector renders.',
                    'At 16-32 px the exclamation mark is not reliably readable; use a text severity label.',
                    'No live Home Assistant or OS integration testing is included.',
                    'This package contains Main, Warning and Critical PNG exports, not the complete 12-variant brand kit.'],
      'files':records}
    (tech/'technical-validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'icons_exported_and_checked':len(records),'sizes':sizes,'native_size':D,'root':str(root)},indent=2))

if __name__=='__main__':main()
