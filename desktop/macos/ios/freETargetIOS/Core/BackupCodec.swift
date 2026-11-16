import Foundation
import CryptoKit
import CoreFoundation

public enum FTError: LocalizedError {
    case message(String)
    public var errorDescription: String? { if case let .message(text) = self { return text }; return nil }
}

public enum BackupCodec {
    public static let maximumBytes = 128 * 1024 * 1024
    public static func canonical(_ storage: [String: String]) throws -> Data {
        // Match Python json.dumps(ensure_ascii=False, sort_keys=True,
        // separators=(',', ':')) exactly; do not rely on Foundation's escaping.
        func quoted(_ text: String) -> String {
            var result = "\""
            for scalar in text.unicodeScalars {
                switch scalar.value {
                case 34: result += "\\\""
                case 92: result += "\\\\"
                case 8: result += "\\b"
                case 9: result += "\\t"
                case 10: result += "\\n"
                case 12: result += "\\f"
                case 13: result += "\\r"
                case 0...31: result += String(format:"\\u%04x",scalar.value)
                default: result.unicodeScalars.append(scalar)
                }
            }
            return result + "\""
        }
        return Data(("{" + storage.keys.sorted().map { quoted($0) + ":" + quoted(storage[$0]!) }.joined(separator:",") + "}").utf8)
    }
    public static func validate(_ storage: [String: String]) throws {
        guard storage.count <= 3000 else { throw FTError.message("Too many data keys.") }
        let expectedArrays = ["ft-shooter-profiles-v1", "ft-session-history-v1", "ft-shooter-names"]
        let expectedObjects = ["ft-session-formats-v1", "ft-rule-presets-v1", "ft-page-overrides-v1", "ft-appearance-v1", "ft-last-guns-v1", "ft-last-successful-connection", "ft-custom-logo-v1"]
        for (key, value) in storage {
            guard key.range(of: #"^ft-[A-Za-z0-9][A-Za-z0-9_.:-]{0,126}$"#, options: .regularExpression) != nil,
                  value.utf8.count <= 64 * 1024 * 1024 else { throw FTError.message("Invalid or oversized data entry.") }
            if expectedArrays.contains(key) || expectedObjects.contains(key) {
                let object = try JSONSerialization.jsonObject(with: Data(value.utf8))
                if expectedArrays.contains(key), !(object is [Any]) { throw FTError.message("Invalid array: \(key)") }
                if expectedObjects.contains(key), !(object is [String: Any]) { throw FTError.message("Invalid object: \(key)") }
                if key == "ft-shooter-profiles-v1", let profiles = object as? [Any] {
                    for profile in profiles {
                        guard let p = profile as? [String: Any], p["name"] is String,
                              p["guns"] == nil || p["guns"] is [Any] else { throw FTError.message("Invalid shooter profile.") }
                    }
                }
                if key == "ft-session-history-v1", let records = object as? [Any] {
                    for record in records {
                        guard let r = record as? [String: Any] else { throw FTError.message("Invalid saved session.") }
                        for field in ["rules","shooter"] {
                            if let value=r[field], !(value is NSNull), !(value is [String:Any]) { throw FTError.message("Invalid saved session \(field).") }
                        }
                        if let shots = r["shotData"] {
                            guard shots is [[String: Any]], r["mode"] is String,
                                  let rules = r["rules"] as? [String: Any], rules["mode"] is String else { throw FTError.message("Individual-shot history is missing its rules.") }
                        }
                    }
                }
                if key == "ft-session-formats-v1", let catalog=object as? [String:Any], !(catalog["entries"] is [Any]) { throw FTError.message("Invalid saved session catalog.") }
                if key == "ft-custom-logo-v1" { try validateLogo(object) }
            }
        }
        guard try canonical(storage).count <= maximumBytes else { throw FTError.message("Backup exceeds 128 MB.") }
    }

    public static func validateLogo(_ value: Any) throws {
        guard let logo = value as? [String: Any], let uri = logo["dataURL"] as? String,
              let name = logo["name"] as? String, name.count <= 1024,
              let width = logo["width"] as? Int, let height = logo["height"] as? Int,
              (1...100000).contains(width), (1...100000).contains(height),
              let split = uri.firstIndex(of: ","),
              ["data:image/png;base64", "data:image/webp;base64", "data:image/svg+xml;base64"].contains(String(uri[..<split])),
              let data = Data(base64Encoded: String(uri[uri.index(after: split)...])), !data.isEmpty,
              data.count <= 2 * 1024 * 1024 else { throw FTError.message("Invalid custom logo.") }
        if uri.hasPrefix("data:image/png"), !data.starts(with:[137,80,78,71,13,10,26,10]) { throw FTError.message("Invalid PNG logo.") }
        if uri.hasPrefix("data:image/webp"), !(data.starts(with:Data("RIFF".utf8)) && data.count>=12 && data[8..<12]==Data("WEBP".utf8)) { throw FTError.message("Invalid WebP logo.") }
        if uri.hasPrefix("data:image/svg+xml") {
            guard let svg = String(data: data, encoding: .utf8),
                  svg.range(of: #"<!DOCTYPE|<!ENTITY|<\s*(script|foreignObject|iframe|object|embed|audio|video)\b|\bon[a-z]+\s*=|@import"#, options: [.regularExpression,.caseInsensitive]) == nil,
                  svg.range(of: #"(?:href|src)\s*=\s*["'](?!#|data:image/(?:png|jpeg|webp);base64,)"#, options: [.regularExpression,.caseInsensitive]) == nil else { throw FTError.message("SVG logo contains unsupported resources.") }
            let regex = try NSRegularExpression(pattern: #"url\(\s*(['"]?)(.*?)\1\s*\)"#, options:.caseInsensitive)
            for match in regex.matches(in:svg,range:NSRange(svg.startIndex...,in:svg)) {
                if let range = Range(match.range(at:2),in:svg), !svg[range].trimmingCharacters(in:.whitespacesAndNewlines).hasPrefix("#") { throw FTError.message("SVG logo contains an external resource.") }
            }
        }
    }

    public static func encode(_ storage: [String: String]) throws -> Data {
        try validate(storage)
        let checksum = SHA256.hash(data: try canonical(storage)).map { String(format: "%02x", $0) }.joined()
        return try JSONSerialization.data(withJSONObject: ["format":"freetarget-desktop-backup", "schema":1,
            "app_version":"0.2.0-alpha.1-ios", "ui_base_version":"1.7.9", "created_at":ISO8601DateFormatter().string(from: Date()),
            "storage":storage, "checksum_sha256":checksum], options: [.prettyPrinted,.sortedKeys,.withoutEscapingSlashes])
    }

    public static func decode(_ data: Data) throws -> [String: String] {
        guard data.count <= maximumBytes,
              let doc = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let format = doc["format"] as? String, ["freetarget-desktop-backup","freetarget-browser-export"].contains(format),
              let schema = doc["schema"] as? NSNumber, CFGetTypeID(schema) != CFBooleanGetTypeID(), schema.doubleValue == 1,
              var storage = doc["storage"] as? [String: String] else { throw FTError.message("Not a supported schema-1 freETarget backup.") }
        try validate(storage)
        if let checksum = doc["checksum_sha256"] as? String {
            let actual = SHA256.hash(data: try canonical(storage)).map { String(format: "%02x", $0) }.joined()
            guard checksum == actual else { throw FTError.message("Backup integrity check failed.") }
        }
        if let logo = doc["logo"], !(logo is NSNull) {
            try validateLogo(logo)
            storage["ft-custom-logo-v1"] = String(decoding: try JSONSerialization.data(withJSONObject: logo), as: UTF8.self)
        }
        try validate(storage)
        return storage
    }

    public static func summary(_ values: [String: String]) -> [String: Any] {
        func array(_ key: String) -> [[String: Any]] { (try? JSONSerialization.jsonObject(with: Data((values[key] ?? "[]").utf8))) as? [[String: Any]] ?? [] }
        let profiles = array("ft-shooter-profiles-v1")
        return ["shooters":profiles.count, "guns":profiles.reduce(0) { total, p in total + ((p["guns"] as? [Any])?.count ?? (["make","model","caliber","nickname"].contains { !(p[$0] as? String ?? "").isEmpty } ? 1 : 0)) },
                "sessions":array("ft-session-history-v1").count, "preferences":values.count, "has_logo":values["ft-custom-logo-v1"] != nil]
    }
}
