package com.nailflow.salonmanager;

// (lệnh 583) YOUR TURN must stop the moment the tech (or the desk) taps Accept:
// - a cancel {cancel: tag} is remembered for 1 hour – a YOUR TURN with that tag that arrives LATER (the phone was asleep / offline, FCM delivers
//   the old ones afterwards) is never shown / never rings;
// - a YOUR TURN past its "exp" time (the server's next reminder would have replaced it) is dropped;
// - the sentence being read out (TextToSpeech) is stopped at once.
import android.content.Context;
import android.content.SharedPreferences;
import android.speech.tts.TextToSpeech;
import java.util.Map;

public class NFStop {
    static final String PREF = "nf583";
    static volatile TextToSpeech tts;

    static void markCancelled(Context ctx, String tag) {
        if (tag == null || tag.isEmpty()) return;
        try { SharedPreferences p = ctx.getSharedPreferences(PREF, Context.MODE_PRIVATE); p.edit().putLong("c:" + tag, System.currentTimeMillis()).apply(); } catch (Exception e) { }
        stopTts();
    }
    static boolean wasCancelled(Context ctx, String tag) {
        if (tag == null || tag.isEmpty()) return false;
        try { long t = ctx.getSharedPreferences(PREF, Context.MODE_PRIVATE).getLong("c:" + tag, 0L); return t > 0 && System.currentTimeMillis() - t < 3600000L; } catch (Exception e) { return false; }
    }
    /** true = too old to ring (exp in seconds since 1970, from the server). */
    static boolean stale(Map<String, String> d) {
        try { String e = d.get("exp"); if (e == null || e.isEmpty()) return false; return System.currentTimeMillis() / 1000L > Long.parseLong(e); } catch (Exception x) { return false; }
    }
    static void setTts(TextToSpeech t) { tts = t; }
    static void stopTts() { try { TextToSpeech t = tts; if (t != null) t.stop(); } catch (Exception e) { } }
}
