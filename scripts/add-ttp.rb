# (TTP-UAT 04/11/2026) Dejavoo Tap to Pay on iPhone (iPOSgo! Deep Linking V2): put DeepLinking.xcframework into the App target (link + embed & sign).
# The framework comes from Dejavoo's public sample (pinned commit) – downloaded by the build, not kept in this repo. Run after "npx cap add ios" + patch-native.js.
require 'xcodeproj'
fw = 'ios/App/App/DeepLinking.xcframework'
abort("#{fw} missing") unless File.directory?(fw)
p = Xcodeproj::Project.open('ios/App/App.xcodeproj')
t = p.targets.find { |x| x.name == 'App' }
g = p.main_group['App']
ref = g.files.find { |f| f.path == 'DeepLinking.xcframework' } || g.new_reference('DeepLinking.xcframework')
ref.last_known_file_type = 'wrapper.xcframework'
t.frameworks_build_phase.add_file_reference(ref, true) unless t.frameworks_build_phase.files_references.include?(ref)
emb = t.copy_files_build_phases.find { |b| b.name == 'Embed Frameworks' } || t.new_copy_files_build_phase('Embed Frameworks')
emb.symbol_dst_subfolder_spec = :frameworks
unless emb.files_references.include?(ref)
  bf = emb.add_file_reference(ref, true)
  bf.settings = { 'ATTRIBUTES' => ['CodeSignOnCopy', 'RemoveHeadersOnCopy'] }
end
p.save
puts 'DeepLinking.xcframework linked + embedded'
