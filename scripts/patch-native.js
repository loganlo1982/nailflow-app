// After "npx cap add android|ios": app name, permission texts, notification channel, push capability. Run by the build (CI), not by hand.
const fs = require('fs'); const path = require('path'); const which = process.argv[2];
const NAME = 'NailFlow'; // the name under the icon (iPhone shows ~12 letters); the store name is "NailFlow – Salon Manager"
const edit = (f, fn) => { const s = fs.readFileSync(f, 'utf8'); const t = fn(s); if (t !== s) fs.writeFileSync(f, t); console.log('patched', f); };
if (which === 'ios') {
  const plist = 'ios/App/App/Info.plist';
  const add = { CFBundleDisplayName: NAME, NSCameraUsageDescription: 'NailFlow uses the camera to scan gift cards and QR codes.', NSFaceIDUsageDescription: 'NailFlow uses Face ID to open the app safely.' };
  edit(plist, (s) => { for (const [k, v] of Object.entries(add)) { if (s.includes(`<key>${k}</key>`)) s = s.replace(new RegExp(`<key>${k}</key>\\s*<string>[^<]*</string>`), `<key>${k}</key>\n\t<string>${v}</string>`); else s = s.replace('<dict>', `<dict>\n\t<key>${k}</key>\n\t<string>${v}</string>`); }
    if (!s.includes('UIBackgroundModes')) s = s.replace('<dict>', '<dict>\n\t<key>UIBackgroundModes</key>\n\t<array><string>remote-notification</string></array>'); return s; });
  const ent = 'ios/App/App/App.entitlements';
  fs.writeFileSync(ent, '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0"><dict><key>aps-environment</key><string>production</string></dict></plist>\n');
  edit('ios/App/App.xcodeproj/project.pbxproj', (s) => s.includes('CODE_SIGN_ENTITLEMENTS') ? s : s.replace(/(INFOPLIST_FILE = App\/Info\.plist;)/g, '$1\n\t\t\t\tCODE_SIGN_ENTITLEMENTS = App/App.entitlements;'));
  if (fs.existsSync('GoogleService-Info.plist')) fs.copyFileSync('GoogleService-Info.plist', 'ios/App/App/GoogleService-Info.plist');
  // Firebase (notifications): start it + hand Apple's push token to it (what @capacitor-firebase/messaging asks for)
  edit('ios/App/App/AppDelegate.swift', (s) => s.includes('FirebaseApp.configure') ? s : s
    .replace('import Capacitor', 'import Capacitor\nimport FirebaseCore\nimport FirebaseMessaging')
    .replace(/(didFinishLaunchingWithOptions[^{]*\{)/, '$1\n        FirebaseApp.configure()')
    .replace(/\n\}\s*$/, `\n    func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {\n        Messaging.messaging().apnsToken = deviceToken\n        NotificationCenter.default.post(name: .capacitorDidRegisterForRemoteNotifications, object: deviceToken)\n    }\n    func application(_ application: UIApplication, didFailToRegisterForRemoteNotificationsWithError error: Error) {\n        NotificationCenter.default.post(name: .capacitorDidFailToRegisterForRemoteNotifications, object: error)\n    }\n}\n`));
}
if (which === 'android') {
  edit('android/app/src/main/res/values/strings.xml', (s) => s.replace(/<string name="app_name">[^<]*<\/string>/, `<string name="app_name">${NAME}</string>`).replace(/<string name="title_activity_main">[^<]*<\/string>/, `<string name="title_activity_main">${NAME}</string>`));
  edit('android/app/src/main/AndroidManifest.xml', (s) => { for (const p of ['android.permission.CAMERA', 'android.permission.VIBRATE', 'android.permission.POST_NOTIFICATIONS', 'android.permission.USE_BIOMETRIC'])
      if (!s.includes(p)) s = s.replace('</manifest>', `    <uses-permission android:name="${p}" />\n</manifest>`);
    if (!s.includes('default_notification_channel_id')) s = s.replace('<application', '<application').replace(/(<application[^>]*>)/, '$1\n        <meta-data android:name="com.google.firebase.messaging.default_notification_channel_id" android:value="nailflow" />');
    return s; });
  // the "nailflow" channel (sound + buzz, high importance) is made when the app starts
  const main = fs.readdirSync('android/app/src/main/java', { recursive: true }).find(f => f.endsWith('MainActivity.java'));
  if (main) edit(path.join('android/app/src/main/java', main), (s) => s.includes('nailflow') ? s : s
    .replace('import com.getcapacitor.BridgeActivity;', 'import com.getcapacitor.BridgeActivity;\nimport android.os.Bundle;\nimport android.app.NotificationChannel;\nimport android.app.NotificationManager;\nimport android.os.Build;')
    .replace(/public class MainActivity extends BridgeActivity \{\s*\}/, `public class MainActivity extends BridgeActivity {\n    @Override\n    public void onCreate(Bundle savedInstanceState) {\n        super.onCreate(savedInstanceState);\n        if (Build.VERSION.SDK_INT >= 26) {\n            NotificationChannel ch = new NotificationChannel("nailflow", "NailFlow", NotificationManager.IMPORTANCE_HIGH);\n            ch.enableVibration(true);\n            getSystemService(NotificationManager.class).createNotificationChannel(ch);\n        }\n    }\n}`));
  if (fs.existsSync('google-services.json')) fs.copyFileSync('google-services.json', 'android/app/google-services.json');
}
