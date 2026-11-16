import UIKit
import WebKit
import UniformTypeIdentifiers

@MainActor private final class LocalWebView: WKWebView {
    var onAttached: (() -> Void)?
    override func didMoveToWindow() {
        super.didMoveToWindow()
        if window != nil { let callback=onAttached; onAttached=nil; callback?() }
    }
}

@MainActor final class WebHost: NSObject, WKNavigationDelegate, WKUIDelegate, WKScriptMessageHandlerWithReply, UIDocumentPickerDelegate {
    let store: NativeStore
    let target = TargetConnection()
    private(set) var webView: WKWebView!
    private var launchURL: URL!
    private var stage: (id: String, values: [String:String], revision: Int, expires: Date)?
    private var documentReply: ((Any?, String?) -> Void)?
    private var documentMode = ""
    private var exportURL: URL?
    private var backupWarning: String?

    init(store: NativeStore) throws {
        self.store = store
        super.init()
        // Imported desktop USB settings cannot select an unsupported iOS transport.
        let initial = try store.snapshot()
        if initial["ft-connection-method"] == "serial" {
            _ = try store.change(key:"ft-connection-method",value:"tcp",expected:store.revision)
        }
        do { _ = try store.backup() } catch { backupWarning = "Startup backup failed. Export a backup to Files: \(error.localizedDescription)" }
        let config = WKWebViewConfiguration()
        config.websiteDataStore = .nonPersistent()
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []
        config.userContentController.addScriptMessageHandler(self, contentWorld:.page, name:"ft")
        let localView = LocalWebView(frame:.zero,configuration:config)
        webView = localView
        webView.navigationDelegate = self; webView.uiDelegate = self
        webView.isOpaque = false; webView.backgroundColor = .systemBackground
        try prepareHTML()
        // Storage prompts must not run until the native view has a window.
        localView.onAttached = { [weak self] in
            guard let self = self else { return }
            self.webView.loadFileURL(self.launchURL, allowingReadAccessTo:self.launchURL.deletingLastPathComponent())
        }
    }

    private func prepareHTML() throws {
        guard let bundle = Bundle.main.url(forResource:"Web",withExtension:nil) else { throw FTError.message("Bundled Web assets are missing. Re-extract the complete iOS source archive.") }
        var html = try String(contentsOf:bundle.appendingPathComponent("index.html"),encoding:.utf8)
        var bootstrap = try String(contentsOf:bundle.appendingPathComponent("ios_bootstrap.js"),encoding:.utf8)
        let boot: [String: Any] = ["storage":try store.snapshot(),"revision":try store.revision]
        let data = try JSONSerialization.data(withJSONObject:boot,options:[.sortedKeys,.withoutEscapingSlashes])
        let json = String(decoding:data,as:UTF8.self).replacingOccurrences(of:"<",with:"\\u003c").replacingOccurrences(of:"\u{2028}",with:"\\u2028").replacingOccurrences(of:"\u{2029}",with:"\\u2029")
        bootstrap = bootstrap.replacingOccurrences(of:"/*__FT_IOS_BOOT__*/",with:json)
        html = html.replacingOccurrences(of:"<!--DESKTOP_BOOTSTRAP-->",with:"<script>\(bootstrap)</script>")
        let css = try String(contentsOf:bundle.appendingPathComponent("mobile.css"),encoding:.utf8)
        html = html.replacingOccurrences(of:"</head>",with:"<style>\(css)</style></head>")
        html = html.replacingOccurrences(of:"freETarget Minimalist — 0.3.10 Beta</title>",
                                         with:"freETarget Minimalist — iOS 0.2.0 Beta</title>")
        html = html.replacingOccurrences(of:"join the freETarget Wi-Fi network on this computer",
                                         with:"join the freETarget Wi-Fi network in iOS Settings")
        let cache = FileManager.default.urls(for:.cachesDirectory,in:.userDomainMask)[0].appendingPathComponent("Launch")
        try FileManager.default.createDirectory(at:cache,withIntermediateDirectories:true)
        launchURL = cache.appendingPathComponent("index.html")
        try Data(html.utf8).write(to:launchURL,options:.atomic)
    }

    private func trusted(_ frame: WKFrameInfo) -> Bool {
        frame.isMainFrame && webView.url?.standardizedFileURL == launchURL.standardizedFileURL
    }
    private func send(_ reply: (Any?,String?) -> Void, _ status: Int, _ body: [String:Any]) {
        reply(["status":status,"body":body],nil)
    }
    private func present(_ controller: UIViewController) throws {
        guard let root = webView.window?.rootViewController else { throw FTError.message("The app window is not ready.") }
        var top = root
        while let next = top.presentedViewController { top = next }
        guard !top.isBeingDismissed else { throw FTError.message("Wait for the current dialog to close.") }
        top.present(controller,animated:true)
    }

