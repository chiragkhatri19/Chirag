"""Turns the couple's photos into big-head, cartoon-shaded caricature cut-outs.

Pipeline per outfit:
  1. background removal (tools/cutout.mjs, @imgly/background-removal-node) -> <name>_cut.png
  2. face landmarks (MediaPipe FaceLandmarker) to locate each head
  3. smooth radial "bobble-head" warp anchored at the chin (heads x1.62, bodies unchanged)
  4. painterly cel shading + soft ink lines + white sticker outline

    node tools/cutout.mjs <photos_dir>                # writes <name>_cut.png next to each photo
    python3 tools/make_caricatures.py <photos_dir> <face_landmarker.task> assets/

<photos_dir> holds casual.jpg (garden photo), traditional.jpg (green lehenga close-up) and
formal.jpg (library, standing). The clean-up polygons below are specific to those photos.
The original photos are intentionally not committed.
"""
import os
import sys

import cv2
import numpy as np

def load_rgba(path):
    return cv2.imread(path,cv2.IMREAD_UNCHANGED).astype(np.float32)/255.

def clean_alpha(im, min_frac=0.02, kill_rects=()):
    a=im[...,3].copy()
    a[a<0.12]=0
    for (x0,y0,x1,y1) in kill_rects: a[y0:y1,x0:x1]=0
    m=(a>0.5).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    keep=np.zeros_like(m)
    tot=m.sum()
    for i in range(1,n):
        if st[i,cv2.CC_STAT_AREA]>min_frac*tot: keep[lab==i]=1
    keep=cv2.dilate(keep,np.ones((9,9),np.uint8))
    a=a*cv2.GaussianBlur(keep.astype(np.float32),(9,9),0)
    im[...,3]=a
    return im

def head_params(pts, hair_top=0.55, side=0.72, k=1.45):
    pts=np.array(pts)
    chin=pts[152]; fore=pts[10]; Lp=pts[234]; Rp=pts[454]
    fh=np.linalg.norm(chin-fore); fw=np.linalg.norm(Rp-Lp)
    A=chin+np.array([0,0.04*fh])
    top=fore[1]-hair_top*fh; bot=A[1]+0.10*fh
    cx=(Lp[0]+Rp[0])/2
    return dict(A=A, c=np.array([cx,(top+bot)/2]), a=side*fw, b=(bot-top)/2, M=0.42*fh, k=k)

def warp(im, h):
    H,W=im.shape[:2]
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    vx=xx-h['A'][0]; vy=yy-h['A'][1]
    r=np.sqrt(vx*vx+vy*vy)+1e-6
    dx=vx/r; dy=vy/r
    # ray A + t d intersect ellipse centered c with semi-axes a,b
    ox=(h['A'][0]-h['c'][0])/h['a']; oy=(h['A'][1]-h['c'][1])/h['b']
    ex=dx/h['a']; ey=dy/h['b']
    qa=ex*ex+ey*ey; qb=2*(ox*ex+oy*ey); qc=ox*ox+oy*oy-1
    disc=np.maximum(qb*qb-4*qa*qc,0)
    Rs=(-qb+np.sqrt(disc))/(2*qa)
    k=h['k']; Ro=k*Rs
    u=np.clip(1-(r-Ro)/h['M'],0,1)
    u=u*u*(3-2*u)
    s=1+(k-1)*u
    mx=(h['A'][0]+vx/s).astype(np.float32); my=(h['A'][1]+vy/s).astype(np.float32)
    pm=im.copy(); pm[...,:3]*=pm[...,3:4]
    out=cv2.remap(pm,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
    out=np.clip(out,0,1)
    a=out[...,3:4]; out[...,:3]=np.where(a>1e-4,out[...,:3]/np.maximum(a,1e-4),0)
    return np.clip(out,0,1)

def crop_alpha(im,pad=40):
    ys,xs=np.where(im[...,3]>0.05)
    y0,y1=max(ys.min()-pad,0),min(ys.max()+pad,im.shape[0]); x0,x1=max(xs.min()-pad,0),min(xs.max()+pad,im.shape[1])
    return im[y0:y1,x0:x1]

def save(im,path):
    cv2.imwrite(path,(np.clip(im,0,1)*255+0.5).astype(np.uint8))


def face_landmarks(photo, guesses, model):
    """Runs FaceLandmarker on a crop around each rough face position (faces are small in frame)."""
    import mediapipe as mp
    from mediapipe.tasks import python as mpt
    from mediapipe.tasks.python import vision
    det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=mpt.BaseOptions(model_asset_path=model), num_faces=1, min_face_detection_confidence=0.2))
    im = cv2.cvtColor(cv2.imread(photo), cv2.COLOR_BGR2RGB)
    faces = []
    for (cx, cy) in guesses:
        h = 220
        x0, y0 = max(cx - h, 0), max(cy - h, 0)
        crop = np.ascontiguousarray(im[y0:cy + h, x0:cx + h])
        r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=crop))
        if not r.face_landmarks:
            raise SystemExit(f'no face found near {(cx, cy)} in {photo}')
        ch, cw = crop.shape[:2]
        faces.append([[p.x * cw + x0, p.y * ch + y0] for p in r.face_landmarks[0]])
    det.close()
    return faces

