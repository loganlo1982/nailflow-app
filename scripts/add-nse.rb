# (lệnh 581) Adds the Notification Service Extension "NailFlowNSE" (com.nailflow.salonmanager.NSE) to the iOS app + Communication Notifications.
# Run by Codemagic ONLY when NF_NSE=1 (Apple Developer: App ID com.nailflow.salonmanager.NSE + an App Store profile for it, and the
# "Communication Notifications" capability on com.nailflow.salonmanager – see KET-QUA 581). Without them the iOS build would fail, so it is off by default.
require 'xcodeproj'
require 'fileutils'
proj_path = 'ios/App/App.xcodeproj'
p = Xcodeproj::Project.open(proj_path)
app = p.targets.find { |t| t.name == 'App' }
exit 0 if p.targets.any? { |t| t.name == 'NailFlowNSE' }
FileUtils.mkdir_p('ios/App/NailFlowNSE')
FileUtils.cp('native/ios/NailFlowNSE/NotificationService.swift', 'ios/App/NailFlowNSE/NotificationService.swift')
FileUtils.cp('native/ios/NailFlowNSE/Info.plist', 'ios/App/NailFlowNSE/Info.plist')
nse = p.new_target(:app_extension, 'NailFlowNSE', :ios, '15.5')
grp = p.main_group.new_group('NailFlowNSE', 'NailFlowNSE')
nse.add_file_references([grp.new_reference('NotificationService.swift')])
grp.new_reference('Info.plist')
team = app.build_configurations.first.build_settings['DEVELOPMENT_TEAM']
mv = app.build_configurations.first.build_settings['MARKETING_VERSION'] || '1.5'
nse.build_configurations.each do |c|
  s = c.build_settings
  s['INFOPLIST_FILE'] = 'NailFlowNSE/Info.plist'
  s['PRODUCT_BUNDLE_IDENTIFIER'] = 'com.nailflow.salonmanager.NSE'
  s['PRODUCT_NAME'] = '$(TARGET_NAME)'
  s['SWIFT_VERSION'] = '5.0'
  s['IPHONEOS_DEPLOYMENT_TARGET'] = '15.5'
  s['TARGETED_DEVICE_FAMILY'] = '1,2'
  s['MARKETING_VERSION'] = mv
  s['CURRENT_PROJECT_VERSION'] = '1'
  s['SKIP_INSTALL'] = 'YES'
  s['LD_RUNPATH_SEARCH_PATHS'] = ['$(inherited)', '@executable_path/Frameworks', '@executable_path/../../Frameworks']
  s['DEVELOPMENT_TEAM'] = team if team
end
nse.add_system_framework('Intents')
app.add_dependency(nse)
embed = app.copy_files_build_phases.find { |ph| ph.name == 'Embed App Extensions' } || app.new_copy_files_build_phase('Embed App Extensions')
embed.symbol_dst_subfolder_spec = :plug_ins
bf = embed.add_file_reference(nse.product_reference, true)
bf.settings = { 'ATTRIBUTES' => ['RemoveHeadersOnCopy'] }
p.save
# the app: Communication Notifications (entitlement) + it may send INSendMessageIntent
ent = 'ios/App/App/App.entitlements'
e = File.read(ent)
unless e.include?('usernotifications.communication')
  e = e.sub('<dict>', '<dict><key>com.apple.developer.usernotifications.communication</key><true/>')
  File.write(ent, e)
end
pl = 'ios/App/App/Info.plist'
x = File.read(pl)
unless x.include?('NSUserActivityTypes')
  x = x.sub('<dict>', "<dict>\n\t<key>NSUserActivityTypes</key>\n\t<array><string>INSendMessageIntent</string></array>")
  File.write(pl, x)
end
puts 'added NailFlowNSE'
