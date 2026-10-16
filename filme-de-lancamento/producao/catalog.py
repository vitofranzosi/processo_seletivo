import struct, sys, re, glob, json, os
rows=[]
for path in glob.glob('/Library/Audio/Apple Loops/Apple/**/*.caf', recursive=True):
    d=open(path,'rb').read(); i=8; m={}; sr=None; frames=None
    while i+12<=len(d):
        t=d[i:i+4]; n=struct.unpack('>q',d[i+4:i+12])[0]
        if n<0: break
        body=d[i+12:i+12+n]
        if t==b'desc': sr=struct.unpack('>d',body[:8])[0]
        if t==b'pakt': frames=struct.unpack('>q',body[8:16])[0]
        if t==b'uuid' and b'beat count' in body:
            parts=body[4+16:].split(b'\x00') if False else body.split(b'\x00')
            parts=[p.decode('latin1') for p in parts]
            # key/value pairs separated by NUL after a 4-byte count; find keys
            for k in ['category','subcategory','key signature','key type','beat count','descriptors','genre','time signature']:
                for j,p in enumerate(parts):
                    if p.endswith(k) and j+1<len(parts):
                        m[k]=parts[j+1]; break
        i+=12+n
    dur = frames/sr if (frames and sr) else None
    bc=int(m.get('beat count','0') or 0)
    bpm= round(bc/dur*60,1) if dur and bc else None
    rows.append(dict(name=os.path.basename(path)[:-4], folder=path.split('/')[-2], path=path, dur=round(dur,2) if dur else None, bpm=bpm, **m))
json.dump(rows, open(sys.argv[1],'w'), ensure_ascii=False, indent=0)
print(len(rows))