K=1.62

def poly_mask(shape, pts, feather=3):
    m=np.zeros(shape[:2],np.float32)
    cv2.fillPoly(m,[np.array(pts,np.int32)],1.0)
    return cv2.GaussianBlur(m,(0,0),feather) if feather else m

def decontaminate(im):
    a=im[...,3]
    w=(a>0.92).astype(np.float32)
    rgb=im[...,:3]
    num=cv2.GaussianBlur(rgb*w[...,None],(0,0),3); den=cv2.GaussianBlur(w,(0,0),3)[...,None]
    inner=num/np.maximum(den,1e-4)
    t=np.clip((a-0.55)/0.4,0,1)[...,None]
    has=(den>1e-3)
    im[...,:3]=np.where(has, rgb*t+inner*(1-t), rgb)
    # tighten matte a little
    a2=np.clip((a-0.18)/0.7,0,1)
    im[...,3]=a2
    return im

def fix_p4(im):  # formal photo: a plant leaf crosses her leg and hand
    # remove plant leaves crossing her leg/hand, then rebuild the leg edge
    rgb=im[...,:3]; a=im[...,3]
    b,g,r=rgb[...,0],rgb[...,1],rgb[...,2]
    green=(g>r*1.02)&(g>b*1.1)&(a>0.05)
    zone=np.zeros_like(a,bool); zone[920:1100,770:920]=True
    leaf=green&zone
    leaf=cv2.dilate(leaf.astype(np.uint8),np.ones((5,5),np.uint8)).astype(bool)&zone
    leg=poly_mask(im.shape,[(845,1040),(866,1046),(880,1085),(893,1125),(891,1154),(886,1179),(858,1179),(850,1100)],feather=1.0)
    fill=(leaf|((leg>0.5)&(a<0.95))).astype(np.uint8)
    near=cv2.dilate(fill,np.ones((41,41),np.uint8)).astype(bool)
    unknown=(fill>0)|(near&(a<0.95))
    u8=(np.clip(rgb,0,1)*255).astype(np.uint8)
    inp=cv2.inpaint(u8,unknown.astype(np.uint8),15,cv2.INPAINT_TELEA).astype(np.float32)/255
    im[...,:3]=np.where(fill[...,None]>0,inp,rgb)
    a=np.where(leaf,0,a)
    hard=(a>0.5).astype(np.uint8)
    closed=cv2.morphologyEx(hard,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(35,35))).astype(np.float32)
    closed=cv2.GaussianBlur(closed,(0,0),1.0)
    a=np.where(zone,np.maximum(a,closed),a)
    a=np.maximum(a,leg)
    im[...,3]=a
    return im

