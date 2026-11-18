// img2pgm in.jpg out.pgm : decode an image with ImageIO and write 8-bit grayscale PGM
import Foundation
import ImageIO
import CoreGraphics
let a = CommandLine.arguments
guard let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: a[1]) as CFURL, nil),
      let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else { print("bad image"); exit(1) }
let w = img.width, h = img.height
var buf = [UInt8](repeating: 0, count: w * h)
let cs = CGColorSpaceCreateDeviceGray()
let ctx = CGContext(data: &buf, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w, space: cs, bitmapInfo: CGImageAlphaInfo.none.rawValue)!
ctx.draw(img, in: CGRect(x: 0, y: 0, width: w, height: h))
var out = Data("P5\n\(w) \(h)\n255\n".utf8)
out.append(contentsOf: buf)
try! out.write(to: URL(fileURLWithPath: a[2]))
