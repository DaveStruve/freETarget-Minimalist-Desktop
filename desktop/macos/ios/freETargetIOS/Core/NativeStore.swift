import Foundation
import SQLite3

/// One owner on the web coordinator's main thread; commits precede UI acknowledgements.
public final class NativeStore {
    private var db: OpaquePointer?
    public let directory: URL
    private let transient = unsafeBitCast(-1, to: sqlite3_destructor_type.self)
    public init(directory: URL) throws {
        self.directory = directory
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        guard sqlite3_open_v2(directory.appendingPathComponent("freetarget.sqlite3").path, &db,
                              SQLITE_OPEN_CREATE | SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX, nil) == SQLITE_OK else { throw FTError.message("Could not open local data.") }
        do {
            try exec("PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=10000;")
            try exec("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL); CREATE TABLE IF NOT EXISTS kv(key TEXT PRIMARY KEY,value TEXT NOT NULL,updated_at TEXT NOT NULL);")
            let check = try scalar("PRAGMA quick_check")
            guard check == "ok" else { throw FTError.message("Database integrity check failed. Data was not reset.") }
            if let schema = try scalar("SELECT value FROM meta WHERE key='schema_version'"), schema != "1" { throw FTError.message("Unsupported database version. Data was not reset.") }
            try exec("INSERT OR IGNORE INTO meta VALUES('schema_version','1'); INSERT OR IGNORE INTO meta VALUES('revision','0');")
            try BackupCodec.validate(snapshot())
        } catch { sqlite3_close(db); db = nil; throw error }
    }
    deinit { sqlite3_close(db) }
    private func exec(_ sql: String) throws {
        if sqlite3_exec(db, sql, nil, nil, nil) != SQLITE_OK { throw FTError.message("Local database write failed: \(String(cString: sqlite3_errmsg(db)))") }
    }
    private func scalar(_ sql: String) throws -> String? {
        var statement: OpaquePointer?
        guard sqlite3_prepare_v2(db, sql, -1, &statement, nil) == SQLITE_OK else { throw FTError.message("Local database query failed.") }
        defer { sqlite3_finalize(statement) }
        let result = sqlite3_step(statement)
        if result == SQLITE_DONE { return nil }
        guard result == SQLITE_ROW, let text = sqlite3_column_text(statement, 0) else { throw FTError.message("Could not read local data.") }
        return String(cString: text)
    }
    public var revision: Int {
        get throws {
            guard let text=try scalar("SELECT value FROM meta WHERE key='revision'"), let value=Int(text), value>=0, value<Int.max else { throw FTError.message("Invalid database revision. Data was not reset.") }
            return value
        }
    }
    public func snapshot() throws -> [String: String] {
        var statement: OpaquePointer?
        guard sqlite3_prepare_v2(db,"SELECT key,value FROM kv",-1,&statement,nil) == SQLITE_OK else { throw FTError.message("Could not read local records.") }
        defer { sqlite3_finalize(statement) }
        var values: [String: String] = [:]
        while true {
            let step = sqlite3_step(statement)
            if step == SQLITE_DONE { break }
            guard step == SQLITE_ROW, let key = sqlite3_column_text(statement,0), let value = sqlite3_column_text(statement,1) else { throw FTError.message("Could not read local records.") }
            let count=Int(sqlite3_column_bytes(statement,1))
            values[String(cString:key)] = String(decoding:UnsafeBufferPointer(start:value,count:count),as:UTF8.self)
        }
        return values
    }
    private func put(_ key: String, _ value: String?) throws {
        var statement: OpaquePointer?
        let sql = value == nil ? "DELETE FROM kv WHERE key=?" : "INSERT INTO kv VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at"
        guard sqlite3_prepare_v2(db,sql,-1,&statement,nil) == SQLITE_OK else { throw FTError.message("Could not prepare local save.") }
        defer { sqlite3_finalize(statement) }
        sqlite3_bind_text(statement,1,key,-1,transient)
        if let value = value {
            sqlite3_bind_text(statement,2,value,Int32(value.utf8.count),transient)
            sqlite3_bind_text(statement,3,ISO8601DateFormatter().string(from: Date()),-1,transient)
        }
        guard sqlite3_step(statement) == SQLITE_DONE else { throw FTError.message("Local save failed. Keep the app open and export a backup.") }
    }
    public func change(key: String, value: String?, expected: Int) throws -> Int {
        if let value = value { try BackupCodec.validate([key:value]) }
        else if key.range(of: #"^ft-[A-Za-z0-9][A-Za-z0-9_.:-]{0,126}$"#, options: .regularExpression) == nil { throw FTError.message("Invalid data key.") }
        try exec("BEGIN IMMEDIATE")
        do {
            let current = try revision
            guard current == expected else { throw FTError.message("Data changed. Reload before saving.") }
            let before = try snapshot()
            if before[key] == value { try exec("COMMIT"); return current }
            try put(key,value)
            try exec("UPDATE meta SET value='\(current+1)' WHERE key='revision'; COMMIT;")
            return current+1
        } catch { try? exec("ROLLBACK"); throw error }
    }
    @discardableResult public func backup() throws -> URL? {
        let values = try snapshot()
        if values.isEmpty { return nil }
        let folder = directory.appendingPathComponent("backups")
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        let url = folder.appendingPathComponent("auto-\(UUID().uuidString).json")
        try BackupCodec.encode(values).write(to:url,options:.atomic)
        let copies = try FileManager.default.contentsOfDirectory(at:folder,includingPropertiesForKeys:[.contentModificationDateKey])
            .filter { $0.lastPathComponent.hasPrefix("auto-") && $0.pathExtension == "json" }
            .sorted { ((try? $0.resourceValues(forKeys:[.contentModificationDateKey]).contentModificationDate) ?? .distantPast) > ((try? $1.resourceValues(forKeys:[.contentModificationDateKey]).contentModificationDate) ?? .distantPast) }
        for old in copies.dropFirst(30) { try? FileManager.default.removeItem(at:old) }
        return url
    }
    public func restore(_ values: [String: String], expected: Int) throws -> Int {
        try BackupCodec.validate(values)
        try exec("BEGIN IMMEDIATE")
        do {
            guard try revision == expected else { throw FTError.message("Data changed after preview. Preview again.") }
            _ = try backup()
            try exec("DELETE FROM kv")
            for (key,value) in values { try put(key,value) }
            try exec("UPDATE meta SET value='\(expected+1)' WHERE key='revision'; COMMIT;")
            return expected+1
        } catch { try? exec("ROLLBACK"); throw error }
    }
}