    func webView(_ webView: WKWebView, runJavaScriptTextInputPanelWithPrompt prompt: String, defaultText: String?, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (String?) -> Void) {
        guard trusted(frame), prompt == "FT_STORE_V1", let text = defaultText else { completionHandler(nil); return }
        do {
            guard text.utf8.count <= BackupCodec.maximumBytes,
                  let obj = try JSONSerialization.jsonObject(with:Data(text.utf8)) as? [String:Any],
                  let key = obj["key"] as? String, let revision = obj["expected_revision"] as? Int else { throw FTError.message("Invalid local save request.") }
            let remove = obj["remove"] as? Bool == true
            guard remove || obj["value"] is String else { throw FTError.message("Invalid local value.") }
            let next = try store.change(key:key,value:remove ? nil : obj["value"] as? String,expected:revision)
            completionHandler(String(decoding:try JSONSerialization.data(withJSONObject:["revision":next]),as:UTF8.self))
        } catch {
            let data = try? JSONSerialization.data(withJSONObject:["error":error.localizedDescription])
            completionHandler(data.map { String(decoding:$0,as:UTF8.self) })
        }
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage, replyHandler: @escaping (Any?, String?) -> Void) {
        guard trusted(message.frameInfo), let request = message.body as? [String:Any], let path = request["path"] as? String,
              path.hasPrefix("/"), !path.hasPrefix("//"), let components = URLComponents(string:path) else {
            send(replyHandler,403,["error":"Untrusted native request."]); return
        }
        let body = request["body"] as? [String:Any] ?? [:]
        do {
            switch components.path {
            case "/api/events":
                let after = components.queryItems?.first(where:{$0.name=="after"})?.value.flatMap(Int.init) ?? 0
                send(replyHandler,200,target.poll(after:max(0,after)))
            case "/api/connect": try target.connect(body); send(replyHandler,200,["ok":true])
            case "/api/disconnect": target.disconnect(); send(replyHandler,200,["ok":true])
            case "/api/serial-ports": send(replyHandler,200,["available":false,"ports":[],"error":"USB is unavailable in this iOS preview."])
            case "/api/clear-diagnostics": send(replyHandler,200,target.clearDiagnostics())
            case "/desktop/info":
                send(replyHandler,200,["app_version":"0.2.0-beta.1-ios","ui_base_version":"1.7.9","data_folder":"On this device — use Export Backup to save a copy in Files.","revision":try store.revision,"summary":BackupCodec.summary(try store.snapshot()),"backup_warning":backupWarning ?? ""])
            case "/desktop/export-backup": try exportBackup(replyHandler)
            case "/desktop/preview-backup":
                idle { [weak self] error in
                    guard let self = self else { return }
                    if let error = error { self.send(replyHandler,400,["error":error]); return }
                    do { try self.importBackup(replyHandler) } catch { self.send(replyHandler,400,["error":error.localizedDescription]) }
                }
            case "/desktop/restore-backup":
                idle { [weak self] error in
                    guard let self = self else { return }
                    if let error = error { self.send(replyHandler,400,["error":error]); return }
                    do {
                        guard let stage = self.stage, stage.id == body["import_id"] as? String, stage.expires > Date(),
                              stage.revision == body["expected_revision"] as? Int, body["confirmed"] as? Bool == true else { throw FTError.message("The restore preview expired or was not confirmed.") }
                        let revision = try self.store.restore(stage.values,expected:stage.revision)
                        self.stage = nil
                        try self.prepareHTML() // Reload must see the restored snapshot, not the old injected cache.
                        self.send(replyHandler,200,["revision":revision,"summary":BackupCodec.summary(stage.values)])
                    } catch { self.send(replyHandler,400,["error":error.localizedDescription]) }
                }
            default:
                send(replyHandler,501,["error":"This iOS preview supports Wi-Fi scoring, local records and Files backups. USB, target setting edits and the desktop browser exporter are not implemented."])
            }
        } catch { send(replyHandler,400,["error":error.localizedDescription]) }
    }

