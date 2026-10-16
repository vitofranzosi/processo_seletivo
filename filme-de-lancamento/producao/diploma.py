"""Diploma fictício (retrato) para a cena da Mesa de avaliação. Marca d'água "DOCUMENTO FICTÍCIO"."""
import skia
W,H=595,842
st=skia.FILEWStream("diploma_ficticio.pdf"); doc=skia.PDF.MakeDocument(st)
c=doc.beginPage(W,H)
fm=skia.FontMgr()
serif=fm.matchFamilyStyle("Palatino", skia.FontStyle.Normal()); serifB=fm.matchFamilyStyle("Palatino", skia.FontStyle.Bold())
serifI=fm.matchFamilyStyle("Palatino", skia.FontStyle.Italic()); sans=fm.matchFamilyStyle("Helvetica Neue", skia.FontStyle.Bold())
gold=skia.Color4f(0.55,0.45,0.20,1); ink=skia.Color4f(0.12,0.12,0.12,1)
def P(col,stroke=None):
    p=skia.Paint(Color4f=col,AntiAlias=True)
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
    return p
c.clear(skia.Color4f(0.995,0.99,0.97,1))
c.drawRect(skia.Rect.MakeXYWH(24,24,W-48,H-48),P(gold,3)); c.drawRect(skia.Rect.MakeXYWH(34,34,W-68,H-68),P(gold,0.8))
def center(s,y,font,col=ink,track=0):
    w=font.measureText(s)+track*(len(s)-1); x=(W-w)/2
    for ch in s:
        c.drawString(ch,x,y,font,P(col)); x+=font.measureText(ch)+track
center("UNIVERSIDADE DE EXEMPLO",110,skia.Font(sans,15),gold,2.2)
center("MODELO PARA DEMONSTRAÇÃO — SEM VALOR LEGAL",132,skia.Font(sans,8.5),gold,1.2)
center("DIPLOMA",230,skia.Font(serifB,48),ink,6)
f=skia.Font(serif,15); y=310
for l in ["O Reitor da Universidade de Exemplo,","no uso de suas atribuições, confere a"]:
    center(l,y,f); y+=24
center("Ana Silva",y+22,skia.Font(serifI,32)); y+=70
for l in ["o grau de Licenciada em Computação,","concluído em 15 de dezembro de 2019,","e outorga-lhe o presente Diploma, para que","possa gozar de todos os direitos e","prerrogativas legais."]:
    center(l,y,f); y+=24
center("Cidade de Exemplo, 20 de fevereiro de 2020.",y+26,skia.Font(serifI,13))
c.drawCircle(W/2,H-196,34,P(gold,1.6)); c.drawCircle(W/2,H-196,27,P(gold,0.7))
center("UE",H-189,skia.Font(serifB,19),gold,2)
for x0,lab in [(70,"Reitor"),(W-70-170,"Diplomada")]:
    c.drawLine(x0,H-130,x0+170,H-130,P(ink,0.8)); fs=skia.Font(serif,11)
    c.drawString(lab,x0+85-fs.measureText(lab)/2,H-114,fs,P(ink))
c.save(); c.translate(W/2,H/2+40); c.rotate(-55)
wm=skia.Font(sans,62); s="DOCUMENTO FICTÍCIO"
c.drawString(s,-wm.measureText(s)/2,20,wm,P(skia.Color4f(0.85,0.2,0.2,0.15))); c.restore()
doc.endPage(); doc.close(); st.flush()
