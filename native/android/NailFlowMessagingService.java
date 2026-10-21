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
import android.media.MediaPlayer;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import java.util.Locale;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
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

    // (lệnh 569) "🗣 Giọng đọc": the server sends a DATA message with say / sayLang / sayAlarm – this phone shows the notification itself (no sound
    // on the channel) and READS the sentence after a short chime. sayAlarm = "1" (YOUR TURN / a new customer for a clocked-in tech): the ALARM
    // stream, like a clock app – heard even on silent / vibrate (Do Not Disturb: when NailFlow is allowed, Me → 📖).
    static final String VOICE = "nailflow_voice", VOICE_TURN = "nailflow_voice_turn";
    private void voiceChannels(NotificationManager nm) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;
        if (nm.getNotificationChannel(VOICE) == null) { NotificationChannel c = new NotificationChannel(VOICE, "NailFlow – giọng đọc", NotificationManager.IMPORTANCE_HIGH);
            c.setSound(null, null); c.enableVibration(true); c.setVibrationPattern(BUZZ); nm.createNotificationChannel(c); }
        if (nm.getNotificationChannel(VOICE_TURN) == null) { NotificationChannel c = new NotificationChannel(VOICE_TURN, "Khách / Turn – giọng đọc", NotificationManager.IMPORTANCE_HIGH);
            c.setSound(null, null); c.enableVibration(true); c.setVibrationPattern(BUZZ); c.setBypassDnd(true); c.setLockscreenVisibility(Notification.VISIBILITY_PUBLIC); nm.createNotificationChannel(c); }
    }
    /** The chime, then the sentence (TextToSpeech of the phone, the language asked). Waits until spoken (≤ 15 s) – the service stays alive meanwhile. */
    private void speak(final String text, final String lang, final boolean alarm) {
        final AudioAttributes aa = new AudioAttributes.Builder().setUsage(alarm ? AudioAttributes.USAGE_ALARM : AudioAttributes.USAGE_NOTIFICATION_EVENT)
            .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build();
        try { int rid = getResources().getIdentifier("nf_ping", "raw", getPackageName());
            if (rid != 0) { MediaPlayer mp = new MediaPlayer(); mp.setAudioAttributes(aa); mp.setDataSource(this, Uri.parse("android.resource://" + getPackageName() + "/" + rid));
                mp.prepare(); mp.start(); Thread.sleep(Math.min(900, Math.max(300, mp.getDuration()))); mp.release(); } } catch (Exception e) { /* no chime – still read */ }
        final CountDownLatch done = new CountDownLatch(1);
        final TextToSpeech[] t = new TextToSpeech[1];
        try {
            t[0] = new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() { @Override public void onInit(int status) { NFStop.setTts(t[0]); // (lệnh 583) a cancel can stop it
                if (status != TextToSpeech.SUCCESS) { done.countDown(); return; }
                try { t[0].setLanguage(Locale.forLanguageTag(lang != null && !lang.isEmpty() ? lang : "en-US")); t[0].setAudioAttributes(aa);
                    t[0].setOnUtteranceProgressListener(new UtteranceProgressListener() {
                        @Override public void onStart(String id) {}
                        @Override public void onDone(String id) { done.countDown(); }
                        @Override public void onError(String id) { done.countDown(); } });
                    Bundle b = new Bundle(); b.putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME, 1f);
                    if (t[0].speak(text, TextToSpeech.QUEUE_FLUSH, b, "nf569") != TextToSpeech.SUCCESS) done.countDown();
                } catch (Exception e) { done.countDown(); } } });
            done.await(15, TimeUnit.SECONDS);
        } catch (Exception e) { /* never stop the service */ }
        try { if (t[0] != null) t[0].shutdown(); } catch (Exception e) {}
    }

    @Override
    public void onMessageReceived(@NonNull RemoteMessage m) {
        try {
            Map<String, String> d = m.getData();
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (nm != null && m.getNotification() == null && NFChat.show(this, nm, d)) { super.onMessageReceived(m); return; } // (lệnh 581) a customer's text: Messages-style
            String cancel = d.get("cancel");
            if (nm != null && cancel != null && !cancel.isEmpty()) { NFStop.markCancelled(this, cancel); nm.cancel(cancel, ID); nm.cancel(cancel, 569); return; } // (lệnh 583) + remembered, the voice stops
            if ("1".equals(d.get("urgent")) && m.getNotification() == null && (NFStop.stale(d) || NFStop.wasCancelled(this, d.get("tag")))) return; // (lệnh 583) an OLD YOUR TURN (after Accept / late): never rings
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
                final String say = d.get("say"); // (lệnh 569) YOUR TURN read out: the notification buzzes (no ring – the voice is the sound)
                if (say != null && !say.isEmpty()) { voiceChannels(nm); chUse = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O ? VOICE_TURN : CH; snd = null; }
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
                if (say != null && !say.isEmpty()) speak(say, d.get("sayLang"), !"0".equals(d.get("sayAlarm")));
            } else if (nm != null && d.get("say") != null && !d.get("say").isEmpty() && m.getNotification() == null) { // (lệnh 569) any other read-out notification
                voiceChannels(nm);
                String tag = d.get("tag") != null && !d.get("tag").isEmpty() ? d.get("tag") : "v" + System.currentTimeMillis();
                Intent i = new Intent(this, MainActivity.class);
                i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
                i.putExtra("nf_url", d.get("url") != null ? d.get("url") : "");
                PendingIntent pi = PendingIntent.getActivity(this, tag.hashCode(), i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
                NotificationCompat.Builder b = new NotificationCompat.Builder(this, VOICE)
                    .setSmallIcon(getApplicationInfo().icon)
                    .setContentTitle(d.get("title")).setContentText(d.get("body"))
                    .setStyle(new NotificationCompat.BigTextStyle().bigText(d.get("body")))
                    .setPriority(NotificationCompat.PRIORITY_MAX).setVisibility(NotificationCompat.VISIBILITY_PUBLIC).setAutoCancel(true)
                    .setVibrate(BUZZ).setSound(null).setContentIntent(pi);
                nm.notify(tag, 569, b.build());
                speak(d.get("say"), d.get("sayLang"), "1".equals(d.get("sayAlarm")));
            }
        } catch (Exception e) { /* never stop the plugin */ }
        super.onMessageReceived(m);
    }
}
