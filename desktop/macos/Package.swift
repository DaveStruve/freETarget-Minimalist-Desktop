// swift-tools-version: 5.9
import PackageDescription
let package = Package(name:"freETargetAppleCore",platforms:[.macOS(.v13),.iOS(.v16)],
    products:[.library(name:"PacketCore",targets:["PacketCore"])],
    targets:[.target(name:"PacketCore",path:"ios/freETargetIOS/Core",linkerSettings:[.linkedLibrary("sqlite3")]),
             .testTarget(name:"PacketCoreTests",dependencies:["PacketCore"],path:"ios/CoreTests")])
