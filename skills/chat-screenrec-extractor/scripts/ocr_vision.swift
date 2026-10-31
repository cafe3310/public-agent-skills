import Foundation
import Vision
import CoreGraphics
import ImageIO

struct OCRBBox: Codable {
    let x: Double
    let y: Double
    let w: Double
    let h: Double
}

struct OCRItem: Codable {
    let text: String
    let confidence: Float
    let bbox: OCRBBox             // Pixel coordinates (top-left origin: x, y, w, h)
    let normalized_bbox: OCRBBox  // Normalized coordinates (0..1, top-left origin: x, y, w, h)
    let width_px: Double          // 区域宽度 (像素)
    let height_px: Double         // 区域高度 (像素)
    let font_size_px: Double      // 估算字体大小 (像素高度)
    let font_size_pt: Double      // 估算字体大小 (点数 pt @ 逻辑分辨率)
}

struct ImageOCRResult: Codable {
    let image_path: String
    let width: Int
    let height: Int
    let results: [OCRItem]
}

func performOCR(imageURL: URL) -> ImageOCRResult? {
    guard let imageSource = CGImageSourceCreateWithURL(imageURL as CFURL, nil),
          let cgImage = CGImageSourceCreateImageAtIndex(imageSource, 0, nil) else {
        return nil
    }

    let imgWidth = cgImage.width
    let imgHeight = cgImage.height
    // Estimate scale factor (standard modern mobile screen ~393pt width)
    let scaleFactor = max(1.0, Double(imgWidth) / 393.0)

    var items: [OCRItem] = []
    let requestHandler = VNImageRequestHandler(cgImage: cgImage, options: [:])

    let request = VNRecognizeTextRequest { (request, error) in
        guard let observations = request.results as? [VNRecognizedTextObservation] else {
            return
        }

        for observation in observations {
            guard let topCandidate = observation.topCandidates(1).first else { continue }
            let text = topCandidate.string
            let confidence = topCandidate.confidence

            // Apple Vision coordinates: origin is bottom-left, (0,0) to (1,1)
            // Convert to top-left origin coordinates
            let box = observation.boundingBox
            let normX = Double(box.origin.x)
            let normY = Double(1.0 - (box.origin.y + box.size.height))
            let normW = Double(box.size.width)
            let normH = Double(box.size.height)

            let pixX = Double(round(normX * Double(imgWidth) * 10) / 10)
            let pixY = Double(round(normY * Double(imgHeight) * 10) / 10)
            let pixW = Double(round(normW * Double(imgWidth) * 10) / 10)
            let pixH = Double(round(normH * Double(imgHeight) * 10) / 10)

            // Font size calculation
            let fontSizePx = pixH
            let fontSizePt = Double(round((pixH / scaleFactor) * 10) / 10)

            let item = OCRItem(
                text: text,
                confidence: confidence,
                bbox: OCRBBox(x: pixX, y: pixY, w: pixW, h: pixH),
                normalized_bbox: OCRBBox(x: normX, y: normY, w: normW, h: normH),
                width_px: pixW,
                height_px: pixH,
                font_size_px: fontSizePx,
                font_size_pt: fontSizePt
            )
            items.append(item)
        }
    }

    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    if #available(macOS 13.0, *) {
        request.recognitionLanguages = ["zh-Hans", "zh-Hant", "en-US"]
    }

    do {
        try requestHandler.perform([request])
        return ImageOCRResult(
            image_path: imageURL.path,
            width: imgWidth,
            height: imgHeight,
            results: items
        )
    } catch {
        return ImageOCRResult(
            image_path: imageURL.path,
            width: imgWidth,
            height: imgHeight,
            results: []
        )
    }
}

func main() {
    let args = CommandLine.arguments
    if args.count < 2 {
        fputs("Usage: ocr_vision <image_path_or_json_list_or_directory> [--output <output.json>]\n", stderr)
        exit(1)
    }

    var inputPaths: [String] = []
    var outputPath: String? = nil

    var i = 1
    while i < args.count {
        let arg = args[i]
        if arg == "--output" || arg == "-o" {
            if i + 1 < args.count {
                outputPath = args[i + 1]
                i += 2
                continue
            }
        } else if arg.hasPrefix("--") {
            i += 1
            continue
        } else {
            inputPaths.append(arg)
            i += 1
        }
    }

    var targetImageURLs: [URL] = []
    let fileManager = FileManager.default

    for path in inputPaths {
        var isDir: ObjCBool = false
        if fileManager.fileExists(atPath: path, isDirectory: &isDir) {
            if isDir.boolValue {
                if let enumerator = fileManager.enumerator(atPath: path) {
                    for case let file as String in enumerator {
                        let lower = file.lowercased()
                        if lower.hasSuffix(".jpg") || lower.hasSuffix(".jpeg") || lower.hasSuffix(".png") {
                            targetImageURLs.append(URL(fileURLWithPath: path).appendingPathComponent(file))
                        }
                    }
                }
            } else if path.hasSuffix(".json") {
                if let data = try? Data(contentsOf: URL(fileURLWithPath: path)),
                   let list = try? JSONDecoder().decode([String].self, from: data) {
                    for item in list {
                        targetImageURLs.append(URL(fileURLWithPath: item))
                    }
                }
            } else {
                targetImageURLs.append(URL(fileURLWithPath: path))
            }
        }
    }

    // Sort to keep natural frame order
    targetImageURLs.sort { $0.path < $1.path }

    var allResults = [ImageOCRResult?](repeating: nil, count: targetImageURLs.count)
    let syncQueue = DispatchQueue(label: "ocr_sync_queue")

    // Hardware-accelerated multi-core concurrent OCR
    DispatchQueue.concurrentPerform(iterations: targetImageURLs.count) { idx in
        let url = targetImageURLs[idx]
        if let res = performOCR(imageURL: url) {
            syncQueue.sync {
                allResults[idx] = res
            }
        }
    }

    let validResults = allResults.compactMap { $0 }

    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted]
    if let jsonData = try? encoder.encode(validResults),
       let jsonString = String(data: jsonData, encoding: .utf8) {
        if let out = outputPath {
            try? jsonString.write(toFile: out, atomically: true, encoding: .utf8)
        } else {
            print(jsonString)
        }
    }
}

main()
