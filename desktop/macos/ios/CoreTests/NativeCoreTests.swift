import XCTest
import CryptoKit
@testable import PacketCore

final class NativeCoreTests: XCTestCase {
    func testFragmentedConcatenatedPacketsAndQuotedBraces() {
        var framer=PacketFramer(), packets:[[String:Any]]=[]
        let data=Data(#"noise{"shot":1,"x":-14.35,"y":-5.54,"V_REF":1.7, ,"name":"a,,{b}"}{"shot":2,"miss":1}"#.utf8)
        for byte in data { packets += framer.feed(Data([byte])) }
        XCTAssertEqual(packets.count,2)
        XCTAssertEqual(packets[0]["name"] as? String,"a,,{b}")
        XCTAssertEqual(packets[0]["x"] as? Double,-14.35)
        XCTAssertEqual(framer.errors,0)
    }
    func testMalformedAndNonfiniteObjectsAreRejected() {
        var framer=PacketFramer()
        let packets=framer.feed(Data(#"{broken}{"shot":1,"x":NaN,"y":0}{"shot":2,"x":1,"y":2}"#.utf8))
        XCTAssertEqual(packets.count,1);XCTAssertEqual(framer.errors,2)
    }
    func testDesktopCanonicalChecksumVector() throws {
        let values = ["ft-Z": "quotes \" \\ / line\n\t\u{0008}\u{000C}\r\u{0000}", "ft-a": "測試 \u{2028} café </script>"]
        let hex = SHA256.hash(data: try BackupCodec.canonical(values)).map { String(format:"%02x", $0) }.joined()
        XCTAssertEqual(hex, "69f375d047fec93e8143aa26133e0da7338a45f0e16db8a689aee1c1934c3696")
    }
    func testBackupRoundTripAndChecksumFailure() throws {
        let values=["ft-theme":"dark","ft-text":"測試 </script> / quote \" value"]
        let bytes=try BackupCodec.encode(values)
        XCTAssertEqual(try BackupCodec.decode(bytes),values)
        var doc=try XCTUnwrap(JSONSerialization.jsonObject(with:bytes) as? [String:Any])
        doc["storage"]=["ft-theme":"tampered"]
        XCTAssertThrowsError(try BackupCodec.decode(JSONSerialization.data(withJSONObject:doc)))
    }
    func testStorePersistenceRevisionAndDelete() throws {
        let directory=FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at:directory) }
        do {
            let store=try NativeStore(directory:directory)
            XCTAssertEqual(try store.change(key:"ft-theme",value:"dark",expected:0),1)
            XCTAssertThrowsError(try store.change(key:"ft-theme",value:"light",expected:0))
            XCTAssertEqual(try store.change(key:"ft-session-history-v1",value:"[]",expected:1),2)
            XCTAssertEqual(try store.change(key:"ft-session-history-v1",value:nil,expected:2),3)
            XCTAssertEqual(try store.change(key:"ft-text",value:"before\u{0000}after",expected:3),4)
        }
        let reopened=try NativeStore(directory:directory)
        XCTAssertEqual(try reopened.snapshot(),["ft-theme":"dark","ft-text":"before\u{0000}after"])
    }
    func testRestoreConfirmationRevisionAndBackup() throws {
        let directory=FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at:directory) }
        let store=try NativeStore(directory:directory)
        _=try store.change(key:"ft-theme",value:"dark",expected:0)
        XCTAssertThrowsError(try store.restore(["ft-theme":"light"],expected:0))
        _=try store.restore(["ft-theme":"light"],expected:1)
        XCTAssertEqual(try store.snapshot(),["ft-theme":"light"])
        let copies=try FileManager.default.contentsOfDirectory(at:directory.appendingPathComponent("backups"),includingPropertiesForKeys:nil)
        XCTAssertEqual(copies.count,1)
        XCTAssertEqual(try BackupCodec.decode(Data(contentsOf:copies[0])),["ft-theme":"dark"])
    }
}
