// After "npx cap add android|ios": app name, permission texts, notification channel, push capability. Run by the build (CI), not by hand.
const fs = require('fs'); const path = require('path'); const which = process.argv[2];
const NAME = 'NailFlow'; // the name under the icon (iPhone shows ~12 letters); the store name is "NailFlow – Salon Manager"
const edit = (f, fn) => { const s = fs.readFileSync(f, 'utf8'); const t = fn(s); if (t !== s) fs.writeFileSync(f, t); console.log('patched', f); };
if (which === 'ios') {
  // GoogleMLKit (gift card scanner) needs iOS 15.5+ – raise the minimum before CocoaPods runs
  edit('ios/App/Podfile', (s) => s.replace(/platform :ios, '[0-9.]+'/, "platform :ios, '15.5'"));
  edit('ios/App/App.xcodeproj/project.pbxproj', (s) => s.replace(/IPHONEOS_DEPLOYMENT_TARGET = [0-9.]+;/g, 'IPHONEOS_DEPLOYMENT_TARGET = 15.5;'));
  const plist = 'ios/App/App/Info.plist';
  const add = { CFBundleDisplayName: NAME, NSCameraUsageDescription: 'NailFlow uses the camera to scan gift cards and QR codes.', NSFaceIDUsageDescription: 'NailFlow uses Face ID to open the app safely.' };
  edit(plist, (s) => { for (const [k, v] of Object.entries(add)) { if (s.includes(`<key>${k}</key>`)) s = s.replace(new RegExp(`<key>${k}</key>\\s*<string>[^<]*</string>`), `<key>${k}</key>\n\t<string>${v}</string>`); else s = s.replace('<dict>', `<dict>\n\t<key>${k}</key>\n\t<string>${v}</string>`); }
    if (!s.includes('ITSAppUsesNonExemptEncryption')) s = s.replace('<dict>', '<dict>\n\t<key>ITSAppUsesNonExemptEncryption</key>\n\t<false/>');
    // (lệnh 576) nailflow://open?u=<manager link> – "📱 Open in app" on a manager page in Safari opens it in the app (native.js → /app/?mlink=, checked by the server)
    if (!s.includes('CFBundleURLSchemes')) s = s.replace('<dict>', '<dict>\n\t<key>CFBundleURLTypes</key>\n\t<array><dict><key>CFBundleURLName</key><string>com.nailflow.salonmanager</string><key>CFBundleURLSchemes</key><array><string>nailflow</string></array></dict></array>');
    if (!s.includes('UIBackgroundModes')) s = s.replace('<dict>', '<dict>\n\t<key>UIBackgroundModes</key>\n\t<array><string>remote-notification</string></array>'); return s; });
  const ent = 'ios/App/App/App.entitlements';
  fs.writeFileSync(ent, '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0"><dict><key>aps-environment</key><string>production</string></dict></plist>\n');
  edit('ios/App/App.xcodeproj/project.pbxproj', (s) => s.includes('CODE_SIGN_ENTITLEMENTS') ? s : s.replace(/(INFOPLIST_FILE = App\/Info\.plist;)/g, '$1\n\t\t\t\tCODE_SIGN_ENTITLEMENTS = App/App.entitlements;'));
  if (fs.existsSync('GoogleService-Info.plist')) fs.copyFileSync('GoogleService-Info.plist', 'ios/App/App/GoogleService-Info.plist');
  if (fs.existsSync('native/sounds/nailflow_ring.wav')) fs.copyFileSync('native/sounds/nailflow_ring.wav', 'ios/App/App/nailflow_ring.wav'); // (lệnh 550) the bell for aps.sound
  // (lệnh 556) NailFlow's 8 own sounds (aps.sound "<id>.caf") + version 1.3 (the web then asks for them: caps "snd")
  for (const f of fs.readdirSync('native/sounds').filter(f => /^nf_.*\.caf$/.test(f))) fs.copyFileSync('native/sounds/' + f, 'ios/App/App/' + f);
  edit('ios/App/App.xcodeproj/project.pbxproj', (s) => s.replace(/MARKETING_VERSION = [0-9.]+;/g, 'MARKETING_VERSION = 1.5;'));
  // Firebase (notifications): start it + hand Apple's push token to it (what @capacitor-firebase/messaging asks for)
  // only when the Firebase file is there – without it FirebaseApp.configure() would crash the app at start
  if (fs.existsSync('GoogleService-Info.plist')) edit('ios/App/App/AppDelegate.swift', (s) => s.includes('FirebaseApp.configure') ? s : s
    .replace('import Capacitor', 'import Capacitor\nimport FirebaseCore\nimport FirebaseMessaging')
    .replace(/(didFinishLaunchingWithOptions[^{]*\{)/, '$1\n        FirebaseApp.configure()')
    .replace(/\n\}\s*$/, `\n    func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {\n        Messaging.messaging().apnsToken = deviceToken\n        NotificationCenter.default.post(name: .capacitorDidRegisterForRemoteNotifications, object: deviceToken)\n    }\n    func application(_ application: UIApplication, didFailToRegisterForRemoteNotificationsWithError error: Error) {\n        NotificationCenter.default.post(name: .capacitorDidFailToRegisterForRemoteNotifications, object: error)\n    }\n}\n`));
  // (lệnh 569) "🗣 Giọng đọc": the iPhone makes its read-out sounds itself (AVSpeechSynthesizer → Library/Sounds/nfv_<id>.caf) – the NFVoice plugin
  // + the view controller that registers it (Main.storyboard); AFTER the Firebase lines above (they add to the end of AppDelegate). App 1.4.
  edit('ios/App/App/AppDelegate.swift', (s) => s.includes('NFVoicePlugin') ? s : s.replace('import Capacitor', 'import Capacitor\nimport AVFoundation\nimport UserNotifications') + fs.readFileSync('native/ios/NFVoice.swift.txt', 'utf8'));
  edit('ios/App/App/Base.lproj/Main.storyboard', (s) => s.replace('customClass="CAPBridgeViewController" customModule="Capacitor"', 'customClass="NFViewController" customModule="App" customModuleProvider="target"'));
}
if (which === 'android') {
  edit('android/app/src/main/res/values/strings.xml', (s) => s.replace(/<string name="app_name">[^<]*<\/string>/, `<string name="app_name">${NAME}</string>`).replace(/<string name="title_activity_main">[^<]*<\/string>/, `<string name="title_activity_main">${NAME}</string>`));
  edit('android/app/src/main/AndroidManifest.xml', (s) => { for (const p of ['android.permission.CAMERA', 'android.permission.VIBRATE', 'android.permission.POST_NOTIFICATIONS', 'android.permission.USE_BIOMETRIC', 'android.permission.ACCESS_NOTIFICATION_POLICY' /* (lệnh 569) YOUR TURN through Do Not Disturb */])
      if (!s.includes(p)) s = s.replace('</manifest>', `    <uses-permission android:name="${p}" />\n</manifest>`);
    if (!s.includes('default_notification_channel_id')) s = s.replace('<application', '<application').replace(/(<application[^>]*>)/, '$1\n        <meta-data android:name="com.google.firebase.messaging.default_notification_channel_id" android:value="nailflow" />');
    return s; });
  // the "nailflow" channel (sound + buzz, high importance) is made when the app starts
  const main = fs.readdirSync('android/app/src/main/java', { recursive: true }).find(f => f.endsWith('MainActivity.java'));
  // (lệnh 571/569) MainActivity is written whole (native/android/MainActivity.java): the two old edits never applied (the package name already has "nailflow",
  // the template's class is "{}" on one line) – NFVoice plugin, the "nailflow" channel, tap → the right screen (nf_url)
  if (main) fs.copyFileSync('native/android/MainActivity.java', path.join('android/app/src/main/java', main));
  if (fs.existsSync('google-services.json')) fs.copyFileSync('google-services.json', 'android/app/google-services.json');
  // (lệnh 534) KHẨN: our own messaging service (rings + buzzes until tapped – FLAG_INSISTENT, full screen when locked) instead of the plugin's;
  // tapping it opens the right screen (nf_url); the app is build 2 (the web then asks for urgent pushes)
  const pkgDir = 'android/app/src/main/java/com/nailflow/salonmanager';
  if (fs.existsSync(pkgDir)) { fs.copyFileSync('native/android/NailFlowMessagingService.java', path.join(pkgDir, 'NailFlowMessagingService.java')); fs.copyFileSync('native/android/NFVoicePlugin.java', path.join(pkgDir, 'NFVoicePlugin.java')); fs.copyFileSync('native/android/NFChat.java', path.join(pkgDir, 'NFChat.java')); fs.copyFileSync('native/android/NFStop.java', path.join(pkgDir, 'NFStop.java')); } // (lệnh 583) NFStop // (lệnh 581) NFChat: Messages-style customer texts // (lệnh 569) + the NFVoice plugin
  // (lệnh 576) nailflow://open?u=<manager link> → the app (Capacitor App plugin "appUrlOpen"; native.js sends it to /app/?mlink=)
  edit('android/app/src/main/AndroidManifest.xml', (s) => s.includes('android:scheme="nailflow"') ? s : s.replace(/(<activity[^>]*\.MainActivity"[\s\S]*?)(\n\s*<\/activity>)/, '$1\n            <intent-filter>\n                <action android:name="android.intent.action.VIEW" />\n                <category android:name="android.intent.category.DEFAULT" />\n                <category android:name="android.intent.category.BROWSABLE" />\n                <data android:scheme="nailflow" />\n            </intent-filter>$2'));
  edit('android/app/src/main/AndroidManifest.xml', (s) => { if (s.includes('NailFlowMessagingService')) return s;
    if (!s.includes('xmlns:tools')) s = s.replace('<manifest ', '<manifest xmlns:tools="http://schemas.android.com/tools" ');
    if (!s.includes('USE_FULL_SCREEN_INTENT')) s = s.replace('</manifest>', '    <uses-permission android:name="android.permission.USE_FULL_SCREEN_INTENT" />\n</manifest>');
    return s.replace('</application>', '        <service android:name="io.capawesome.capacitorjs.plugins.firebase.messaging.MessagingService" tools:node="remove" />\n        <service android:name=".NailFlowMessagingService" android:exported="false">\n            <intent-filter><action android:name="com.google.firebase.MESSAGING_EVENT" /></intent-filter>\n        </service>\n    </application>'); });
  // (lệnh 550) NailFlow's own bell for the notification channel "nailflow_ring"; build 3 (the web then may use the quiet / ring channels)
  fs.mkdirSync('android/app/src/main/res/raw', { recursive: true }); if (fs.existsSync('native/sounds/nailflow_ring.wav')) fs.copyFileSync('native/sounds/nailflow_ring.wav', 'android/app/src/main/res/raw/nailflow_ring.wav');
  // (lệnh 556) the 8 own sounds (res/raw/nf_*.ogg → one channel each, made by NailFlowMessagingService) – build 4 / 1.3
  for (const f of fs.readdirSync('native/sounds').filter(f => /^nf_.*\.ogg$/.test(f))) fs.copyFileSync('native/sounds/' + f, 'android/app/src/main/res/raw/' + f);
  // (lệnh 571) NailFlowMessagingService extends the plugin's service, which extends Firebase's FirebaseMessagingService and uses RemoteMessage –
  // the plugin adds firebase-messaging as "implementation" (not "api"), so the APP did not see it: "cannot find symbol" (RemoteMessage, getResources…).
  // The app now asks for firebase-messaging itself (same version as the plugin, 24.1.0 unless the project sets one) + androidx.core (NotificationCompat).
  edit('android/app/build.gradle', (s) => s.includes('com.google.firebase:firebase-messaging') ? s : s.replace(/(implementation project\(':capacitor-android'\))/,
    "$1\n    implementation \"com.google.firebase:firebase-messaging:${rootProject.ext.has('firebaseMessagingVersion') ? rootProject.ext.firebaseMessagingVersion : '24.1.0'}\" // (lệnh 571) NailFlowMessagingService\n    implementation \"androidx.core:core:${rootProject.ext.has('androidxCoreVersion') ? rootProject.ext.androidxCoreVersion : '1.15.0'}\" // (lệnh 571) NotificationCompat"));
  edit('android/app/build.gradle', (s) => s.replace(/versionCode \d+/, 'versionCode 8').replace(/versionName "[^"]*"/, 'versionName "1.5"') /* (lệnh 569) 1.4: voice · (lệnh 576) build 6: nailflow:// link · (lệnh 589) build 8: nailflow_silent */);
  // (lệnh 534) tap → the right screen: now in native/android/MainActivity.java (copied above)

}