def kill_green_fringe(im, band=30):
    a=im[...,3]; rgb=im[...,:3]
    b,g,r=rgb[...,0],rgb[...,1],rgb[...,2]
    inner=cv2.erode((a>0.5).astype(np.uint8),np.ones((2*band+1,2*band+1),np.uint8)).astype(bool)
    green=(g>r*0.98)&(g>b*1.08)&~inner&(a>0)
    green=cv2.morphologyEx(green.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8)).astype(bool)
    a=np.where(green,0,a)
    h=(a>0.5).astype(np.uint8)
    ker=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
    h=cv2.morphologyEx(cv2.morphologyEx(h,cv2.MORPH_OPEN,ker),cv2.MORPH_CLOSE,ker)
    n,lab,st,_=cv2.connectedComponentsWithStats(h)
    keep=np.zeros_like(h)
    for i in range(1,n):
        if st[i,cv2.CC_STAT_AREA]>3000: keep[lab==i]=1
    im[...,3]=np.minimum(a,cv2.GaussianBlur(keep.astype(np.float32),(0,0),1.5))
    return im

def stylize(im, scale=1.0):
    if scale!=1.0:
        im=cv2.resize(im,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC); im=np.clip(im,0,1)
    a=im[...,3]
    rgb=(im[...,:3]*255).astype(np.uint8)
    c=cv2.edgePreservingFilter(rgb,flags=1,sigma_s=45,sigma_r=0.28)
    c=cv2.bilateralFilter(c,9,35,9)
    lab=cv2.cvtColor(c,cv2.COLOR_BGR2LAB).astype(np.float32)
    Lc=lab[...,0]; lv=8.0
    qL=np.round(Lc/255*lv)/lv*255
    qL=cv2.GaussianBlur(qL,(0,0),1.2)
    lab[...,0]=np.clip(0.45*qL+0.55*Lc,0,255)
    lab[...,0]=np.clip((lab[...,0]-128)*1.06+134,0,255)
    lab[...,1:]=128+(lab[...,1:]-128)*1.22
    c=cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR).astype(np.float32)
    gg=cv2.cvtColor(rgb,cv2.COLOR_BGR2GRAY).astype(np.float32)
    s1=1.1*max(scale,1); dog=cv2.GaussianBlur(gg,(0,0),s1)-cv2.GaussianBlur(gg,(0,0),s1*2.2)
    line=np.clip(1-np.maximum(-dog-4,0)/14,0.42,1)
    line=cv2.GaussianBlur(line,(0,0),0.6)[...,None]
    c=c*line
    out=np.dstack([np.clip(c/255,0,1),a])
    return out

def add_outline(im, width=10, color=(1,1,1), dark=2):
    a=im[...,3]
    pad=width+dark+8
    im=cv2.copyMakeBorder(im,pad,pad,pad,pad,cv2.BORDER_CONSTANT,value=0)
    a=im[...,3]
    hard=(a>0.35).astype(np.uint8)
    # fill small holes so the outline doesn't creep inside
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*width+1,2*width+1))
    outer=cv2.dilate(hard,k).astype(np.float32)
    outer=cv2.GaussianBlur(outer,(0,0),1.0)
    k2=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*(width+dark)+1,2*(width+dark)+1))
    rim=cv2.GaussianBlur(cv2.dilate(hard,k2).astype(np.float32),(0,0),1.0)
    out=np.zeros_like(im)
    # dark rim
    rimc=np.array([0.10,0.12,0.35],np.float32)  # maroon-ish (BGR)
    out[...,:3]=rimc; out[...,3]=rim*0.9
    # white sticker
    wa=outer
    out[...,:3]=out[...,:3]*(1-wa[...,None])*out[...,3:4]+np.array(color,np.float32)*wa[...,None]
    oa=wa+out[...,3]*(1-wa)
    out[...,:3]=out[...,:3]/np.maximum(oa[...,None],1e-4); out[...,3]=oa
    # character on top
    ca=im[...,3:4]
    rgb=im[...,:3]*ca+out[...,:3]*out[...,3:4]*(1-ca)
    fa=ca[...,0]+out[...,3]*(1-ca[...,0])
    out[...,:3]=rgb/np.maximum(fa[...,None],1e-4); out[...,3]=fa
    return out

