// ppm2png in.ppm out.png : write a binary P6 PPM as PNG
import Foundation
import ImageIO
import CoreGraphics
import UniformTypeIdentifiers
let a = CommandLine.arguments
let d = try! Data(contentsOf: URL(fileURLWithPath: a[1]))
var bytes = [UInt8](d)
// parse header: P6\nW H\n255\n
var idx = 0; var fields: [String] = []
while fields.count < 4 {
  var s = ""
  while idx < bytes.count, bytes[idx] == 32 || bytes[idx] == 10 || bytes[idx] == 13 || bytes[idx] == 9 { idx += 1 }
  while idx < bytes.count, !(bytes[idx] == 32 || bytes[idx] == 10 || bytes[idx] == 13 || bytes[idx] == 9) { s.append(Character(UnicodeScalar(bytes[idx]))); idx += 1 }
  fields.append(s)
}
idx += 1
let w = Int(fields[1])!, h = Int(fields[2])!
var px = Array(bytes[idx..<(idx + w*h*3)])
let cs = CGColorSpaceCreateDeviceRGB()
let prov = CGDataProvider(data: Data(px) as CFData)!
let img = CGImage(width: w, height: h, bitsPerComponent: 8, bitsPerPixel: 24, bytesPerRow: w*3, space: cs, bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.none.rawValue), provider: prov, decode: nil, shouldInterpolate: false, intent: .defaultIntent)!
let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: a[2]) as CFURL, UTType.png.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(dest, img, nil)
CGImageDestinationFinalize(dest)
