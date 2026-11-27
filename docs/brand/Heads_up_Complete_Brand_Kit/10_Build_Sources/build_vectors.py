from __future__ import annotations
from pathlib import Path
import json, copy, hashlib
from io import BytesIO
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt, gaussian_filter, map_coordinates, binary_erosion
from scipy.interpolate import splprep, splev
from skimage.measure import find_contours
from skimage.metrics import structural_similarity
from lxml import etree as ET
import cairosvg

ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent
APP=WORK/'approved_png/Heads_up_Transparent_PNGs'
LAYOUT=WORK/'approved_layout/Heads_up_Tile_Boundary_Review'
ORIG=WORK/'original/heads_up_brand_package'
D=1088
NS='http://www.w3.org/2000/svg'
S=lambda name:f'{{{NS}}}{name}'

def tag(name, parent=None, **attrs):
    node=ET.Element(S(name), {k.replace('_','-'):str(v) for k,v in attrs.items()})
    if parent is not None:parent.append(node)
    return node

def spline_path(contour, smooth=0.04):
    p=np.asarray(contour,float)
    if np.linalg.norm(p[0]-p[-1])>1e-6:p=np.vstack([p,p[0]])
    # Periodic cubic spline, squared fitting tolerance in source pixels.
    tck,_=splprep(p.T, s=len(p)*smooth, per=True)
    knots=np.unique(tck[0]);lo=tck[0][3];hi=tck[0][-4]
    knots=knots[(knots>=lo)&(knots<=hi)]
    out=[]
    for i,(a,b) in enumerate(zip(knots[:-1],knots[1:])):
        p0=np.array(splev(a,tck));p3=np.array(splev(b,tck))
        p1=p0+np.array(splev(a,tck,der=1))*(b-a)/3
        p2=p3-np.array(splev(b,tck,der=1))*(b-a)/3
        if i==0:out.append('M '+','.join(f'{v:.3f}' for v in p0))
        out.append('C '+ ' '.join(','.join(f'{v:.3f}' for v in q) for q in (p1,p2,p3)))
    return ' '.join(out)+' Z'

def make_svg(title):
    svg=ET.Element(S('svg'),nsmap={None:NS},width='1024',height='1024',viewBox='0 0 1088 1088',version='1.1')
    tag('title',svg).text=title
    tag('desc',svg).text='Heads up. Shared house and bell outlines traced from the user-approved raster layout. No embedded raster imagery or external dependencies.'
    return svg,tag('defs',svg)

def png(svg,size=D):
    return Image.open(BytesIO(cairosvg.svg2png(bytestring=ET.tostring(svg),output_width=size,output_height=size))).convert('RGBA')

def hexrgb(a):return '#'+''.join(f'{int(v):02X}' for v in np.clip(np.rint(a),0,255))

def hue_map(rgb,kind):
    if kind=='Main':return np.clip(np.rint(rgb),0,255).astype(np.uint8)
    a=np.array(rgb,dtype=np.uint8).reshape(-1,1,3)
    h=cv2.cvtColor(a.astype(np.float32)/255,cv2.COLOR_RGB2HSV);h[:,:,0]/=360
    if kind=='Warning':h[:,:,0]=np.clip(.115-(h[:,:,0]-.5)*.50,.035,.13)
    else:h[:,:,0]=np.mod(.005+(h[:,:,0]-.5)*.025,1)
    h[:,:,0]*=360
    return np.rint(cv2.cvtColor(h,cv2.COLOR_HSV2RGB)*255).clip(0,255).astype(np.uint8).reshape(np.shape(rgb))