def finish(im,name,target_h=None,target_w=None,scale=1.0,outline=10,cut_bottom=False):
    im=crop_alpha(im,pad=10)
    im=decontaminate(im)
    st=stylize(im,scale)
    if target_h: f=target_h/st.shape[0]
    elif target_w: f=target_w/st.shape[1]
    else: f=1
    if f!=1: st=np.clip(cv2.resize(st,None,fx=f,fy=f,interpolation=cv2.INTER_AREA if f<1 else cv2.INTER_CUBIC),0,1)
    st=add_outline(st,outline)
    if cut_bottom:
        # photo ends mid-body: drop the outline/padding under the cut so it can sit on a ledge
        ys=np.where((st[...,3]>0.5).any(1))[0]
        st=st[:ys.max()-outline-14]
    save(st,os.path.join(OUT,f'{name}.png'))
    return st

if __name__ == '__main__':
    PH, MODEL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(OUT, exist_ok=True)
    P = lambda n: os.path.join(PH, n)
    # 1) casual garden look (half body)
    L = face_landmarks(P('casual.jpg'), [(770, 360), (1045, 345)], MODEL)
    im = kill_green_fringe(clean_alpha(load_rgba(P('casual_cut.png'))))
    for i, (ht, sd) in enumerate([(0.55, 0.72), (0.45, 0.8)]):
        im = warp(im, head_params(L[i], ht, sd, k=K))
    finish(im, 'caricature_casual', target_w=1000, scale=1.0, cut_bottom=True)
    # 2) traditional: heads touch and she is in front, so her head is warped on its own layer
    L = face_landmarks(P('traditional.jpg'), [(430, 615), (585, 690)], MODEL)
    im = clean_alpha(load_rgba(P('traditional_cut.png')), kill_rects=[(195, 1050, 300, 1190)])
    PF = poly_mask(im.shape, [(490, 380), (720, 380), (720, 810), (412, 810), (430, 780), (447, 753), (463, 733), (480, 700),
                              (470, 673), (463, 653), (461, 633), (467, 610), (477, 590), (483, 575)], feather=0)
    base = im.copy(); base[..., 3] *= (1 - PF)
    base = warp(base, head_params(L[0], 0.62, 0.72, k=K))
    lay = im.copy(); lay[..., 3] *= PF
    lay = warp(lay, head_params(L[1], 0.42, 0.8, k=K))
    a1 = lay[..., 3:4]; out = base.copy()
    out[..., :3] = lay[..., :3] * a1 + base[..., :3] * base[..., 3:4] * (1 - a1)
    oa = np.clip(a1[..., 0] + base[..., 3] * (1 - a1[..., 0]), 0, 1)
    out[..., :3] /= np.maximum(oa[..., None], 1e-4); out[..., 3] = oa
    finish(out, 'caricature_traditional', target_h=1500, scale=1.4)
    # 3) formal library look
    L = face_landmarks(P('formal.jpg'), [(385, 395), (690, 375)], MODEL)
    im = fix_p4(clean_alpha(load_rgba(P('formal_cut.png'))))
    for i, (ht, sd) in enumerate([(0.62, 0.72), (0.5, 0.85)]):
        im = warp(im, head_params(L[i], ht, sd, k=K))
    finish(im, 'caricature_formal', target_h=1500, scale=1.1)
    print('wrote caricatures to', OUT)
