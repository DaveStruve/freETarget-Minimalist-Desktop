import SwiftUI
import WebKit

@MainActor final class AppModel: ObservableObject {
    let host: WebHost?
    let failure: String?
    init() {
        do {
            let folder = FileManager.default.urls(for:.applicationSupportDirectory,in:.userDomainMask)[0].appendingPathComponent("freETarget")
            host = try WebHost(store:NativeStore(directory:folder)); failure = nil
        } catch { host = nil; failure = error.localizedDescription }
    }
}
struct ScoringWebView: UIViewRepresentable {
    let host: WebHost
    func makeUIView(context: Context) -> WKWebView { host.webView }
    func updateUIView(_ uiView: WKWebView, context: Context) {}
}
@main struct FreETargetIOSApp: App {
    @StateObject private var model = AppModel()
    @Environment(\.scenePhase) private var scenePhase
    var body: some Scene {
        WindowGroup {
            Group {
                if let host = model.host { ScoringWebView(host:host) }
                else {
                    VStack(spacing:16) {
                        Text("freETarget could not start").font(.headline)
                        Text(model.failure ?? "Unknown error")
                        Text("Existing saved data was not reset.").font(.footnote)
                    }.padding()
                }
            }.onChange(of:scenePhase) { phase in
                if phase == .background { model.host?.suspend() }
            }
        }
    }
}
