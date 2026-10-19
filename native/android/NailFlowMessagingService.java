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
                NotificationCompat.Builder b = new NotificationCompat.Builder(this, CH)
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
