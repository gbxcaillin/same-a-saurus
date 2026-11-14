"""Turns raw OpenArt output into game-ready assets.
Usage: python3 tools/make_assets.py <raw_dir> <proc_dir> <assets_dir>
raw_dir: OpenArt downloads; proc_dir: normalised 1024px sprites (see prep step in README)."""
import sys, os, subprocess, tempfile
import numpy as np
from PIL import Image
raw, proc, out = sys.argv[1:4]
SPECIES = ['trex','trice','stego','bronto','ptero','centro','carno','para']

def save_webp(im, path, q=86):
    im.save(path, 'WEBP', quality=q, method=6)

def statics():
    for n in SPECIES:
        im = Image.open(f'{proc}/{n}.png').convert('RGBA').resize((512,512), Image.LANCZOS)
        save_webp(im, f'{out}/sprites/{n}.webp', 88)

def worn(src, dst, kinds):
    """Dinosaurs redrawn wearing an accessory: raw/<src>/<species>_<kind>.png -> assets/<dst>/*.webp"""
    os.makedirs(f'{out}/{dst}', exist_ok=True)
    for n in SPECIES:
        for w in kinds:
            p = f'{raw}/{src}/{n}_{w}.png'
            if not os.path.exists(p): continue
            im = Image.open(p).convert('RGBA')
            a = im.split()[3].point(lambda v: 255 if v > 24 else 0)
            im = im.crop(a.getbbox()); S = 512; m = int(S*0.08); sc = min((S-2*m)/im.width, (S-2*m)/im.height)
            im = im.resize((round(im.width*sc), round(im.height*sc)), Image.LANCZOS)
            cv = Image.new('RGBA', (S, S), (0,0,0,0)); cv.alpha_composite(im, ((S-im.width)//2, (S-im.height)//2))
            save_webp(cv, f'{out}/{dst}/{n}_{w}.webp', 86)

def crop_alpha(im, pad=6):
    a = im.split()[3].point(lambda v: 255 if v > 20 else 0)
    x0,y0,x1,y1 = a.getbbox()
    return im.crop((max(0,x0-pad),max(0,y0-pad),min(im.width,x1+pad),min(im.height,y1+pad)))

def accessories():
    for n in ['sg_star','sg_heart','sg_round','sg_square','hair_mohawk','hair_afro','hair_pigtails','hair_quiff']:
        im = crop_alpha(Image.open(f'{raw}/{n}.png').convert('RGBA'))
        w = 320; im = im.resize((w, round(im.height*w/im.width)), Image.LANCZOS)
        save_webp(im, f'{out}/acc/{n}.webp', 88)
        print(n, im.size)

def misc():
    bg = Image.open(f'{raw}/bg.png').convert('RGB').resize((1400,1400), Image.LANCZOS)
    save_webp(bg, f'{out}/bg.webp', 80)
    logo = crop_alpha(Image.open(f'{raw}/logo_b.png').convert('RGBA'), 10)
    logo = logo.resize((1000, round(logo.height*1000/logo.width)), Image.LANCZOS)
    save_webp(logo, f'{out}/logo.webp', 90); print('logo', logo.size)
    for p in ['party','party2','intro']:
        if os.path.exists(f'{raw}/{p}.png'):
            save_webp(Image.open(f'{raw}/{p}.png').convert('RGB').resize((640,640), Image.LANCZOS), f'{out}/{p}.webp', 78)
    ic = Image.open(f'{raw}/icon.png').convert('RGB')
    ic.resize((512,512), Image.LANCZOS).save(f'{out}/icon-512.png', optimize=True)
    ic.resize((180,180), Image.LANCZOS).save(f'{out}/icon-180.png', optimize=True)

def key_magenta(fr):
    """fr: HxWx3 uint8 on magenta. Returns RGBA with soft edge + despill."""
    f = fr.astype(np.float32)
    r,g,b = f[...,0],f[...,1],f[...,2]
    m = np.minimum(r,b) - g                     # magenta-ness
    alpha = 1 - np.clip((m-35)/(120-35), 0, 1)
    ex = np.clip(m, 0, None)                    # despill
    r2 = r-ex; b2 = b-ex
    # edge pixels that lost colour: darken toward outline navy
    out_ = np.stack([r2,g,b2,alpha*255],-1)
    return np.clip(out_,0,255).astype(np.uint8)

def dance(n, frames, size=256):
    """frames: list of source frame numbers (24fps) forming the forward half of a ping-pong loop."""
    src = f'{raw}/{n}_dance.mp4'
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(['ffmpeg','-v','error','-y','-i',src,f'{td}/f%03d.png'],check=True)
        strip = Image.new('RGBA',(size*len(frames),size),(0,0,0,0))
        for i,fn in enumerate(frames):
            fr = np.array(Image.open(f'{td}/f{fn+1:03d}.png').convert('RGB'))
            im = Image.fromarray(key_magenta(fr),'RGBA').resize((size,size), Image.LANCZOS)
            strip.paste(im,(i*size,0))
        save_webp(strip, f'{out}/dance/{n}.webp', 84)
    print('dance',n,len(frames))

def video(name, size=480, crf='29'):
    src=f'{raw}/{name}.mp4'
    if os.path.exists(src):
        subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-an','-vf',f'scale={size}:{size}','-c:v','libx264','-profile:v','main','-level','3.1','-pix_fmt','yuv420p','-crf',crf,'-preset','veryslow','-movflags','+faststart',f'{out}/{name}.mp4'],check=True)

if __name__=='__main__':
    import json
    statics(); accessories(); misc()
    worn('wig', 'hair', ['mohawk','afro','pigtails','quiff']); worn('shades', 'shades', ['star','heart','round','square'])
    cfg = json.load(open(os.path.join(os.path.dirname(__file__),'dance_frames.json')))
    for n,fr in cfg.items():
        if os.path.exists(f'{raw}/{n}_dance.mp4'): dance(n, fr)
    video('party'); video('party2'); video('intro', 720, '25')    # full-resolution master is kept in masters/