native=np.array(Image.open(APP/'02_Native_Assets/heads-up-main-1088.png'))
rgb=native[:,:,:3]
y,x=np.indices((D,D))
roi=(x>200)&(x<880)&(y>140)&(y<840)
mask=((rgb[:,:,1]>140)&roi).astype(np.uint8)
n,labels,stats,cents=cv2.connectedComponentsWithStats(mask)
ids=sorted(range(1,n),key=lambda i:stats[i,4],reverse=True)[:3]
components={k:labels==i for k,i in zip(['house','bell','clapper'],ids)}
mask=np.logical_or.reduce(list(components.values()))
expanded=cv2.dilate(mask.astype(np.uint8),np.ones((17,17),np.uint8))
background=cv2.inpaint(rgb,expanded,15,cv2.INPAINT_TELEA)
# Restore non-glyph source pixels without changing the color reference.
bg=background.astype(float)
localmax=cv2.dilate(rgb[:,:,1],np.ones((11,11),np.uint8)).astype(float)
a=(rgb[:,:,1]-bg[:,:,1])/np.maximum(localmax-bg[:,:,1],1)
a=np.clip(a,0,1)
geometry={}
for k,comp in components.items():
    valid=cv2.dilate(comp.astype(np.uint8),np.ones((7,7),np.uint8))>0
    field=np.where(valid,a,0)
    cs=find_contours(field,.5)
    cs=[c for c in cs if len(c)>25]
    geometry[k]=' '.join(spline_path(c[:,::-1]+.5) for c in cs)
xy=np.array(json.loads((APP/'04_Technical/tile-alpha-boundary.json').read_text())['contour_points_xy'])
geometry['tile']=spline_path(xy,smooth=.02)
(ROOT/'geometry.json').write_text(json.dumps(geometry,indent=2))
np.savez_compressed(ROOT/'reference_fields.npz',rgb=rgb,background=background,mask=mask,alpha=a)

