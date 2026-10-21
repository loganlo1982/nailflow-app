package com.nailflow.salonmanager;

// (lệnh 581) A customer's text looks like a Messages notification: a round picture with the customer's first letter on their own colour,
// the customer's name in bold (no name yet → the number), the words under it, all texts of one customer in ONE notification (MessagingStyle,
// newest last), tap → that chat in the app. The server sends a DATA message {chat: "1", sender, initial, color, thread, body, url, ch, quiet}
// only to this app (build 7+, it said "caps: chat"); older apps keep the normal notification.
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.os.Build;
import android.service.notification.StatusBarNotification;
import androidx.core.app.NotificationCompat;
import androidx.core.app.Person;
import androidx.core.graphics.drawable.IconCompat;
import java.util.Map;

public class NFChat {
    static final int ID = 581;
    static final String GROUP = "nf_chat";

    /** The round picture: the first letter, white, on the customer's colour (like Contacts). */
    static Bitmap avatar(String initial, String color) {
        int size = 192;
        Bitmap bm = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888);
        Canvas c = new Canvas(bm);
        Paint bg = new Paint(Paint.ANTI_ALIAS_FLAG);
        int col; try { col = Color.parseColor(color != null && color.startsWith("#") ? color : "#8E8E93"); } catch (Exception e) { col = Color.parseColor("#8E8E93"); }
        bg.setColor(col);
        c.drawCircle(size / 2f, size / 2f, size / 2f, bg);
        Paint tx = new Paint(Paint.ANTI_ALIAS_FLAG);
        tx.setColor(Color.WHITE); tx.setTextSize(size * 0.46f); tx.setTypeface(Typeface.create(Typeface.DEFAULT, Typeface.BOLD)); tx.setTextAlign(Paint.Align.CENTER);
        String s = initial != null && !initial.isEmpty() ? initial.substring(0, Math.min(2, initial.length())).toUpperCase() : "#";
        float y = size / 2f - (tx.descent() + tx.ascent()) / 2f;
        c.drawText(s, size / 2f, y, tx);
        return bm;
    }

    /** true = shown here (the caller still hands the message to the plugin, as before). */
    static boolean show(Context ctx, NotificationManager nm, Map<String, String> d) {
        if (nm == null || d == null || !"1".equals(d.get("chat"))) return false;
        String body = d.get("body"); if (body == null || body.isEmpty()) return false;
        String thread = d.get("thread"); if (thread == null || thread.isEmpty()) thread = "chat";
        String name = d.get("sender"); if (name == null || name.isEmpty()) name = d.get("title"); if (name == null || name.isEmpty()) name = "Khách";
        String tag = "chat:" + thread;
        String ch = "1".equals(d.get("quiet")) ? "nailflow_quiet" : d.get("ch");
        if (ch == null || ch.isEmpty()) ch = "nailflow";
        if (Build.VERSION.SDK_INT >= 26 && nm.getNotificationChannel(ch) == null) {
            ch = "nailflow";
            if (nm.getNotificationChannel(ch) == null) nm.createNotificationChannel(new NotificationChannel(ch, "NailFlow", NotificationManager.IMPORTANCE_HIGH));
        }
        Person me = new Person.Builder().setName(String.valueOf(ctx.getApplicationInfo().loadLabel(ctx.getPackageManager()))).setKey("salon").build();
        Person who = new Person.Builder().setName(name).setKey(thread).setIcon(IconCompat.createWithBitmap(avatar(d.get("initial"), d.get("color")))).build();
        NotificationCompat.MessagingStyle st = null;
        if (Build.VERSION.SDK_INT >= 23) {
            try { for (StatusBarNotification sb : nm.getActiveNotifications()) if (tag.equals(sb.getTag()) && sb.getId() == ID) { st = NotificationCompat.MessagingStyle.extractMessagingStyleFromNotification(sb.getNotification()); break; } }
            catch (Exception e) { st = null; }
        }
        if (st == null) st = new NotificationCompat.MessagingStyle(me);
        st.addMessage(body, System.currentTimeMillis(), who);
        Intent i = new Intent(ctx, MainActivity.class);
        i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        String url = d.get("url"); i.putExtra("nf_url", url != null ? url : "");
        PendingIntent pi = PendingIntent.getActivity(ctx, tag.hashCode(), i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        NotificationCompat.Builder b = new NotificationCompat.Builder(ctx, ch)
            .setSmallIcon(ctx.getApplicationInfo().icon)
            .setStyle(st)
            .setCategory(NotificationCompat.CATEGORY_MESSAGE)
            .setPriority("1".equals(d.get("quiet")) ? NotificationCompat.PRIORITY_LOW : NotificationCompat.PRIORITY_HIGH)
            .setGroup(GROUP).setAutoCancel(true).setOnlyAlertOnce(false)
            .setContentIntent(pi);
        Notification n = b.build();
        nm.notify(tag, ID, n);
        return true;
    }
}
