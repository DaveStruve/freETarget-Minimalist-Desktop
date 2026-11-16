import Foundation
import Network
import UIKit

/// All state and callbacks are owned by the main queue, just like the WebKit UI.
@MainActor final class TargetConnection {
    private var connection: NWConnection?
    private var generation = UUID()
    private var framer = PacketFramer()
    private var events: [[String: Any]] = []
    private var nextID = 1
    private var epoch = 0
    private var bytesReceived = 0
    private var packetsReceived = 0
    private var parseErrorsCleared = 0
    private var config: [String: Any] = [:]
    private var successfulConfig: [String: Any]?
    private(set) var connected = false
    private(set) var connecting = false
    private var message = "Disconnected — iOS Wi-Fi preview"

    func connect(_ config: [String: Any]) throws {
        guard (config["method"] as? String ?? "tcp") == "tcp" else { throw FTError.message("This iOS preview supports Wi-Fi/TCP only. USB is not implemented.") }
        guard let host = config["host"] as? String, !host.isEmpty, host.count <= 253,
              host.rangeOfCharacter(from: .whitespacesAndNewlines) == nil,
              !host.contains("/"), !host.contains("\\"),
              let port = config["port"] as? Int, (1...65535).contains(port),
              let endpoint = NWEndpoint.Port(rawValue: UInt16(port)) else { throw FTError.message("Enter your target IP/hostname and TCP port.") }
        disconnect()
        self.config = config
        framer = PacketFramer()
        parseErrorsCleared = 0
        let id = UUID(); generation = id
        connecting = true; message = "Connecting to Minimalist target…"
        let parameters = NWParameters.tcp
        parameters.requiredInterfaceType = .wifi
        let socket = NWConnection(host: NWEndpoint.Host(host), port: endpoint, using: parameters)
        connection = socket
        socket.stateUpdateHandler = { [weak self, weak socket] state in
            DispatchQueue.main.async {
            guard let self = self, self.generation == id else { return }
            switch state {
            case .ready:
                self.connected = true; self.connecting = false; self.epoch += 1
                self.message = "Wi-Fi/TCP connected"
                self.successfulConfig = self.config
                UIApplication.shared.isIdleTimerDisabled = true
                self.append(["type":"status","message":self.message])
                if let socket = socket { self.receive(socket,id:id) }
            case .waiting(let error): self.message = "Waiting for local network access: \(error.localizedDescription)"
            case .failed(let error): self.disconnect(reason:"Connection failed: \(error.localizedDescription)")
            default: break
            }
            }
        }
        socket.start(queue: .main)
        DispatchQueue.main.asyncAfter(deadline:.now()+20) { [weak self] in
            guard let self = self, self.generation == id, self.connecting else { return }
            self.disconnect(reason:"Connection timed out. Check Local Network permission, target address and Wi-Fi.")
        }
    }
    func disconnect(reason: String = "Disconnected") {
        generation = UUID(); connection?.stateUpdateHandler = nil; connection?.cancel(); connection = nil
        connected = false; connecting = false; message = reason
        UIApplication.shared.isIdleTimerDisabled = false
    }
    private func receive(_ socket: NWConnection, id: UUID) {
        socket.receive(minimumIncompleteLength:1,maximumLength:16384) { [weak self] data, _, complete, error in
            DispatchQueue.main.async {
            guard let self = self, self.generation == id else { return }
            if let data = data, !data.isEmpty {
                self.bytesReceived += data.count
                for packet in self.framer.feed(data) { self.consume(packet) }
            }
            if let error = error { self.disconnect(reason:"Target connection lost: \(error.localizedDescription)"); return }
            if complete { self.disconnect(reason:"Target closed the connection. Reconnect when ready."); return }
            if self.connected { self.receive(socket,id:id) }
            }
        }
    }
    private func append(_ event: [String: Any]) {
        if events.count >= 10000 {
            disconnect(reason:"Shot event buffer is full. Some reports may be missing; stop and inspect the result.")
            return
        }
        var item = event; item["id"] = nextID; nextID += 1; events.append(item)
    }
    private func consume(_ packet: [String: Any]) {
        packetsReceived += 1
        func number(_ value: Any?) -> Double? {
            if let n = value as? NSNumber { return n.doubleValue }
            if let s = value as? String { return Double(s) }
            return nil
        }
        guard let count = number(packet["shot"]), count.isFinite, count >= 0, count < Double(Int.max) else {
            append(["type":"message","data":packet]); return
        }
        let miss = (packet["miss"] as? NSNumber)?.intValue == 1 || packet["miss"] as? String == "1"
        let x = number(packet["x"]) ?? (miss ? 0 : .nan)
        let y = number(packet["y"]) ?? (miss ? 0 : .nan)
        guard x.isFinite, y.isFinite else { append(["type":"message","data":packet]); return }
        append(["type":"shot","count":Int(count),"x":x,"y":y,"miss":miss,"transport":"tcp","raw":packet])
    }
    func poll(after: Int) -> [String: Any] {
        // Discard only events already acknowledged by the UI's shot cursor.
        events.removeAll { ($0["id"] as? Int ?? 0) <= after }
        return ["connected":connected,"connecting":connecting,"message":message,"method":"tcp",
                "events":events,"latest":nextID-1,"connection_epoch":epoch,"bytes_received":bytesReceived,
                "raw_packets":packetsReceived,"parse_errors":max(0,framer.errors-parseErrorsCleared),"successful_config":successfulConfig.map { $0 as Any } ?? NSNull()]
    }
    func clearDiagnostics() -> [String: Any] {
        bytesReceived = 0; packetsReceived = 0
        parseErrorsCleared = framer.errors
        return ["latest":nextID-1]
    }
}
