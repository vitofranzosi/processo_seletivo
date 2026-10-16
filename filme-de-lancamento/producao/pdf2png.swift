import Foundation
import PDFKit
import AppKit
let args = CommandLine.arguments
let doc = PDFDocument(url: URL(fileURLWithPath: args[1]))!
let scale = CGFloat(Double(args[3]) ?? 3.0)
for i in 0..<doc.pageCount {
    let page = doc.page(at: i)!
    let r = page.bounds(for: .mediaBox)
    let w = Int(r.width * scale), h = Int(r.height * scale)
    let cs = CGColorSpaceCreateDeviceRGB()
    let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0, space: cs, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1)); ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: ctx)
    let img = ctx.makeImage()!
    let rep = NSBitmapImageRep(cgImage: img)
    let data = rep.representation(using: .png, properties: [:])!
    try! data.write(to: URL(fileURLWithPath: String(format: "%@_%02d.png", args[2], i + 1)))
}
print(doc.pageCount)
