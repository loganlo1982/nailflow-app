package com.nailflow.salonmanager;

// (lệnh 571/569) The whole MainActivity is written by scripts/patch-native.js (before, two small edits never applied: the template's
// package name already contains "nailflow" and its class is "{}" on one line). It: registers the NFVoice plugin (lệnh 569), makes the
// "nailflow" notification channel (sound + buzz), and opens the right screen when a YOUR TURN / read-out notification is tapped (nf_url – lệnh 534).
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(NFVoicePlugin.class);
        super.onCreate(savedInstanceState);
        if (Build.VERSION.SDK_INT >= 26) {
            try { NotificationChannel ch = new NotificationChannel("nailflow", "NailFlow", NotificationManager.IMPORTANCE_HIGH);
                ch.enableVibration(true);
                getSystemService(NotificationManager.class).createNotificationChannel(ch); } catch (Exception e) {}
        }
    }

    private void nfOpen(Intent i) {
        if (i == null) return;
        final String u = i.getStringExtra("nf_url"); if (u == null || u.isEmpty()) return; i.removeExtra("nf_url");
        final String js = "try{location.href=new URL(" + org.json.JSONObject.quote(u) + ",location.href).href}catch(e){}";
        if (getBridge() != null && getBridge().getWebView() != null) getBridge().getWebView().postDelayed(new Runnable() { @Override public void run() { getBridge().getWebView().evaluateJavascript(js, null); } }, 1200);
    }

    @Override
    protected void onNewIntent(Intent intent) { super.onNewIntent(intent); nfOpen(intent); }

    @Override
    public void onResume() { super.onResume(); nfOpen(getIntent()); }
}
