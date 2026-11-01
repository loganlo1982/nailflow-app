import sys, struct, wave, audioop
w = wave.open(sys.argv[1]); n = w.getnchannels(); fr = w.readframes(w.getnframes()); sw = w.getsampwidth()
print('ch', n, 'rate', w.getframerate(), 'sec', round(w.getnframes()/w.getframerate(),1))
if n == 2:
    print('left rms', audioop.rms(audioop.tomono(fr, sw, 1, 0), sw), 'right rms', audioop.rms(audioop.tomono(fr, sw, 0, 1), sw))
