# v10 turn rules → app settings map

Source: the live release at `/home/claude/int651` (read-only). "Save" = the check in `inc/api/settings.php` (save_settings). "Default" = `inc/core/settings.php` defaults, or the fallback in `tq_cfg()` / `ta_*()` when the key is not stored. Q = the question number in v10 (`/home/claude/turnprev/v10/index.html`, id in brackets).

| key | meaning (from the code) | allowed values | default | v10 Q |
|---|---|---|---|---|
| turn_auto_on | The app gives "Anyone" walk-ins to the first free tech in line (YOUR TURN); 0 = the owner/desk assigns and the app only shows the line. `inc/turnauto.php:17` (ta_on), `assets/admin/turn-mode.js:1-4`; save `settings.php:312` | 1 / 0 | 1 (hair salons 0) `core/settings.php:135,191` | 1 (a1) |
| turn_tie | Equal turns: who clocked in first, or who finished a customer first. `inc/turnq.php:26,348`; save `settings.php:296` | clock / done | clock | 2 (a2) |
| turn_wait_auto | Everyone busy: the app guesses the first-in-line tech's end (start + menu minutes); done in ≤ turn_wait_min → the customer waits for her. `turnauto-dispatch.php:216`, `turnq.php:28`; save `settings.php:302` | 1 / 0 | 0 | 3 (a3) |
| turn_wait_min | Minutes for turn_wait_auto and for wait mode 'wait'. `turnq.php:28`, `turnauto-dispatch.php:186`; save `settings.php:297` (0–60; 0/empty → 10) | 1–60 | 10 | 3–4 (a3, a4) |
| turn_wait_mode | Busy tech's turn with another tech free: wait for her if done in ≤ turn_wait_min, or give it to the free tech now. `turnauto-dispatch.php:180-186`, `turnq.php:28`; save `settings.php:296` | wait / free | wait | 4 (a4) |
| turn_ask_min | Before giving to a free tech, a busy tech ahead who has worked ≥ N min is asked "how long?" (only when turn_wait_auto = 0; not for requested/booked). `turnauto-dispatch.php:233`; save `settings.php:333` | 0 (off) – 240 | 45 `core/settings.php:143` | 5 (a5) |
| turn_wait_ok | That tech answers ≤ N min → the walk-in waits for her. save `settings.php:334` | 1–30 | 5 | 5 (a5) |
| turn_wait_max | Longest wait after the answer, then the free tech gets it ("late"). `turnauto-dispatch.php:127-128`; save `settings.php:335` (must be ≥ turn_wait_ok) | 1–60 | 8 | 5 (a5) |
| turn_ask_reply | Minutes to answer the question; no answer → free tech. `turnauto-dispatch.php:116-118`; save `settings.php:336` | 1–10 | 2 | 5 (a5) |
| turn_wait_alert | A walk-in waiting this long with no tech → the desk is told once. `core/turns-plan.php:72`, `api/desk.php:79`; save `settings.php:313` | 0 (off) – 240 | 60 `core/settings.php:130` | 6 (a6) |
| turn_req_mode | Customer who asked for the tech by name (incl. booked AND asked): like any customer / no turn / half. Also writes turn_count_req. `turnq.php:17-18,32`; save `settings.php:292-293` | count / none / half | count (stored '' → from turn_count_req = 1) `core/settings.php:129,132` | 7 (b1) |
| turn_early | A booked customer who came early vs a waiting walk-in: booked first, or who waited longer (at the booked time: booked). `inc/turn-early.php:8-31`; save `settings.php:296` | appt / wait | appt `core/settings.php:179` | 8 (b2) |
| turn_hold_min | A tech whose booked customer starts within N min gets no walk-in (keeps her place); booking 15+ min late → not kept. `turnauto-state.php:107-116`; save `settings.php:297` | 0 (only at the booked time) – 120 | 20 (`turnq.php:28`) | 9 (b3) |
| turn_rare_keep | Keep a tech who does a rare service (only 1–2 techs today) for the customer who needs it; kept = no turn lost. `turnq.php:28`; save `settings.php:301` | 1 / 0 | 1 | 10 (b4) |
| turn_min | A service from $N = 1 turn (0 = every customer counts). `turnq.php:19-21,199-200`; save `settings.php:294` | 0–1000 | 30 | 11 (c1) |
| turn_under | A customer under turn_min: half a turn / bonus (own rotation, no turn) / nothing. `turnq.php:21,195-200`; save `settings.php:304` | half / bonus / none | half | 12 (c2) |
| turn_bonus_n | Every N bonus = 1 turn on the line (0 = off). `turnq.php:27,345`; save `settings.php:297` | 0–20 | 0 | 13 (c3) |
| turn_multi | Several services, same tech: whole customer = 1 turn / each service from turn_svc_amt = 1 turn / every turn_multi_amt of the total = 1 turn. `turnq.php:21,184-201`; save `settings.php:305` | cust / svc / per | cust | 14 (c4) |
| turn_svc_amt | The $ for "each service from $… = 1 turn". `turnq.php:22` (svcMin; empty → turn_min); save `settings.php:307` | 1–1000 | = turn_min (30) | 14 (c4, svc) |
| turn_multi_amt | The $ for "every $… of the total = 1 turn". `turnq.php:19,21`; save `settings.php:306` | 1–1000 | 35 | 14 (c4, per) |
| turn_with | (svc mode) small services with a big one: nothing more / 1 bonus each (bonus only when turn_under = bonus). `turnq.php:22,193`; save `settings.php:308` | zero / bonus | zero | 15 (c5) |
| turn_small | (svc mode) only small services: each on its own by turn_under / add up – total ≥ the $ = 1 turn. `turnq.php:22,194-198`; save `settings.php:310` | each / sum | each | 16 (c6) |
| turn_half_svcs | Services that count half a turn (only when all services of the visit are on the list). `turnq.php:18,202`; save `settings.php:311` | list of service ids | (none) | 17 (c7) – names, NailFlow maps to ids |
| turn_none_svcs | Services that count nothing (no turn, no bonus); a customer with only these goes to the tech free the longest. `turnq.php:26,36,41`; save `settings.php:303` | list of service ids | (none) | 18 (c8) – names |
| turn_assign | Several services – who may take the customer: a tech who does the MAIN service / the next tech if she does one service / only a tech who does all. `turnauto.php:145-170`; save `settings.php:326` | main / some / all | main (migration 553 put every salon on main) | 19 (d1) |
| turn_pass | 2+ services: first part done → the next service goes to the next free tech who can (feet first). `turnauto-pass.php:22-35`; save `settings.php:325` | 1 / 0 | '' → main_salon(): ON for American Nails, OFF for other salons | 20 (d2) |
| turn_skill_split | The free first-in-line tech does the part she can do now, the rest goes to the next tech after Service done (never at once). `turnauto-pass.php:63`, `settings-pay.js:60-62`; save `settings.php:324` | 1 / 0 | '' → main_salon() (AN ON, others OFF) | 21 (d3) |
| te_pass_auto | Nobody free for the next part → the tech continues at once (no question). `inc/tech-easy.php:11,14`; save `settings.php:299` | 1 / 0 | 1 | 22 (d4) |
| turn_brk_max | A break longer than N min → the end of the line (0 = always keeps the place). `turnauto-pass.php:9-10`; save `settings.php:297` | 0–600 | 0 | 23 (e1) |
| turn_out_staff | Techs not in the turn line (only when the desk picks them). `turnq.php:27,350`; save `settings.php:303` | list of staff ids | (none) | 24 (e2) – names |
| turn_skip_max | Skips MORE than N in a day → the end of the line; 0 = always keeps the place. A "can't do this service" Skip never counts (2.99.650). `turnauto-state.php:68-79`; save `settings.php:297` | 0–20 | 0 | 25 (f1) |
| turn_accept_min | Time to tap Accept: off (no Accept) / minutes / no limit. `turnauto.php:19-20`; save `settings.php:318-320` | off / none / 1–30 | 3 `core/settings.php:139` | 26 (f2) |
| turn_timeout_do | Not accepted in time: tell the desk / next tech by itself / the desk taps Accept for her. `turnauto.php:39`; save `settings.php:323` | tell / next / desk | tell | 27 (f3) |
| turn_pre_open | A customer STARTED at 9:15 AM or earlier and before opening counts nothing (the 9:15 is fixed in code). `turnq.php:272-274`; save `settings.php:309` | 1 / 0 | 0 | 28 (g1) |
| turn_late | A tech who clocks in late: starts from 0 / with the lowest turns now. `turnq.php:26,327-328`; save `settings.php:296` | zero / min | zero | 29 (g2) |
| clock_early_min | Techs can clock in on the iPad from N min before opening. `api/_auth.php:72`; save `settings.php:337` | 0–240 | 60 `core/settings.php:147` | 30 (g3) |
| ck_pick_tech | Customers may pick a tech on the check-in iPad (= a request). `api/checkin.php:217`; save `settings.php:315` | 1 / 0 | 0 | 31 (h1) |
| ck_unsure_btn | "Not sure yet – Skip" on the check-in iPad. `api/checkin.php:214`; save `settings.php:316` | 1 / 0 | 0 | 32 (h2) |
| ck_undecided_min | Minutes held on the schedule for a "Not sure" customer. `api/checkin.php:225`; save `settings.php:439` | 5–180 | 30 `core/settings.php:100` | 32 (h2) |
| ck_anytime | Check-in outside business hours allowed. `api/_kiosk.php:72-73`; save `settings.php:314` | 1 / 0 | 1 | 33 (h3) |
| te_co_done | Desk opens Checkout → that customer's techs are Service done. `tech-easy.php:4`; save `settings.php:299` | 1 / 0 | 1 | 34 (i1) |
| te_one_tap | Service done = one tap + 5 s undo. `tech-easy.php:5` | 1 / 0 | 1 | 35 (i2) |
| te_over_ask | 15 min past the expected end → ask the desk once. `tech-easy.php:7`, `api/notify.php:91` | 1 / 0 | 1 | 36 (i3) |
| te_eta_small | "Still a while / Almost done" buttons small. `tech-easy.php:8` | 1 / 0 | 1 | 37 (i4) |
| te_accept_big | YOUR TURN: Accept fills half the screen. `tech-easy.php:9` | 1 / 0 | 1 | 38 (i5) |
| te_desk_acts | The desk can tap the tech's buttons (Done, Break, I'm back). `tech-easy.php:10` | 1 / 0 | 1 | 39 (i6) |
| rot_order | Tech order used when the app picks a tech for an "any tech" booking (after free time and turns). `core/turns-plan.php:138-142,210-217`; set by `api/staffpages.php:250` | ordered list of staff ids | all active techs | 40 (i7) – names |