# Foreground color reconstruction: solve a projected multi-stop gradient per component.
# The coordinates are measured from the source; no core geometry is redesigned.
gradients={};gradient_metrics={}
for k,comp in components.items():
    sample=binary_erosion(comp,iterations=5)
    ys,xs=np.where(sample)
    vals=rgb[ys,xs].astype(float)
    sel=np.arange(0,len(xs),max(1,len(xs)//7000));xs=xs[sel];ys=ys[sel];vals=vals[sel]
    best=None
    for theta in np.linspace(0,np.pi/2,61):
        u=np.array([np.cos(theta),np.sin(theta)])
        t=xs*u[0]+ys*u[1]; lo,hi=t.min(),t.max();tn=(t-lo)/(hi-lo)
        nodes=np.linspace(0,1,15)
        centers=[]
        for v in nodes:
            nearest=np.argsort(abs(tn-v))[:max(40,len(tn)//40)]
            centers.append(np.median(vals[nearest],axis=0))
        pred=np.stack([np.interp(tn,nodes,np.array(centers)[:,c]) for c in range(3)],axis=-1)
        err=np.mean((pred-vals)**2)
        if best is None or err<best[0]:best=(err,u,lo,hi,nodes,np.array(centers))
    err,u,lo,hi,nodes,colors=best
    gradients[k]={'start':list(u*lo),'end':list(u*hi),'offsets':list(nodes),'colors':colors.tolist()}
    gradient_metrics[k]={'rgb_rmse_inside_glyph':float(np.sqrt(err))}
(ROOT/'foreground-gradients.json').write_text(json.dumps(gradients,indent=2))

# Background is reconstructed with continuous crossed linear gradients.
# Each row is a genuine vector gradient, crossfaded vertically; no pixel mosaic.
alpha=native[:,:,3]>127
dist=distance_transform_edt(alpha)
valid=dist>=5
near=distance_transform_edt(~valid,return_distances=False,return_indices=True)
field=background.copy();field[~valid]=background[near[0][~valid],near[1][~valid]]
field=gaussian_filter(field.astype(float),sigma=(1.2,1.2,0))
# Fine source sampling near the rounded tile edge is restored by a thin traced rim.
xs=np.unique(np.r_[0,2,4,8,np.arange(8,D,8),D-8,D-4,D-2,D-1]).astype(float)
ys=xs.copy()
xx,yy=np.meshgrid(xs,ys)
grid=np.stack([map_coordinates(field[:,:,c],[yy,xx],order=1,mode='nearest') for c in range(3)],axis=-1)
(ROOT/'background-gradients.json').write_text(json.dumps({'xs':xs.tolist(),'ys':ys.tolist(),'rgb':np.round(grid,2).tolist()}))


def add_crossed_gradients(defs,parent,kind):
    cols=hue_map(grid,kind)
    for j,yp in enumerate(ys):
        grad=tag('linearGradient',defs,id=f'surface-row-{j}',gradientUnits='userSpaceOnUse',x1=0,y1=0,x2=D-1,y2=0)
        for i,xp in enumerate(xs):tag('stop',grad,offset=f'{xp/(D-1):.7f}',stop_color=hexrgb(cols[j,i]))
        attrs={'x':0,'y':0,'width':D,'height':D,'fill':f'url(#surface-row-{j})'}
        if j>0:
            ramp=tag('linearGradient',defs,id=f'blend-{j}',gradientUnits='userSpaceOnUse',x1=0,y1=f'{ys[j-1]:.2f}',x2=0,y2=f'{yp:.2f}')
            tag('stop',ramp,offset=0,stop_color='#FFFFFF',stop_opacity=0)
            tag('stop',ramp,offset=1,stop_color='#FFFFFF',stop_opacity=1)
            m=tag('mask',defs,id=f'row-mask-{j}',maskUnits='userSpaceOnUse',maskContentUnits='userSpaceOnUse',x=0,y=0,width=D,height=D)
            tag('rect',m,x=0,y=0,width=D,height=D,fill=f'url(#blend-{j})')
            attrs['mask']=f'url(#row-mask-{j})'
        tag('rect',parent,**attrs)
    # The narrow rim is sampled from the approved native artwork, along its traced contour.
    # Separate short vector strokes follow the actual curved boundary; no exterior halo.
    count=len(xy)
    for j in range(64):
        ids=np.arange(j*count//64-1,(j+1)*count//64+2)%count
        ps=xy[ids]
        tck,u=splprep(ps.T,s=.005*len(ps),per=False)
        ts=np.unique(tck[0][3:-3]);path=[]
        for l,r in zip(ts[:-1],ts[1:]):
            p0=np.array(splev(l,tck));p3=np.array(splev(r,tck))
            p1=p0+np.array(splev(l,tck,der=1))*(r-l)/3
            p2=p3-np.array(splev(r,tck,der=1))*(r-l)/3
            if not path:path.append('M '+','.join(f'{v:.3f}' for v in p0))
            path.append('C '+' '.join(','.join(f'{v:.3f}' for v in q) for q in [p1,p2,p3]))
        start,end=ps[0],ps[-1]
        grad=tag('linearGradient',defs,id=f'rim-{j}',gradientUnits='userSpaceOnUse',x1=start[0],y1=start[1],x2=end[0],y2=end[1])
        for off,point in [(0,start),(.5,ps[len(ps)//2]),(1,end)]:
            v=point-np.array([D/2,D/2]);point=point-v/max(np.linalg.norm(v),1)*1.6
            c=np.array([map_coordinates(rgb[:,:,i].astype(float),[[point[1]],[point[0]]],order=1,mode='nearest')[0] for i in range(3)])
            tag('stop',grad,offset=off,stop_color=hexrgb(hue_map(c,kind)))
        tag('path',parent,d=' '.join(path),fill='none',stroke=f'url(#rim-{j})',stroke_width=4.0)


def add_core(svg,defs,kind=None,original=None):
    group=tag('g',svg,id='house-and-bell',fill_rule='evenodd')
    for k in ['house','bell','clapper']:
        if original is not None:
            mark=copy.deepcopy(defs.find(S('linearGradient')+"[@id='mark']"))
            mark.set('id',f'mark-{k}');mark.set('gradientUnits','userSpaceOnUse')
            component=components[k] if k=='house' else (components['bell']|components['clapper'])
            py,px=np.where(component)
            for key,value in {'x1':px.min(),'y1':py.min(),'x2':px.max()+1,'y2':py.max()+1}.items():mark.set(key,str(value))
            defs.append(mark);fill=f'url(#mark-{k})'
        else:
            g=gradients[k]
            gr=tag('linearGradient',defs,id=f'{k}-color',gradientUnits='userSpaceOnUse',x1=g['start'][0],y1=g['start'][1],x2=g['end'][0],y2=g['end'][1])
            for off,c in zip(g['offsets'],g['colors']):tag('stop',gr,offset=off,stop_color=hexrgb(hue_map(np.array(c),kind)))
            fill=f'url(#{k}-color)'
        tag('path',group,id=k,d=geometry[k],fill=fill)
    return group

variants={
'Main':'main','Bright':'bright','Dark':'dark','Flat-Blue':'flat_blue','Flat-White':'flat_white','Flat-Navy':'flat_navy',
'Transparent-Light':'transparent/on_light','Transparent-Dark':'transparent/on_dark','Monochrome-Black':'transparent/monochrome_black','Monochrome-White':'transparent/monochrome_white',
'Warning':None,'Critical':None}

for kind,orig in variants.items():
    svg,defs=make_svg(f'Heads up - {kind}')
    clip=tag('clipPath',defs,id='tile-clip');tag('path',clip,d=geometry['tile'])
    if kind in ['Main','Warning','Critical']:
        bg_group=tag('g',svg,id='background',clip_path='url(#tile-clip)',color_interpolation='sRGB')
        add_crossed_gradients(defs,bg_group,kind)
        add_core(svg,defs,kind=kind)
        if kind!='Main':
            badge=ET.parse(str(LAYOUT/'04_Technical'/f'{kind.lower()}-badge.svg')).getroot()
            for elem in badge.iter():
                for attr,value in list(elem.attrib.items()):
                    if attr=='id':elem.set(attr,'badge-'+value)
                    elif 'url(#' in value:elem.set(attr,value.replace('url(#','url(#badge-'))
            bg=tag('g',svg,id='severity-badge',transform='translate(578 770) scale(1.2222222222)')
            for ch in badge:bg.append(copy.deepcopy(ch))
    else:
        name=orig.split('/')[-1]
        src=ET.parse(str(ORIG/'icons'/orig/f'{name}.svg')).getroot()
        for g in src.find(S('defs')):defs.append(copy.deepcopy(g))
        rect=src.find(S('rect'))
        if rect is not None:tag('path',svg,id='background',d=geometry['tile'],fill=rect.get('fill'))
        add_core(svg,defs,original=orig)
    out=ROOT/f'{kind}.svg';out.write_bytes(ET.tostring(svg,xml_declaration=True,encoding='UTF-8',pretty_print=True))
    image=png(svg,512);image.save(ROOT/f'{kind}-512.png')
    if kind in ['Main','Warning','Critical']:
        ref=Image.open(APP/f'01_Icons/Rounded-Square/{kind}/heads-up-{kind.lower()}-512.png').convert('RGBA')
        actual=np.array(image);r=np.array(ref);inside=r[:,:,3]==255
        print(kind, 'RGB RMSE',round(float(np.sqrt(np.mean((actual[:,:,:3][inside].astype(float)-r[:,:,:3][inside])**2))),3),
              'SSIM',round(float(structural_similarity(r[:,:,:3],actual[:,:,:3],channel_axis=2,data_range=255)),4),flush=True)
print('Gradient fit',gradient_metrics,flush=True)
# Geometry view at native 1088.
gsvg,gdefs=make_svg('geometry')
for k in ['house','bell','clapper']:tag('path',gsvg,d=geometry[k],fill='#FFFFFF',fill_rule='evenodd')
image=png(gsvg,D);image.save(ROOT/'geometry-mask.png')
print('FINISHED',flush=True)
