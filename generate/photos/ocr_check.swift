// OCR-verify generated receipt photos, using the same Vision framework the app
// uses to discover receipts in a photo library.
//
// PLAN.md's receipt-photos step says "OCR must still read them — verify before
// committing the batch", and that is not a formality: compositing a crisp
// rendered scan into a photographed context adds perspective, shadow and
// camera noise, any of which can push text under Vision's recognition
// threshold. A receipt photo that does not OCR is invisible to the product it
// exists to demonstrate, and nothing about the image looks wrong.
//
// Usage:
//   swift ocr_check.swift <image>... [--expect <substring>]
// Prints, per image: the number of text lines found, and whether an expected
// substring (typically the merchant name or the total) was among them.
// Exit status 1 if any image yields no text at all.

import Foundation
import Vision
import AppKit

var paths: [String] = []
var expects: [String] = []
var args = Array(CommandLine.arguments.dropFirst())
while let a = args.first {
    args.removeFirst()
    if a == "--expect", let v = args.first { expects.append(v); args.removeFirst() }
    else { paths.append(a) }
}
guard !paths.isEmpty else {
    FileHandle.standardError.write("usage: swift ocr_check.swift <image>... [--expect <substr>]\n".data(using: .utf8)!)
    exit(2)
}

func ocr(_ path: String) -> [String] {
    guard let image = NSImage(contentsOfFile: path),
          let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil)
    else { return [] }
    let request = VNRecognizeTextRequest()
    // `accurate` matches what the app asks Vision for; `fast` would report a
    // rosier number than production ever sees.
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["de-DE", "en-US", "es-ES", "sv-SE", "fi-FI"]
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    try? handler.perform([request])
    return (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
}

var failed = false
for path in paths {
    let lines = ocr(path)
    let joined = lines.joined(separator: " ").lowercased()
    let name = (path as NSString).lastPathComponent
    if lines.isEmpty {
        print("FAIL  \(name)  — no text recognised")
        failed = true
        continue
    }
    var note = ""
    if !expects.isEmpty {
        let missing = expects.filter { !joined.contains($0.lowercased()) }
        note = missing.isEmpty ? "  all expected strings found"
                               : "  MISSING: \(missing.joined(separator: ", "))"
        if !missing.isEmpty { failed = true }
    }
    print("ok    \(name)  — \(lines.count) lines\(note)")
}
exit(failed ? 1 : 0)
