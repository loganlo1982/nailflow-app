package com.nailflow.salonmanager;

// (lệnh 534) KHẨN – YOUR TURN: the server sends a DATA message {urgent: "1", title, body, url, tag} to this app (build 2+, it said "caps: urgent").
// This service shows it itself on the "Khách / Turn" channel with FLAG_INSISTENT (sound + vibration repeat until the tech taps it) and a full-screen
// intent when the phone is locked. {cancel: tag} = the tech / the desk acted → that notification goes away (the ringing stops).
// Everything else (and the same message) still goes to the Capacitor Firebase plugin as before (super).
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.media.AudioAttributes;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import androidx.annotation.NonNull;
import androidx.core.app.NotificationCompat;
import com.google.firebase.messaging.RemoteMessage;
import java.util.Map;

public class NailFlowMessagingService extends io.capawesome.capacitorjs.plugins.firebase.messaging.MessagingService {
    static final String CH = "nailflow_turn";
    static final int ID = 534;
    static final long[] BUZZ = new long[] { 0, 800, 400, 800, 400, 800 };

    private void channel(NotificationManager nm) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O || nm.getNotificationChannel(CH) != null) return;
        NotificationChannel c = new NotificationChannel(CH, "Khách / Turn", NotificationManager.IMPORTANCE_HIGH);
        c.setDescription("YOUR TURN – kêu + rung tới khi bấm");
        c.enableVibration(true); c.setVibrationPattern(BUZZ); c.setBypassDnd(true); c.setLockscreenVisibility(Notification.VISIBILITY_PUBLIC);
        Uri snd = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM); if (snd == null) snd = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
        c.setSound(snd, new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_ALARM).setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build());
        nm.createNotificationChannel(c);
    }

    // (lệnh 550) two more channels, made when the service starts (before any notification arrives):
    // "nailflow_quiet" = outside the salon's ring hours (shown, no sound / buzz) · "nailflow_ring" = NailFlow's own bell (res/raw/nailflow_ring)
    static final String QUIET = "nailflow_quiet", RING = "nailflow_ring";
    static final String[] SOUNDS = { "alarm", "rush", "door", "chime", "pop", "knock", "ping", "marimba" }; // (lệnh 556)
    @Override
    public void onCreate() {
        super.onCreate();
        try {
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (nm == null || Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;
            if (nm.getNotificationChannel(QUIET) == null) { NotificationChannel q = new NotificationChannel(QUIET, "Ngoài giờ (im lặng)", NotificationManager.IMPORTANCE_LOW);
                q.setSound(null, null); q.enableVibration(false); nm.createNotificationChannel(q); }
            if (nm.getNotificationChannel(RING) == null) { NotificationChannel r = new NotificationChannel(RING, "NailFlow – chuông", NotificationManager.IMPORTANCE_HIGH);
                int id = getResources().getIdentifier("nailflow_ring", "raw", getPackageName());
                Uri u = id != 0 ? Uri.parse("android.resource://" + getPackageName() + "/" + id) : RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
                r.setSound(u, new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_NOTIFICATION).setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build());
                r.enableVibration(true); r.setVibrationPattern(BUZZ); nm.createNotificationChannel(r); }
            // (lệnh 556) one channel per NailFlow sound ("nf_<id>", res/raw/nf_<id>.ogg) – the server picks the channel of the sound each person chose
            for (String sn : SOUNDS) { String cid = "nf_" + sn; if (nm.getNotificationChannel(cid) != null) continue; int rid = getResources().getIdentifier("nf_" + sn, "raw", getPackageName()); if (rid == 0) continue;
                NotificationChannel c = new NotificationChannel(cid, "NailFlow – " + sn, NotificationManager.IMPORTANCE_HIGH);
                c.setSound(Uri.parse("android.resource://" + getPackageName() + "/" + rid), new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_NOTIFICATION).setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build());
                c.enableVibration(true); c.setVibrationPattern(BUZZ); nm.createNotificationChannel(c); }
        } catch (Exception e) { /* never stop the service */ }
    }

    @Override
    public void onMessageReceived(@NonNull RemoteMessage m) {
        try {
            Map<String, String> d = m.getData();
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            String cancel = d.get("cancel");
            if (nm != null && cancel != null && !cancel.isEmpty()) { nm.cancel(cancel, ID); return; }
            if (nm != null && "1".equals(d.get("urgent")) && m.getNotification() == null) {
                channel(nm);
                String tag = d.get("tag") != null ? d.get("tag") : "turn";
                Intent i = new Intent(this, MainActivity.class);
                i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
                i.putExtra("nf_url", d.get("url") != null ? d.get("url") : "");
                PendingIntent pi = PendingIntent.getActivity(this, tag.hashCode(), i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
                Uri snd = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM); if (snd == null) snd = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
                String chUse = CH; String sk = d.get("snd"); // (lệnh 556) the YOUR TURN sound this tech chose: its own "turn" channel (alarm usage, rings until tapped)
                if (sk != null && sk.startsWith("nf_") && Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) { int rid = getResources().getIdentifier(sk, "raw", getPackageName());
                    if (rid != 0) { Uri u = Uri.parse("android.resource://" + getPackageName() + "/" + rid); String cid = "nailflow_turn_" + sk;
                        if (nm.getNotificationChannel(cid) == null) { NotificationChannel c = new NotificationChannel(cid, "Khách / Turn – " + sk.substring(3), NotificationManager.IMPORTANCE_HIGH);
                            c.setSound(u, new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_ALARM).setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build());
                            c.enableVibration(true); c.setVibrationPattern(BUZZ); c.setLockscreenVisibility(Notification.VISIBILITY_PUBLIC); nm.createNotificationChannel(c); }
                        chUse = cid; snd = u; } }
                NotificationCompat.Builder b = new NotificationCompat.Builder(this, chUse)
                    .setSmallIcon(getApplicationInfo().icon)
                    .setContentTitle(d.get("title")).setContentText(d.get("body"))
                    .setStyle(new NotificationCompat.BigTextStyle().bigText(d.get("body")))
                    .setPriority(NotificationCompat.PRIORITY_MAX).setCategory(NotificationCompat.CATEGORY_CALL)
                    .setVisibility(NotificationCompat.VISIBILITY_PUBLIC).setAutoCancel(true)
                    .setVibrate(BUZZ).setSound(snd)
                    .setContentIntent(pi).setFullScreenIntent(pi, true);
                Notification n = b.build();
                n.flags |= Notification.FLAG_INSISTENT;
                nm.notify(tag, ID, n);
            }
        } catch (Exception e) { /* never stop the plugin */ }
        super.onMessageReceived(m);
    }
}