## Not owner choices (left out)

| key | why |
|---|---|
| turn_count_req | Legacy mirror of turn_req_mode (written by save_settings `settings.php:293`). |
| turn_hold_buf | No longer used: replaced by turn_hold_min (`turnauto-state.php:111`); no UI. |
| turn_late2_from | Set once by the code (`turnq.php:31`) – migration date. |
| turn_split_ids, turn_svc_hold | Internal state (`turnq.php:37,134`, `checkout-edit.php:104`, `person-edit.php:41`). |
| turn_assign_was, ta_mig553 | Migration 553 bookkeeping (`turnauto.php:152-153`). |
| turn_voice | Per-tech voice language, set on the staff page (`core/staff-services.php:162-166`). |
| ipad_voice, tv_* , notify_clock, day_report_* | Sound / notification settings on the Turn page, not turn rules. |

## Not in the app (v10 last section, sent as `not_in_app`)

| v10 Q | what the app does now |
|---|---|
| 41 (m1) hands or feet first | Always feet first when turn_pass is ON (`turnauto-pass.php:25-35`); no choice. |
| 42 (m2) two techs at the same time | Never at once (turn_pass / turn_skill_split are one after the other). |
| 43 (m3) small extra first / last | No rule. |
| 44 (m4) changed service after check-in | A is built in: Skip "can't do this service" → next tech, keeps place, not counted (`turnauto-state.php:68`); no setting. |
| 45 (m5) a group at the same time | Persons 2, 3 of a party never wait for a busy tech (`turnauto-dispatch.php:232`); no setting. |

## JSON copied from the "Will save" sheet

`{"salon": "...", "settings": {key: value as in the table}, "notes": [{q, question, note}], "not_in_app": [{q, question, choice, label}], "lists_by_name": [...]}` – the four list keys carry names, which NailFlow maps to the salon's ids before applying.
