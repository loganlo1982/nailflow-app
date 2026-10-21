package com.nailflow.salonmanager;

// (lệnh 569) "NFVoice" for the web page inside the app (assets/native.js):
//  generate({items}) → Android speaks live (TextToSpeech in NailFlowMessagingService), so nothing to make: { done: [] }
//  have()            → { ids: [] }
//  muted()           → { muted: true } when the phone is on silent / vibrate (the page shows the yellow warning), false otherwise
//  dnd()             → opens Android's "Do Not Disturb access" screen for NailFlow (Me → 📖), so YOUR TURN can ring through Do Not Disturb
import android.content.Context;
import android.content.Intent;
import android.media.AudioManager;
import android.provider.Settings;
import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "NFVoice")
public class NFVoicePlugin extends Plugin {
    @PluginMethod
    public void generate(PluginCall call) { JSObject r = new JSObject(); r.put("done", new JSArray()); call.resolve(r); }

    @PluginMethod
    public void have(PluginCall call) { JSObject r = new JSObject(); r.put("ids", new JSArray()); call.resolve(r); }

    @PluginMethod
    public void muted(PluginCall call) {
        JSObject r = new JSObject();
        try { AudioManager am = (AudioManager) getContext().getSystemService(Context.AUDIO_SERVICE);
            r.put("muted", am != null && am.getRingerMode() != AudioManager.RINGER_MODE_NORMAL);
        } catch (Exception e) { r.put("muted", JSObject.NULL); }
        call.resolve(r);
    }

    @PluginMethod
    public void dnd(PluginCall call) {
        try { Intent i = new Intent(Settings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS); i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK); getContext().startActivity(i); } catch (Exception e) {}
        call.resolve();
    }
}
