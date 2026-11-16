import Foundation

/// Frames concatenated/fragmented target objects without splitting quoted braces.
public struct PacketFramer {
    private var bytes: [UInt8] = []
    private var depth = 0
    private var quoted = false
    private var escaped = false
    public private(set) var errors = 0
    public init() {}

    public mutating func feed(_ data: Data) -> [[String: Any]] {
        var packets: [[String: Any]] = []
        for byte in data {
            if depth == 0 {
                if byte != 123 { continue }
                bytes = []; quoted = false; escaped = false
            }
            bytes.append(byte)
            if quoted {
                if escaped { escaped = false }
                else if byte == 92 { escaped = true }
                else if byte == 34 { quoted = false }
            } else if byte == 34 { quoted = true }
            else if byte == 123 { depth += 1 }
            else if byte == 125 { depth -= 1 }
            if bytes.count > 524_288 {
                errors += 1; bytes = []; depth = 0; quoted = false; escaped = false
                continue
            }
            if depth == 0 {
                if let packet = try? JSONSerialization.jsonObject(with: Self.sanitize(bytes)) as? [String: Any] {
                    packets.append(packet)
                } else { errors += 1 }
                bytes = []
            }
        }
        return packets
    }

    /// Older Arduino output sometimes contains empty comma-separated members.
    private static func sanitize(_ input: [UInt8]) -> Data {
        var output: [UInt8] = [], quoted = false, escaped = false
        for byte in input {
            if quoted {
                output.append(byte)
                if escaped { escaped = false }
                else if byte == 92 { escaped = true }
                else if byte == 34 { quoted = false }
                continue
            }
            if byte == 34 { quoted = true; output.append(byte); continue }
            let previous = output.lastIndex(where: { ![9,10,13,32].contains($0) })
            if byte == 44, let i = previous, [44,123,91].contains(output[i]) { continue }
            if [125,93].contains(byte), let i = previous, output[i] == 44 { output.remove(at: i) }
            output.append(byte)
        }
        return Data(output)
    }
}