    private func idle(_ completion: @escaping (String?) -> Void) {
        guard !target.connected && !target.connecting else { completion("Disconnect the target before restoring data."); return }
        webView.evaluateJavaScript("window.FTDesktopSessionState?.()") { [weak self] value,error in
            guard let self = self, !self.target.connected, !self.target.connecting else { completion("Disconnect the target before restoring data."); return }
            guard error == nil, let state = value as? [String:Any], state["active"] as? Bool != true, state["unsaved"] as? Bool != true else {
                completion("Finish and log or discard the current session before restoring data."); return
            }
            completion(nil)
        }
    }
    private func exportBackup(_ reply: @escaping (Any?,String?) -> Void) throws {
        guard documentReply == nil else { throw FTError.message("Another file dialog is open.") }
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("freETarget-backup-\(UUID().uuidString).json")
        try BackupCodec.encode(store.snapshot()).write(to:url,options:.atomic)
        let picker = UIDocumentPickerViewController(forExporting:[url],asCopy:true)
        picker.delegate = self; documentMode = "export"; exportURL = url; documentReply = reply
        do { try present(picker) } catch { finishDocument(status:400,body:["error":error.localizedDescription]) }
    }
    private func importBackup(_ reply: @escaping (Any?,String?) -> Void) throws {
        guard documentReply == nil else { throw FTError.message("Another file dialog is open.") }
        let picker = UIDocumentPickerViewController(forOpeningContentTypes:[.json],asCopy:false)
        picker.allowsMultipleSelection = false; picker.delegate = self
        documentMode = "import"; documentReply = reply
        do { try present(picker) } catch { finishDocument(status:400,body:["error":error.localizedDescription]) }
    }
    func documentPickerWasCancelled(_ controller: UIDocumentPickerViewController) { finishDocument(status:200,body:["cancelled":true]) }
    func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
        do {
            guard let url = urls.first else { throw FTError.message("No file was selected.") }
            if documentMode == "export" { finishDocument(status:200,body:["saved":true,"filename":url.lastPathComponent]); return }
            let access = url.startAccessingSecurityScopedResource(); defer { if access { url.stopAccessingSecurityScopedResource() } }
            let size = try url.resourceValues(forKeys:[.fileSizeKey]).fileSize ?? BackupCodec.maximumBytes + 1
            guard size <= BackupCodec.maximumBytes else { throw FTError.message("Backup exceeds 128 MB.") }
            var values = try BackupCodec.decode(Data(contentsOf:url))
            // Connection preferences are platform-specific; preserve history and profile values.
            if values["ft-connection-method"] == "serial" { values["ft-connection-method"] = "tcp" }
            let id = UUID().uuidString, revision = try store.revision
            stage = (id,values,revision,Date().addingTimeInterval(600))
            finishDocument(status:200,body:["import_id":id,"filename":url.lastPathComponent,"expected_revision":revision,
                "incoming":BackupCodec.summary(values),"current":BackupCodec.summary(try store.snapshot())])
        } catch { finishDocument(status:400,body:["error":error.localizedDescription]) }
    }
    private func finishDocument(status: Int, body: [String:Any]) {
        let reply = documentReply; documentReply = nil; documentMode = ""
        if let url = exportURL { try? FileManager.default.removeItem(at:url); exportURL = nil }
        if let reply = reply { send(reply,status,body) }
    }
    func suspend() {
        webView.evaluateJavaScript("window.FTDesktopPrepareClose?.();")
        target.disconnect(reason:"App left the foreground. Reconnect and restart any interrupted series.")
        do { _ = try store.backup() } catch { backupWarning = error.localizedDescription }
    }
    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        target.disconnect(reason:"The scoring view stopped. Reconnect after reloading.")
        let alert=UIAlertController(title:"Reload scoring view?",message:"iOS stopped the scoring view. Unlogged shots may have been lost. Committed profiles and History remain saved.",preferredStyle:.alert)
        alert.addAction(UIAlertAction(title:"Reload",style:.default) { [weak self] _ in
            guard let self=self else { return }
            do {
                try self.prepareHTML()
                self.webView.loadFileURL(self.launchURL,allowingReadAccessTo:self.launchURL.deletingLastPathComponent())
            } catch { self.backupWarning=error.localizedDescription }
        })
        try? present(alert)
    }
    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else { decisionHandler(.cancel); return }
        if url.standardizedFileURL == launchURL.standardizedFileURL { decisionHandler(.allow); return }
        if navigationAction.navigationType == .linkActivated, ["https","http"].contains(url.scheme ?? "") { UIApplication.shared.open(url) }
        decisionHandler(.cancel)
    }
    func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
        guard trusted(frame) else { completionHandler(); return }
        let alert = UIAlertController(title:"freETarget",message:message,preferredStyle:.alert)
        alert.addAction(UIAlertAction(title:"OK",style:.default) { _ in completionHandler() })
        do { try present(alert) } catch { completionHandler() }
    }
    func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (Bool) -> Void) {
        guard trusted(frame) else { completionHandler(false); return }
        let alert = UIAlertController(title:"freETarget",message:message,preferredStyle:.alert)
        alert.addAction(UIAlertAction(title:"Cancel",style:.cancel) { _ in completionHandler(false) })
        alert.addAction(UIAlertAction(title:"Continue",style:.default) { _ in completionHandler(true) })
        do { try present(alert) } catch { completionHandler(false) }
    }
}
