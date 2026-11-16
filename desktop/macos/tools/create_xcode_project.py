"""Create a self-contained, dependency-free Xcode iOS app project."""
from pathlib import Path
import hashlib
import json
import plistlib

ROOT=Path(__file__).resolve().parents[1]
IOS=ROOT/'ios'

def ident(name):return hashlib.sha256(name.encode()).hexdigest()[:24].upper()
def quote(text):return json.dumps(str(text))

def create():
    sources=['freETargetIOSApp.swift','WebHost.swift','TargetConnection.swift','Core/PacketFramer.swift','Core/BackupCodec.swift','Core/NativeStore.swift']
    entries=[]
    def add(name,content):entries.append(ident(name)+' = { '+content+' };')
    for path in sources:
        add('file:'+path,'isa=PBXFileReference; lastKnownFileType=sourcecode.swift; path='+quote(path)+'; sourceTree="<group>";')
        add('build:'+path,'isa=PBXBuildFile; fileRef='+ident('file:'+path)+';')
    for name,kind in [('Web','folder'),('Assets.xcassets','folder.assetcatalog'),('PrivacyInfo.xcprivacy','text.xml')]:
        add('file:'+name,'isa=PBXFileReference; lastKnownFileType='+kind+'; path='+quote(name)+'; sourceTree="<group>";')
        add('build:'+name,'isa=PBXBuildFile; fileRef='+ident('file:'+name)+';')
    add('plist','isa=PBXFileReference; lastKnownFileType=text.plist.xml; path=Info.plist; sourceTree="<group>";')
    add('product','isa=PBXFileReference; explicitFileType=wrapper.application; includeInIndex=0; path=freETargetIOS.app; sourceTree=BUILT_PRODUCTS_DIR;')
    add('products','isa=PBXGroup; name=Products; children=('+ident('product')+'); sourceTree="<group>";')
    children=[ident('file:'+p) for p in sources+['Web','Assets.xcassets','PrivacyInfo.xcprivacy']]+[ident('plist')]
    add('sourcegroup','isa=PBXGroup; path=freETargetIOS; children=('+','.join(children)+'); sourceTree="<group>";')
    add('rootgroup','isa=PBXGroup; children=('+ident('sourcegroup')+','+ident('products')+'); sourceTree="<group>";')
    add('sources','isa=PBXSourcesBuildPhase; buildActionMask=2147483647; files=('+','.join(ident('build:'+s) for s in sources)+'); runOnlyForDeploymentPostprocessing=0;')
    add('resources','isa=PBXResourcesBuildPhase; buildActionMask=2147483647; files=('+','.join(ident('build:'+s) for s in ['Web','Assets.xcassets','PrivacyInfo.xcprivacy'])+'); runOnlyForDeploymentPostprocessing=0;')
    add('frameworks','isa=PBXFrameworksBuildPhase; buildActionMask=2147483647; files=(); runOnlyForDeploymentPostprocessing=0;')
    project_settings={'SDKROOT':'iphoneos','IPHONEOS_DEPLOYMENT_TARGET':'16.0','CLANG_ENABLE_MODULES':'YES','SWIFT_VERSION':'5.0','SWIFT_STRICT_CONCURRENCY':'minimal'}
    app_settings={'PRODUCT_BUNDLE_IDENTIFIER':'designs.struve.freetarget.ios.preview','PRODUCT_NAME':'$(TARGET_NAME)',
        'INFOPLIST_FILE':'freETargetIOS/Info.plist','GENERATE_INFOPLIST_FILE':'NO','CODE_SIGN_STYLE':'Automatic',
        'TARGETED_DEVICE_FAMILY':'1,2','SUPPORTED_PLATFORMS':'iphoneos iphonesimulator','ASSETCATALOG_COMPILER_APPICON_NAME':'AppIcon',
        'OTHER_LDFLAGS':'$(inherited) -lsqlite3','LD_RUNPATH_SEARCH_PATHS':'$(inherited) @executable_path/Frameworks',
        'CURRENT_PROJECT_VERSION':'1','MARKETING_VERSION':'0.2.0'}
    for scope,settings in [('project',project_settings),('app',app_settings)]:
        for config in ['Debug','Release']:
            values=dict(settings)
            if scope=='app':values['SWIFT_OPTIMIZATION_LEVEL']='-Onone' if config=='Debug' else '-O'
            add(scope+config,'isa=XCBuildConfiguration; name='+config+'; buildSettings={'+''.join(k+'='+quote(v)+';' for k,v in values.items())+'};')
        add(scope+'configs','isa=XCConfigurationList; buildConfigurations=('+ident(scope+'Debug')+','+ident(scope+'Release')+'); defaultConfigurationIsVisible=0; defaultConfigurationName=Release;')
    add('target','isa=PBXNativeTarget; name=freETargetIOS; productName=freETargetIOS; productType="com.apple.product-type.application"; productReference='+ident('product')+'; buildConfigurationList='+ident('appconfigs')+'; buildPhases=('+','.join(ident(s) for s in ['sources','frameworks','resources'])+'); buildRules=(); dependencies=();')
    add('project','isa=PBXProject; attributes={LastUpgradeCheck=1600;}; buildConfigurationList='+ident('projectconfigs')+'; compatibilityVersion="Xcode 14.0"; developmentRegion=en; knownRegions=(en,Base); mainGroup='+ident('rootgroup')+'; productRefGroup='+ident('products')+'; projectDirPath=""; projectRoot=""; targets=('+ident('target')+');')
    project=IOS/'freETargetIOS.xcodeproj';project.mkdir(exist_ok=True)
    (project/'project.pbxproj').write_text('// !$*UTF8*$!\n{ archiveVersion=1; classes={}; objectVersion=56; objects={\n'+'\n'.join(entries)+'\n}; rootObject='+ident('project')+'; }\n')
    scheme=project/'xcshareddata/xcschemes';scheme.mkdir(parents=True,exist_ok=True)
    ref='<BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="'+ident('target')+'" BuildableName="freETargetIOS.app" BlueprintName="freETargetIOS" ReferencedContainer="container:freETargetIOS.xcodeproj"/>'
    (scheme/'freETargetIOS.xcscheme').write_text('<?xml version="1.0" encoding="UTF-8"?><Scheme LastUpgradeVersion="1600" version="1.3"><BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES"><BuildActionEntries><BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES">'+ref+'</BuildActionEntry></BuildActionEntries></BuildAction><TestAction buildConfiguration="Debug"/><LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" debugServiceExtension="internal" allowLocationSimulation="YES"><BuildableProductRunnable runnableDebuggingMode="0">'+ref+'</BuildableProductRunnable></LaunchAction><ProfileAction buildConfiguration="Release"><BuildableProductRunnable runnableDebuggingMode="0">'+ref+'</BuildableProductRunnable></ProfileAction><AnalyzeAction buildConfiguration="Debug"/><ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES"/></Scheme>')
    info={'CFBundleDevelopmentRegion':'en','CFBundleDisplayName':'freETarget Minimalist','CFBundleExecutable':'$(EXECUTABLE_NAME)',
          'CFBundleIdentifier':'$(PRODUCT_BUNDLE_IDENTIFIER)','CFBundleInfoDictionaryVersion':'6.0','CFBundleName':'freETargetIOS',
          'CFBundlePackageType':'APPL','CFBundleShortVersionString':'0.2.0','CFBundleVersion':'1','LSRequiresIPhoneOS':True,
          'NSLocalNetworkUsageDescription':'Connect to your freETarget Minimalist electronic target over Wi-Fi to display and score shots.',
          'NSCameraUsageDescription':'Optionally take a photo for a custom logo using the image picker. Choosing Files does not use the camera.',
          'NSPhotoLibraryUsageDescription':'Optionally choose an image to use as a custom logo. Images are saved only in this app unless you export a backup.',
          'UILaunchScreen':{},'UIApplicationSupportsIndirectInputEvents':True,
          'UIApplicationSceneManifest':{'UIApplicationSupportsMultipleScenes':False},
          'UISupportedInterfaceOrientations':['UIInterfaceOrientationPortrait','UIInterfaceOrientationLandscapeLeft','UIInterfaceOrientationLandscapeRight'],
          'UISupportedInterfaceOrientations~ipad':['UIInterfaceOrientationPortrait','UIInterfaceOrientationPortraitUpsideDown','UIInterfaceOrientationLandscapeLeft','UIInterfaceOrientationLandscapeRight']}
    (IOS/'freETargetIOS/Info.plist').write_bytes(plistlib.dumps(info))
    privacy={'NSPrivacyTracking':False,'NSPrivacyTrackingDomains':[],'NSPrivacyCollectedDataTypes':[],
             'NSPrivacyAccessedAPITypes':[{'NSPrivacyAccessedAPIType':'NSPrivacyAccessedAPICategoryFileTimestamp','NSPrivacyAccessedAPITypeReasons':['C617.1','3B52.1']}]}
    (IOS/'freETargetIOS/PrivacyInfo.xcprivacy').write_bytes(plistlib.dumps(privacy))
    print('Xcode iOS project created:',project)

if __name__=='__main__':create()
