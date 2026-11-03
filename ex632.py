# CHAT 632-ex (anh Logan 02/11 21:04): moi lua chon trong /setup/ co 1 dong VI DU giai thich can ke. Chi doi setup/index.php (chu hien thi), khong doi gia tri luu.
import sys,shutil,time,subprocess,hashlib,json
EX = {
 "q1:clock": ["VD: Lan và Mai đều có 2 turn. Lan clock in 9:30, Mai clock in 9:45 → khách kế giao cho Lan.", "E.g. Lan and Mai both have 2 turns. Lan clocked in at 9:30, Mai at 9:45 → the next customer goes to Lan."],
 "q1:done": ["VD: Lan và Mai đều có 2 turn. Mai làm xong khách lúc 11:00, Lan xong lúc 11:20 → khách kế giao cho Mai.", "E.g. Lan and Mai both have 2 turns. Mai finished at 11:00, Lan at 11:20 → the next customer goes to Mai."],
 "q1:L:fixed": ["VD: ngày nào cũng theo thứ tự chủ xếp sẵn Lan – Mai – Hoa, ai tới trước cũng vậy.", "E.g. every day the owner's order Lan – Mai – Hoa, whoever comes in first."],
 "q1:L:rotate": ["VD: hôm nay Lan đứng đầu, ngày mai Mai đứng đầu, ngày mốt Hoa đứng đầu.", "E.g. today Lan is first, tomorrow Mai, the day after Hoa."],
 "q1:L:yesterday": ["VD: tối qua tới lượt Hoa thì sáng nay bắt đầu từ Hoa.", "E.g. last night it was Hoa's turn, so this morning starts with Hoa."],
 "q1:L:start": ["VD: Lan vừa nhận khách là xuống cuối hàng ngay, không chờ làm xong.", "E.g. Lan goes to the end of the line as soon as she takes a customer."],
 "q2:cust": ["VD: mức $ là 30. Khách trả $45 = 1 turn. Khách trả $20 (dưới $30) thì tính theo ô \"Khách dưới mức đó\" bên dưới (nửa turn / bonus / không tính).", "E.g. the $ line is 30. A $45 customer = 1 turn. A $20 customer (under $30) follows \"A customer under that\" below (half / bonus / nothing)."],
 "q2:svc": ["VD: X = $35. Khách làm pedicure $40 + gel manicure $40 → 2 turn (mỗi dịch vụ từ $35 là 1 turn).", "E.g. X = $35. Pedicure $40 + gel manicure $40 → 2 turns (each service from $35 = 1 turn)."],
 "q2:per": ["VD: X = $35. Khách trả $70 → 2 turn; khách trả $105 → 3 turn.", "E.g. X = $35. A $70 customer → 2 turns; $105 → 3 turns."],
 "q2:L:minutes": ["VD: mỗi 45 phút làm = 1 turn; khách full set làm 90 phút = 2 turn.", "E.g. every 45 minutes = 1 turn; a 90-minute full set = 2 turns."],
 "q2:L:15": ["VD: khách trên $80 (full set + design) = 1.5 turn.", "E.g. a customer over $80 (full set + design) = 1.5 turns."],
 "q4:none": ["VD: khách gọi tên Lan. Lan làm khách đó nhưng không bị tính turn, vẫn giữ chỗ trong hàng.", "E.g. a customer asks for Lan. Lan does her but gets no turn and keeps her place in line."],
 "q4:count": ["VD: Lan làm khách gọi tên mình → Lan bị tính 1 turn và xuống cuối hàng như khách walk-in.", "E.g. Lan does a customer who asked for her → 1 turn, to the end of the line like a walk-in."],
 "q4:half": ["VD: Lan làm khách gọi tên mình → tính 0.5 turn.", "E.g. Lan does a customer who asked for her → half a turn."],
 "q4:L:keepfirst": ["VD: Lan đang đứng đầu hàng thì nhận khách gọi tên mình → không tính turn, nhưng khách walk-in kế giao cho người đứng sau Lan.", "E.g. Lan is first in line and takes her own customer → no turn, but the next walk-in goes to the tech after Lan."],
 "q5:": ["VD: ghi 20. Lan có hẹn lúc 2:00 → từ 1:40 app không giao khách walk-in cho Lan nữa, để Lan rảnh đón khách hẹn.", "E.g. 20. Lan has a booking at 2:00 → from 1:40 the app gives Lan no walk-in, so she is free for it."],
 "q6:1": ["VD: chỉ Tammy và Hana làm builder gel. Khách builder gel tới thì giữ Tammy làm khách đó, Tammy không bị tính mất turn.", "E.g. only Tammy and Hana do builder gel. A builder gel customer comes: Tammy is kept for her and loses no turn."],
 "q6:0": ["VD: khách builder gel tới, hàng là Lan – Tammy – Hana. Lan không biết làm nên bỏ qua, giao Tammy. Lan vẫn giữ chỗ đầu hàng.", "E.g. a builder gel customer, line Lan – Tammy – Hana. Lan can't, so it goes to Tammy. Lan keeps first place."],
 "q6:L:keeplose": ["VD: Tammy được giữ làm khách builder gel và bị tính 1 turn như khách thường.", "E.g. Tammy is kept for the builder gel customer and gets 1 turn like any customer."],
 "q6:L:asreq": ["VD: khách builder gel giao Tammy, tính như khách gọi tên Tammy (theo câu \"khách gọi đích danh\" ở trên).", "E.g. the builder gel customer goes to Tammy, counted like a customer who asked for Tammy (see the question above)."],
 "q7:1": ["VD: tiệm mở cửa 10 giờ. Thợ tới sớm 9 giờ làm khách → không tính turn. Khách bắt đầu từ 9:16 trở đi mới tính turn.", "E.g. the salon opens at 10. A tech who comes in at 9 and does a customer → no turn. From 9:16 on, turns count."],
 "q7:0": ["VD: thợ tới 9 giờ làm khách đầu tiên → tính turn luôn, dù tiệm chưa mở cửa.", "E.g. a tech does the first customer at 9 → it counts, even before opening."],
 "q7:L:othertime": ["VD: tiệm mở 9 giờ, muốn khách bắt đầu trước 8:30 không tính → ghi \"8:30\" ở ô ghi chú bên dưới.", "E.g. the salon opens at 9 and customers before 8:30 should not count → write \"8:30\" in the note below."],
 "q8:1": ["VD: tới lượt Lan nhưng Lan không nhận khách → Lan xuống cuối hàng, khách giao người kế.", "E.g. it is Lan's turn but she says no → Lan goes to the end, the customer goes to the next tech."],
 "q8:N": ["VD: ghi 2. Lan từ chối 2 lần trong ngày vẫn giữ chỗ; lần thứ 3 thì xuống cuối hàng.", "E.g. 2. Lan says no twice in a day and keeps her place; the 3rd time she goes to the end."],
 "q8:0": ["VD: Lan từ chối bao nhiêu lần cũng giữ nguyên chỗ, khách giao người kế.", "E.g. however often Lan says no, she keeps her place; the customer goes to the next tech."],
 "q9:0": ["VD: Lan đi ăn 1 tiếng, về vẫn đứng đúng chỗ cũ trong hàng.", "E.g. Lan takes an hour for lunch and comes back to the same place in line."],
 "q9:N": ["VD: ghi 30. Lan nghỉ 20 phút về vẫn giữ chỗ; nghỉ 45 phút thì xuống cuối hàng.", "E.g. 30. A 20-minute break keeps her place; 45 minutes → end of the line."],
 "q10:L:giveback": ["VD: khách của Lan làm được 5 phút thì bỏ về → Lan không bị tính turn, giữ chỗ như cũ.", "E.g. Lan's customer leaves after 5 minutes → no turn for Lan, she keeps her place."],
 "q10:L:keep": ["VD: khách của Lan bỏ về giữa chừng → Lan vẫn bị tính 1 turn.", "E.g. Lan's customer leaves midway → Lan still gets 1 turn."],
 "q11:=split": ["VD: Lan làm pedicure, Mai làm manicure cho cùng 1 khách → mỗi người tính turn theo dịch vụ mình làm.", "E.g. Lan does the pedicure and Mai the manicure for one customer → each by their own service."],
 "q11:L:half": ["VD: Lan và Mai cùng làm 1 khách → mỗi người 0.5 turn.", "E.g. Lan and Mai on one customer → half a turn each."],
 "q11:L:main": ["VD: Lan làm chính, Mai phụ → Lan 1 turn, Mai không tính.", "E.g. Lan is the main tech, Mai helps → Lan 1 turn, Mai nothing."],
 "q12:1": ["VD: khách walk-in check-in xong, app tự báo \"tới lượt\" trên điện thoại của thợ đứng đầu hàng.", "E.g. a walk-in checks in and the first tech in line gets \"your turn\" on her phone."],
 "q12:0": ["VD: app hiện \"Lan đứng đầu\", lễ tân xem rồi tự bấm chọn thợ cho khách.", "E.g. the app shows \"Lan is first\"; the desk picks the tech."],
 "q13:=nofix": ["VD: khách quay lại sửa 1 móng bị bong → thợ sửa không bị tính turn.", "E.g. a customer comes back to fix one lifted nail → no turn for the tech."],
 "q13:L:otherhalf": ["VD: thợ cũ nghỉ, Mai sửa giúp → Mai được 0.5 turn.", "E.g. the first tech is off and Mai fixes it → Mai gets half a turn."],
 "q13:L:count": ["VD: sửa cũng tính 1 turn như khách thường.", "E.g. a fix counts 1 turn like any customer."],
}
JS = "const EX = " + json.dumps(EX, ensure_ascii=False) + ";\nconst ex = (q, v) => { const t = EX[q + ':' + v]; return t ? `<small class=\"ex\">${esc(V(t[0], t[1]))}</small>` : ''; };\n"
R = [
 ("const cur = q => {", JS + "const cur = q => {"),
 ("`<span class=\"tag later\">${V('NailFlow sẽ liên hệ cài thêm', 'NailFlow will set this up')}</span>` : ''}</span></label>`; }).join('')",
  "`<span class=\"tag later\">${V('NailFlow sẽ liên hệ cài thêm', 'NailFlow will set this up')}</span>` : ''}${ex(q.id, v)}</span></label>`; }).join('')"),
 ("return `<div class=\"q\" data-q=\"${q.id}\"><h3>${esc(q.t)}</h3><div class=\"f\"><span>${esc(lab)}</span>",
  "return `<div class=\"q\" data-q=\"${q.id}\"><h3>${esc(q.t)}</h3><div class=\"f\"><span>${esc(lab)}</span>${ex(q.id, '')}"),
 (".f{margin:8px 0}", ".ex{display:block;color:var(--sub);font-size:14px;line-height:1.4;margin-top:3px}.f{margin:8px 0}"),
]
p = sys.argv[2] + "/setup/index.php"; t = open(p, encoding="utf-8").read()
if "const EX = " in t: sys.exit("ALREADY")
for a, b in R:
    if t.count(a) != 1: sys.exit("STOP anchor %d: %s" % (t.count(a), a[:60]))
n = t
for a, b in R: n = n.replace(a, b)
print("anchors ok", hashlib.sha256(t.encode()).hexdigest()[:8], "->", hashlib.sha256(n.encode()).hexdigest()[:8])
if sys.argv[1] == "out": open(sys.argv[3], "w", encoding="utf-8").write(n); sys.exit()
if sys.argv[1] == "go":
    b = "/root/app/old/setup__index.php.pre-632ex-" + time.strftime("%m%d%H%M"); shutil.copy2(p, b)
    open(p, "w", encoding="utf-8").write(n)
    r = subprocess.run(["/usr/local/bin/php", "-l", p], capture_output=True, text=True)
    if r.returncode: shutil.copy2(b, p); sys.exit("LINT FAIL put back")
    print("PATCHED backup", b)
