#!/usr/bin/env python3
# rebuild the pre-606m backup of inc/api/appts.php (the sim copy wrote through a symlink): reverse the 2 lines, check sha b29f3801, save to ~/app/old
import sys, os, hashlib, time
f = sys.argv[1]; t = open(f, encoding='utf-8').read()
A = [("if ($timeChanged && (empty($in['force']) || $role !== 'admin' || $linkedPart)) {", "if ($timeChanged && (empty($in['force']) || $role !== 'admin')) { // (CHAT 01/11 606m) the owner may move a part of a 2-tech booking too (asked first)"),
     ("if ($linkedPart) fail($msg . ' Moved back.', 409);", "if ($linkedPart && $role !== 'admin') fail($msg . ' Moved back.', 409); // (CHAT 01/11 606m) owner: \"Move anyway?\" below")]
o = t
for a, b in A: o = o.replace(b, a)
s = hashlib.sha256(o.encode()).hexdigest()[:8]; print('rebuilt', s)
if s != 'b29f3801': sys.exit('MISMATCH')
p = os.path.expanduser('~/app/old/inc__api__appts.php.pre-606m-' + time.strftime('%m%d%H%M')); open(p, 'w', encoding='utf-8').write(o); print('saved', p)
