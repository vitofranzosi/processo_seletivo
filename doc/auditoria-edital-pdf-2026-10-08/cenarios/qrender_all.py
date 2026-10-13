import sys
import Quartz
from Foundation import NSURL
pdf, prefix, scale = sys.argv[1], sys.argv[2], float(sys.argv[3])
doc = Quartz.CGPDFDocumentCreateWithURL(NSURL.fileURLWithPath_(pdf))
n = Quartz.CGPDFDocumentGetNumberOfPages(doc)
for page_no in range(1, n+1):
    page = Quartz.CGPDFDocumentGetPage(doc, page_no)
    box = Quartz.CGPDFPageGetBoxRect(page, Quartz.kCGPDFMediaBox)
    w, h = int(box.size.width*scale), int(box.size.height*scale)
    ctx = Quartz.CGBitmapContextCreate(None, w, h, 8, 0, Quartz.CGColorSpaceCreateDeviceRGB(), Quartz.kCGImageAlphaPremultipliedLast)
    Quartz.CGContextSetRGBFillColor(ctx, 1, 1, 1, 1); Quartz.CGContextFillRect(ctx, Quartz.CGRectMake(0,0,w,h))
    Quartz.CGContextScaleCTM(ctx, scale, scale); Quartz.CGContextDrawPDFPage(ctx, page)
    out = f"{prefix}-{page_no:02d}.png"
    dest = Quartz.CGImageDestinationCreateWithURL(NSURL.fileURLWithPath_(out), "public.png", 1, None)
    Quartz.CGImageDestinationAddImage(dest, Quartz.CGBitmapContextCreateImage(ctx), None); Quartz.CGImageDestinationFinalize(dest)
print(n, "pages")
