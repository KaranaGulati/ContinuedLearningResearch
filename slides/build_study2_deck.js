// Builds slides/study2-final.pptx. Run with NODE_PATH pointing at a node_modules that has pptxgenjs.
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.APPLY_THEME ||
  "/root/.claude/skills/synced/2a801b73-387a-4a8f-a933-cd1229816463_1e1899ee-efee-4430-b963-be75ebe16f62/pptx/scripts/apply_theme.js");

const OUT = process.argv[2] || "study2-final.pptx";
const THEME = {
  name: "Chess Study 2", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "2D2D2D", lt1: "FFFFFF", dk2: "1F4E79", lt2: "EBF3FA", accent1: "2E75B6", accent2: "1F4E79",
            accent3: "C27C0E", accent4: "777777", accent5: "A0BBDD", accent6: "FFF2CC", hlink: "2E75B6", folHlink: "1F4E79" },
};
const HEX = { navy: "1F4E79", blue: "2E75B6", amber: "C27C0E", gray: "777777", grid: "D9D9D9",
              band: "EBF3FA", body: "2D2D2D", light: "A0BBDD", callout: "FFF2CC" };

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.theme = { headFontFace: "Arial", bodyFontFace: "Arial" };
pres.title = "Do lucky wins make chess players play worse in their next game?";
pres.author = "Karana Gulati";
const C = pres.SchemeColor;
const M = 0.5, W = 9;
const F = { title: 26, header: 20, body: 20, label: 16, cite: 12 };

pres.defineSlideMaster({ title: "TITLE_DARK", background: { color: HEX.navy }, objects: [
  { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 1.1, w: 8.6, h: 1.8, fontSize: 34, bold: true,
      color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } },
  { placeholder: { options: { name: "body", type: "body", x: 0.7, y: 3.1, w: 8.6, h: 1.4, fontSize: 18,
      color: C.accent5, align: "left", valign: "top", margin: 0 }, text: "" } } ] });
pres.defineSlideMaster({ title: "SECTION", background: { color: HEX.navy }, objects: [
  { placeholder: { options: { name: "body", type: "body", x: 0.7, y: 1.7, w: 8.6, h: 0.5, fontSize: 18,
      color: C.accent5, align: "left", valign: "top", margin: 0 }, text: "" } },
  { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 2.2, w: 8.6, h: 1.4, fontSize: 36, bold: true,
      color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } } ] });
pres.defineSlideMaster({ title: "CONTENT", background: { color: "FFFFFF" }, objects: [
  { placeholder: { options: { name: "title", type: "title", x: M, y: 0.25, w: W, h: 0.9, fontSize: F.title, bold: true,
      color: C.text2, align: "left", valign: "top", margin: 0 }, text: "" } } ],
  slideNumber: { x: 9.1, y: 5.2, w: 0.5, h: 0.3, fontSize: 11, color: HEX.gray, fontFace: "Arial" } });
pres.defineSlideMaster({ title: "CLOSE_DARK", background: { color: HEX.navy }, objects: [
  { placeholder: { options: { name: "title", type: "title", x: M, y: 0.3, w: W, h: 0.5, fontSize: 20, bold: false,
      color: C.accent5, align: "left", valign: "top", margin: 0 }, text: "" } } ] });

const nb = (t) => typeof t === "string" ? t.replace(/(\d) (cp|pawns?|min)\b/g, "$1 $2").replace(/p = /g, "p = ").replace(/ < /g, " < ") : t.map((r) => ({ ...r, text: nb(r.text) }));
function text(s, t, o) {
  s.addText(nb(t), Object.assign({ isTextBox: true, fontFace: "Arial", color: C.text1, valign: "top", margin: 0, fontSize: F.body }, o));
}
function bullets(s, items, o) {
  const runs = items.map((t, i) => ({ text: nb(t), options: { bullet: true, breakLine: i < items.length - 1 } }));
  s.addText(runs, Object.assign({ isTextBox: true, fontFace: "Arial", fontSize: F.body, color: C.text1, valign: "top",
    paraSpaceAfter: 10, margin: 0 }, o));
}
function cite(s, t) { text(s, t, { x: M, y: 5.15, w: 8.4, h: 0.3, fontSize: F.cite, color: HEX.gray, valign: "middle" }); }
function box(s, x, y, w, h, fill, line, name) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: line, width: 1 },
    rectRadius: 0.06, objectName: name });
}
function formula(s, t, x, y, w, h, size) {
  box(s, x, y, w, h, HEX.band, HEX.blue, "formula");
  text(s, t, { x: x + 0.2, y, w: w - 0.4, h, fontSize: size || F.body, color: HEX.navy, bold: true, valign: "middle", align: "center" });
}
const th = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: HEX.navy } } });
function table(s, rows, o) {
  s.addTable(rows, Object.assign({ x: M, w: W, fontFace: "Arial", fontSize: F.label, color: HEX.body,
    border: { type: "solid", pt: 0.75, color: HEX.grid }, valign: "middle", margin: 0.07 }, o));
}
function title(s, t) { s.addText(nb(t), { placeholder: "title" }); }
function section(label, t, notes) {
  pres.addSection({ title: t });
  const s = pres.addSlide({ masterName: "SECTION", sectionTitle: t });
  s.addText(label, { placeholder: "body" });
  s.addText(t, { placeholder: "title" });
  s.addNotes(notes);
  return t;
}
let SEC = "Introduction";
const slide = () => pres.addSlide({ masterName: "CONTENT", sectionTitle: SEC });

// Confidence-interval plot built from native shapes.
function ciPlot(s, rows, o) {
  const { x, y, w, rowH, labelW, lo, hi, ticks, band, unit } = o;
  const px0 = x + labelW, pw = w - labelW, X = (v) => px0 + ((v - lo) / (hi - lo)) * pw, plotH = rows.length * rowH;
  if (band) {
    s.addShape(pres.shapes.RECTANGLE, { x: X(-band), y, w: X(band) - X(-band), h: plotH, fill: { color: HEX.band },
      line: { color: HEX.band, width: 0 }, objectName: "zone" });
    text(s, `"no real difference" zone: ±${band} ${unit}`, { x: X(-band) - 0.5, y: y + plotH + 0.38, w: X(band) - X(-band) + 1,
      h: 0.28, fontSize: 13, color: HEX.blue, align: "center" });
  }
  s.addShape(pres.shapes.LINE, { x: X(0), y: y - 0.05, w: 0, h: plotH + 0.1, line: { color: HEX.gray, width: 1, dashType: "dash" }, objectName: "zero" });
  rows.forEach((r, i) => {
    const cy = y + i * rowH + rowH / 2, col = r.highlight ? HEX.amber : HEX.navy;
    text(s, r.label, { x, y: cy - 0.25, w: labelW - 0.15, h: 0.5, fontSize: 14, valign: "middle", color: r.highlight ? HEX.amber : C.text1, bold: !!r.highlight });
    s.addShape(pres.shapes.LINE, { x: X(r.ci[0]), y: cy, w: X(r.ci[1]) - X(r.ci[0]), h: 0, line: { color: col, width: 2.5 }, objectName: "ci " + i });
    s.addShape(pres.shapes.OVAL, { x: X(r.est) - 0.08, y: cy - 0.08, w: 0.16, h: 0.16, fill: { color: col }, line: { color: col, width: 0 }, objectName: "est " + i });
    text(s, `${r.est > 0 ? "+" : ""}${r.est.toFixed(2)}`, { x: X(r.ci[1]) + 0.08, y: cy - 0.14, w: 0.6, h: 0.28, fontSize: 13, color: col, bold: true, valign: "middle" });
  });
  const ay = y + plotH + 0.05;
  s.addShape(pres.shapes.LINE, { x: px0, y: ay, w: pw, h: 0, line: { color: HEX.gray, width: 1 }, objectName: "axis" });
  ticks.forEach((t) => text(s, `${t > 0 ? "+" : ""}${t}`, { x: X(t) - 0.3, y: ay + 0.04, w: 0.6, h: 0.25, fontSize: 13, color: HEX.gray, align: "center" }));
  text(s, o.axisTitle, { x: px0, y: ay + 0.66, w: pw, h: 0.28, fontSize: 13, color: HEX.gray, align: "center" });
}

// ================= 1. Title =================
pres.addSection({ title: "Introduction" });
let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Introduction" });
s.addText("Do lucky wins make chess players play worse in their next game?", { placeholder: "title" });
s.addText([
  { text: "Study 2: 41,957 online games, analysed with a plan fixed before any data was scored", options: { breakLine: true } },
  { text: " ", options: { breakLine: true } },
  { text: "Karana Gulati  ·  October 2026", options: { color: HEX.light } },
], { placeholder: "body" });
s.addNotes("This talk is about one question: if you win a chess game by luck, does it affect how well you play your next game? You do not need to know chess or advanced maths. Every idea is built from the ground up.");

// ================= Part 1 =================
SEC = section("Part 1", "The basics, no chess needed", "First, the three ideas everything else rests on: how chess games are won, how a computer scores a position, and how we turn that score into a measure of how well someone played.");

s = slide();
title(s, "A chess game can be won in three ways, and most wins come from the opponent giving up");
s.addChart(pres.charts.BAR, [{ name: "Share of wins", labels: ["Opponent's clock ran out", "Checkmate", "Opponent resigned"], values: [11.4, 30.0, 58.6] }], {
  x: M, y: 1.3, w: 5.3, h: 3.6, barDir: "col", chartColors: [HEX.amber, HEX.blue, HEX.blue],
  showValue: true, dataLabelFormatCode: '0"%"', dataLabelPosition: "outEnd", dataLabelColor: HEX.body, dataLabelFontSize: F.label,
  dataLabelFontFace: "+mn-lt", catAxisLabelFontFace: "+mn-lt", catAxisLabelColor: HEX.body, catAxisLabelFontSize: 14,
  valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, valAxisMaxVal: 70, valAxisMinVal: 0, showLegend: false });
text(s, "How a game ends", { x: 6.1, y: 1.35, w: 3.4, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
bullets(s, ["Checkmate: the king is trapped", "Resignation: the loser gives up", "On time: each player has a clock, and it ran out"],
  { x: 6.1, y: 1.85, w: 3.4, h: 3.1 });
cite(s, "Lichess rated rapid games, first 2 million games of September 2026");
s.addNotes("Every online chess game has a clock for each player, like a timer in a quiz. You can win in three ways: trap the opponent's king, which is checkmate; the opponent gives up, which is resignation; or the opponent's clock runs out. About one win in nine is on time.");

s = slide();
title(s, "A win on time can be undeserved: one in five time winners was losing when the clock ran out");
box(s, M, 1.4, 4.3, 2.3, HEX.band, HEX.blue, "deserved");
text(s, "Deserved time win", { x: M + 0.25, y: 1.55, w: 3.8, h: 0.4, fontSize: F.header, bold: true, color: HEX.navy });
text(s, "You were ahead on the board, and the opponent also ran out of time.", { x: M + 0.25, y: 2.05, w: 3.8, h: 1.5 });
box(s, 5.2, 1.4, 4.3, 2.3, HEX.callout, HEX.amber, "lucky");
text(s, "Lucky time win", { x: 5.45, y: 1.55, w: 3.8, h: 0.4, fontSize: F.header, bold: true, color: HEX.amber });
text(s, "You were losing on the board, but the opponent's clock hit zero first.", { x: 5.45, y: 2.05, w: 3.8, h: 1.5 });
text(s, [{ text: "14,284 of 70,000 ", options: { bold: true, color: HEX.amber } }, { text: "time wins checked were lucky (20.4%)." }],
  { x: M, y: 4.0, w: W, h: 0.8 });
cite(s, "Study 2 screening: final positions of 70,000 time wins scored by Stockfish 16, 6 to 30 September 2026");
s.addNotes("This is the key idea of the study. A win on time is recorded as a win, even if you were completely losing the actual game. We checked 70,000 time wins with a chess computer and found that in about one in five, the winner was the one losing on the board. Those are lucky wins.");

s = slide();
title(s, "A chess computer gives every position a score, measured in centipawns (100 cp = 1 pawn)");
const nlX = 1.0, nlW = 8.0, nlY = 2.55, NX = (v) => nlX + ((v + 500) / 1000) * nlW;
s.addShape(pres.shapes.LINE, { x: nlX, y: nlY, w: nlW, h: 0, line: { color: HEX.navy, width: 2.5 }, objectName: "number line" });
[-500, -300, -100, 0, 100, 300, 500].forEach((v) => {
  s.addShape(pres.shapes.LINE, { x: NX(v), y: nlY - 0.1, w: 0, h: 0.2, line: { color: HEX.navy, width: 1.5 }, objectName: "tick " + v });
  text(s, (v > 0 ? "+" : "") + v, { x: NX(v) - 0.4, y: nlY + 0.15, w: 0.8, h: 0.3, fontSize: 14, align: "center", color: HEX.gray });
});
text(s, "Black is winning", { x: nlX - 0.2, y: 1.75, w: 2.6, h: 0.4, fontSize: F.label, bold: true, color: HEX.navy });
text(s, "Equal", { x: NX(0) - 0.6, y: 1.75, w: 1.2, h: 0.4, fontSize: F.label, bold: true, color: HEX.navy, align: "center" });
text(s, "White is winning", { x: NX(500) - 2.4, y: 1.75, w: 2.6, h: 0.4, fontSize: F.label, bold: true, color: HEX.navy, align: "right" });
bullets(s, ["A pawn is the smallest chess piece; 1 pawn = 100 cp", "+300 means White is about 3 pawns better", "We always read the score from the side of the player we study"],
  { x: M, y: 3.25, w: W, h: 1.8 });
s.addNotes("A chess computer, called an engine, can look at any position and give one number for who is better and by how much. The unit is the centipawn, a hundredth of a pawn. Zero means equal. Plus 300 means White is about three pawns ahead. This is the same line you see in the graph after a game on chess.com.");

s = slide();
title(s, "A move's mistake is how much it lowers the player's own score");
table(s, [
  [th("Move"), th("Score before"), th("Score after"), th("Mistake (loss)")],
  ["1", "+50", "+40", "10 cp"],
  ["2", "+40", "-250", { text: "290 cp (a blunder)", options: { bold: true, color: HEX.amber } }],
  ["3", "-250", "-200", "0 cp (score went up)"],
  ["4", "-200", "-220", "20 cp"],
], { y: 1.3, colW: [1.2, 2.4, 2.4, 3.0], rowH: 0.42 });
formula(s, "loss = max(0, score before − score after)", M, 3.65, W, 0.7);
text(s, "Illustrative numbers. Scores are from the moving player's side, so for Black the engine's sign is flipped.",
  { x: M, y: 4.5, w: W, h: 0.6, fontSize: 14, color: HEX.gray });
s.addNotes("To measure how well someone played, we look at each of their moves. If the score was +40 before a move and -250 after, the move threw away 290 centipawns, almost three pawns. If the score goes up, the loss is zero, because you cannot do better than the engine's best move. 'max of zero and' just means negative losses count as zero.");

s = slide();
title(s, "Average centipawn loss (ACPL) is the average mistake per move, so lower means better play");
formula(s, "ACPL = (loss₁ + loss₂ + … + lossₙ) ÷ n", M, 1.35, W, 0.75);
text(s, "Example from the previous slide: (10 + 290 + 0 + 20) ÷ 4 = 80 cp", { x: M, y: 2.3, w: W, h: 0.5 });
text(s, "In study 2's next games", { x: M, y: 3.0, w: W, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
bullets(s, ["Middle player: 61 cp per move", "Middle half of games: 38 to 95 cp", "Each 100 rating points stronger: about 3.7 cp lower"],
  { x: M, y: 3.5, w: W, h: 1.5 });
cite(s, "Study 2, 23,995 lucky and deserved pairs; rating effect from the regression in Part 3");
s.addNotes("ACPL is just the average of those losses over the moves we score. A perfect game would be zero. Club players in our data lose about 61 centipawns per move on a typical game. Stronger players lose less: about 3.7 centipawns less for every 100 rating points. That gives us a way to translate centipawns into rating points later.");

s = slide();
title(s, "Study 1 found the type of win barely matters, but hinted that lucky wins might");
box(s, M, 1.35, 4.3, 2.4, HEX.band, HEX.blue, "study 1 result");
text(s, "Main result", { x: M + 0.25, y: 1.5, w: 3.8, h: 0.4, fontSize: F.header, bold: true, color: HEX.navy });
text(s, "Time, checkmate and resignation wins: next-game gaps under 1 cp (18,002 games).", { x: M + 0.25, y: 2.0, w: 3.8, h: 2.3 });
box(s, 5.2, 1.35, 4.3, 2.4, HEX.callout, HEX.amber, "study 1 hint");
text(s, "Unplanned hint", { x: 5.45, y: 1.5, w: 3.8, h: 0.4, fontSize: F.header, bold: true, color: HEX.amber });
text(s, "1,288 lucky time winners played 2.2 cp worse. Too few to be sure (p = 0.15).", { x: 5.45, y: 2.0, w: 3.8, h: 2.3 });
cite(s, "Study 1: Lichess rated rapid, 1 to 5 August and 1 to 5 September 2026; results/SUMMARY.md");
s.addNotes("Our first study asked whether winning on time, by checkmate or by resignation changes the next game. It barely does. But when we split the time wins afterwards, the lucky ones seemed to play a bit worse. Because we only spotted that after looking, it could have been chance. Study 2 was built to test it properly.");

// ================= Part 2 =================
SEC = section("Part 2", "The questions", "Next, exactly what study 2 asked, and what was predicted before any of its data was looked at.");

s = slide();
title(s, "Two questions, each with a prediction fixed and dated before any data was scored");
function rq(x, tag, q, h) {
  box(s, x, 1.3, 4.35, 2.75, HEX.band, HEX.blue, tag);
  text(s, tag, { x: x + 0.25, y: 1.42, w: 3.9, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
  text(s, q, { x: x + 0.25, y: 1.88, w: 3.9, h: 1.0, color: HEX.navy });
  text(s, h, { x: x + 0.25, y: 2.9, w: 3.9, h: 1.1 });
}
rq(M, "RQ2 (main)", "Does a lucky time win change the next game?", "Prediction: no. Players reset, within ±2 cp.");
rq(5.15, "RQ1 (repeat)", "Does the type of win change the next game?", "Prediction: no. Within ±3 cp, as in study 1.");
text(s, "Fixing the prediction first is like painting the target before shooting the arrow.", { x: M, y: 4.3, w: W, h: 0.75, fontSize: 18, color: HEX.gray });
cite(s, "PREREGISTRATION_STUDY2.md, committed 12 October 2026, 11:02 UTC");
s.addNotes("Both predictions were written down, dated and saved publicly before a single game was scored. Why? If you look at the data first, with dozens of ways to slice it, something will look interesting by pure chance. Writing the prediction first means the result can be trusted.");

// ================= Part 3 =================
SEC = section("Part 3", "How it was measured", "Now the method: where the games came from, how lucky wins were found, how the comparison was made fair, and how the numbers were tested.");

s = slide();
title(s, "From 89.6 million games to about 24,000 comparable pairs");
const steps = [
  ["89,616,462", "all rated games, September 2026"],
  ["14,935,862", "rapid games, standard chess, no computer accounts"],
  ["454,791", "time wins followed by a next game, rating 1200–2000, 6–30 Sep"],
  ["148,277", "one per player"],
  ["70,000", "checked by the chess computer, in random order"],
  ["12,033 + 11,962", "lucky + deserved pairs scored"],
];
steps.forEach(([n, d], i) => {
  const w = 9 - i * 0.6, x = M + (W - w) / 2, y = 1.25 + i * 0.6;
  box(s, x, y, w, 0.5, i === 5 ? HEX.callout : HEX.band, i === 5 ? HEX.amber : HEX.blue, "funnel " + i);
  text(s, [{ text: n + "  ", options: { bold: true, color: i === 5 ? HEX.amber : HEX.navy } }, { text: d }],
    { x: x + 0.15, y, w: w - 0.3, h: 0.5, fontSize: 15, valign: "middle", align: "center" });
});
cite(s, "Lichess open database (database.lichess.org, CC0). Box widths are not to scale.");
s.addNotes("We started with every rated game played on Lichess in September 2026, nearly 90 million. We kept rapid games, which last about 10 to 15 minutes, removed computer accounts, and kept players rated 1200 to 2000. Then we took one time win per player, checked 70,000 of them with the chess computer, and ended with about 12,000 lucky and 12,000 deserved pairs.");

s = slide();
title(s, "A pair is one win plus the same player's very next game, started within 30 minutes");
box(s, M, 1.6, 3.0, 1.4, HEX.band, HEX.blue, "game A");
text(s, [{ text: "Game A", options: { bold: true, breakLine: true } }, { text: "the win (lucky or deserved)" }], { x: M + 0.2, y: 1.6, w: 2.6, h: 1.4, valign: "middle", color: HEX.navy });
s.addShape(pres.shapes.RIGHT_ARROW, { x: 3.65, y: 2.1, w: 1.7, h: 0.4, fill: { color: HEX.gray }, line: { color: HEX.gray, width: 0 }, objectName: "arrow" });
text(s, "≤ 30 min, no game in between", { x: 3.45, y: 2.6, w: 2.1, h: 0.6, fontSize: 14, color: HEX.gray, align: "center" });
box(s, 5.5, 1.6, 4.0, 1.4, HEX.callout, HEX.amber, "game B");
text(s, [{ text: "Game B", options: { bold: true, breakLine: true } }, { text: "the next game: moves 15 to 30 are scored" }], { x: 5.7, y: 1.6, w: 3.6, h: 1.4, valign: "middle", color: HEX.amber });
bullets(s, ["We measure how well game B was played", "Game A only tells us which group the pair is in"], { x: M, y: 3.5, w: W, h: 1.4 });
s.addNotes("Each data point is a pair. Game A is the win. Game B is the same player's next rated game, which must start within 30 minutes with no other game in between. Any after-effect of a lucky win should show up right away, not days later. We only measure accuracy in game B.");

s = slide();
title(s, "The computer's score at the end of game A decides whether the win was lucky");
const L = (v) => 1.0 + ((v + 1000) / 2000) * 8.0;
s.addShape(pres.shapes.RECTANGLE, { x: L(-1000), y: 1.55, w: L(-100) - L(-1000), h: 0.55, fill: { color: HEX.callout }, line: { color: HEX.amber, width: 1 }, objectName: "lucky zone" });
s.addShape(pres.shapes.RECTANGLE, { x: L(-100), y: 1.55, w: L(1000) - L(-100), h: 0.55, fill: { color: HEX.band }, line: { color: HEX.blue, width: 1 }, objectName: "deserved zone" });
text(s, "lucky", { x: L(-1000), y: 1.55, w: L(-100) - L(-1000), h: 0.55, fontSize: F.label, bold: true, color: HEX.amber, align: "center", valign: "middle" });
text(s, "deserved", { x: L(-100), y: 1.55, w: L(1000) - L(-100), h: 0.55, fontSize: F.label, bold: true, color: HEX.navy, align: "center", valign: "middle" });
[-1000, -100, 0, 1000].forEach((v) => text(s, (v > 0 ? "+" : "") + v, { x: L(v) - 0.45, y: 2.15, w: 0.9, h: 0.3, fontSize: 13, color: HEX.gray, align: "center" }));
text(s, "winner's final score (cp)", { x: 3, y: 2.45, w: 4, h: 0.3, fontSize: 13, color: HEX.gray, align: "center" });
formula(s, "lucky  if  S_final < −100 cp     (S_final = engine score from the winner's side)", M, 3.0, W, 0.7, 17);
text(s, "Losing by more than a pawn when the clock ran out. Forced mates count as ±1000.", { x: M, y: 3.9, w: W, h: 0.8 });
s.addNotes("For every time win, the chess computer scored the final position from the winner's side. If the winner was more than one pawn behind, minus 100 centipawns or worse, the win counts as lucky. Otherwise it is deserved. We also ran a stricter version, losing by more than three pawns, as a check.");

s = slide();
title(s, "Each lucky win is compared with a deserved win from the same rating band and game speed");
table(s, [
  [th("Rating band"), th("Game speed"), th("Lucky pairs"), th("Deserved pairs")],
  ["1500–1599", "10 minutes", "1,513", "1,513"],
  ["1600–1699", "10 minutes", "1,446", "1,446"],
  ["1700–1799", "10 minutes", "1,431", "1,431"],
  ["1400–1499", "10 minutes", "1,353", "1,353"],
], { y: 1.3, colW: [2.4, 2.2, 2.2, 2.2], rowH: 0.42 });
text(s, "247 such slots in total. Matching stops stronger or faster players from crowding one group.", { x: M, y: 3.6, w: W, h: 0.9 });
cite(s, "Study 2 sample; the four largest slots shown. 58 deserved pairs could not be matched (0.45%).");
s.addNotes("To be fair, the two groups must contain similar players. So for every rating band and game speed, we took exactly as many deserved wins as lucky wins. If lucky winners were, say, weaker players, they would look worse for that reason alone. Matching removes that.");

s = slide();
title(s, "Every next game is scored with exactly the same computer settings");
table(s, [
  [th("Setting"), th("Value"), th("Why")],
  ["Engine", "Stockfish 16", "Strong, free, standard in research"],
  ["Search depth", "15 moves ahead", "Same effort for every position, reproducible"],
  ["Moves scored", "15 to 30", "Skips memorised openings (Backus et al., 2023)"],
  ["Score cap", "±1000 cp", "One missed mate cannot swamp a game"],
  ["Minimum", "5 scored moves", "Very short games are too noisy"],
], { y: 1.3, colW: [2.2, 2.6, 4.2], rowH: 0.48, fontSize: 15 });
cite(s, "42,851 next games scored; two separate runs on the same games gave identical numbers in study 1");
s.addNotes("Every game goes through the same machine with the same settings. A fixed depth means the computer thinks equally hard about every position, so anyone can rerun this and get the same numbers. We skip the first 14 moves because players often play memorised openings there.");

s = slide();
title(s, "A regression compares the groups while holding rating, opponent and colour fixed");
formula(s, "ACPL = β₀ + β₁·Lucky + β₂·Rating + β₃·Gap + β₄·White + speed + error", M, 1.3, W, 0.8, 17);
table(s, [
  [th("Term"), th("Estimate"), th("Plain meaning")],
  [{ text: "β₁ Lucky (1 if lucky, 0 if not)", options: { bold: true, color: HEX.amber } }, { text: "+1.96 cp", options: { bold: true, color: HEX.amber } }, "the effect we are testing"],
  ["β₂ per +100 rating", "−3.69 cp", "stronger players make smaller mistakes"],
  ["β₃ opponent +100 stronger", "+0.62 cp", "tougher opponents cause slightly more"],
  ["β₄ playing White", "−0.44 cp", "almost no difference"],
], { y: 2.3, colW: [3.4, 1.6, 4.0], rowH: 0.45, fontSize: 15 });
cite(s, "Ordinary least squares, standard errors clustered by player; 23,995 pairs");
s.addNotes("The regression is a line of best fit with several ingredients. It estimates how much each factor pushes ACPL up or down, separately. The one we care about is beta one: the extra mistakes after a lucky win, with rating, opponent strength and colour already accounted for. The other rows are sensible, which tells us the model works.");

s = slide();
title(s, "A confidence interval gives the range of believable values, and the p-value tests 'no effect'");
formula(s, "95% interval = estimate ± 1.96 × SE      90% interval = estimate ± 1.645 × SE", M, 1.3, W, 0.75, 17);
text(s, "Our numbers: 1.96 ± 1.96 × 0.666 = 0.66 to 3.27 cp", { x: M, y: 2.25, w: W, h: 0.45, bold: true, color: HEX.navy });
bullets(s, ["SE (standard error): how much the estimate would wobble with different games",
            "p-value 0.003: if lucky wins truly did nothing, a gap this big would appear 3 times in 1,000"],
  { x: M, y: 2.9, w: W, h: 2.1 });
s.addNotes("No estimate is exact. The standard error tells us how much it would change if we had picked different games. Multiply by 1.96 each way and you get the 95 percent confidence interval: the range of values the data can believe. The p-value asks: if lucky wins truly made no difference, how often would we see a gap this large by luck? Here, 3 times in a thousand.");

s = slide();
title(s, "The decision rule was fixed in advance: each result is supported, refuted or inconclusive");
const D = (v) => 2.2 + ((v + 4) / 8) * 6.8;
s.addShape(pres.shapes.RECTANGLE, { x: D(-2), y: 1.35, w: D(2) - D(-2), h: 2.35, fill: { color: HEX.band }, line: { color: HEX.band, width: 0 }, objectName: "zone" });
s.addShape(pres.shapes.LINE, { x: D(0), y: 1.3, w: 0, h: 2.45, line: { color: HEX.gray, width: 1, dashType: "dash" }, objectName: "zero" });
[["Supported", -1.1, 1.0, HEX.navy], ["Refuted", 2.4, 3.6, HEX.amber], ["Inconclusive", 0.4, 3.1, HEX.gray]].forEach(([lab, a, b, col], i) => {
  const cy = 1.65 + i * 0.8;
  text(s, lab, { x: M, y: cy - 0.2, w: 1.6, h: 0.4, fontSize: 15, bold: true, color: col, valign: "middle" });
  s.addShape(pres.shapes.LINE, { x: D(a), y: cy, w: D(b) - D(a), h: 0, line: { color: col, width: 3 }, objectName: "rule " + lab });
});
[-4, -2, 0, 2, 4].forEach((t) => text(s, (t > 0 ? "+" : "") + t, { x: D(t) - 0.3, y: 3.75, w: 0.6, h: 0.25, fontSize: 13, color: HEX.gray, align: "center" }));
bullets(s, ["Supported: whole 90% interval inside ±2 cp", "Refuted: 95% interval misses 0 and gap is at least 2 cp"],
  { x: M, y: 4.15, w: W, h: 1.0, fontSize: 17 });
s.addNotes("This is the rule written down before the study. If the whole interval sits inside the shaded zone of plus or minus 2 centipawns, the groups are equal for practical purposes, and the 'players reset' prediction is supported. If the interval is clear of zero and the gap is at least 2, the prediction is refuted. Anything else is inconclusive. This test of 'equal within a margin' is called an equivalence test, or TOST.");

s = slide();
title(s, "About 10,700 pairs per group were needed, so we planned 13,000 to allow for losses");
formula(s, "n = 2 × σ² × (z₁ + z₂)² ÷ Δ²", M, 1.3, W, 0.75);
table(s, [
  [th("Symbol"), th("Value"), th("Meaning")],
  ["σ", "50 cp", "spread of ACPL between games (from study 1)"],
  ["z₁ , z₂", "1.645 , 1.282", "set by 5% error rate and 80% power"],
  ["Δ", "2 cp", "smallest difference we decided matters"],
  [{ text: "n", options: { bold: true } }, { text: "≈ 10,700", options: { bold: true } }, "pairs per group needed"],
], { y: 2.25, colW: [1.6, 2.4, 5.0], rowH: 0.42, fontSize: 15 });
s.addNotes("Before scoring, we worked out how many games were needed. Games vary a lot, by about 50 centipawns, so to pin down a 2 centipawn difference we need a lot of them: about 10,700 per group. We planned 13,000 because some games end too early to score. We ended with about 12,000 usable per group.");

// ================= Part 4 =================
SEC = section("Part 4", "Results", "Now what happened.");

s = slide();
title(s, "Lucky winners made 1.96 cp more mistakes per move in their next game (p = 0.003)");
ciPlot(s, [
  { label: "Lucky minus deserved, 90% interval", est: 1.96, ci: [0.87, 3.06], highlight: true },
  { label: "Lucky minus deserved, 95% interval", est: 1.96, ci: [0.66, 3.27] },
], { x: M, y: 1.5, w: 5.1, rowH: 0.9, labelW: 2.1, lo: -4, hi: 4, ticks: [-4, -2, 0, 2, 4], band: 2, unit: "cp",
     axisTitle: "Difference in next-game ACPL, cp" });
text(s, "What it means", { x: 6.2, y: 1.35, w: 3.3, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
bullets(s, ["Not chance: p = 0.003", "Not equal: it leaves the ±2 zone", "Official verdict: inconclusive, as 1.96 < 2"], { x: 6.2, y: 1.85, w: 3.3, h: 3.0 });
cite(s, "Raw means: 74.38 cp after a lucky win, 72.28 after a deserved win; 12,033 and 11,962 pairs");
s.addNotes("Here is the main result. After a lucky win, players lost 1.96 more centipawns per move. The 90 percent interval pokes out of the plus or minus 2 zone, so we cannot say the groups are equal, and the 'players reset' prediction is not supported. But the rule needed at least 2 centipawns to call it refuted, and 1.96 falls short by 0.04. So the official verdict is inconclusive, right on the line. In rating terms, 1.96 centipawns is about the gap between players 53 points apart.");

s = slide();
title(s, "Every check gives the same answer: lucky winners play 1.8 to 2.3 cp worse");
ciPlot(s, [
  { label: "Main result", est: 1.96, ci: [0.66, 3.27], highlight: true },
  { label: "10-minute games only", est: 2.29, ci: [0.82, 3.76] },
  { label: "Rematches removed", est: 1.85, ci: [0.53, 3.18] },
  { label: "Rating 1200–1600", est: 1.82, ci: [-0.17, 3.80] },
  { label: "Rating 1600–2000", est: 2.12, ci: [0.46, 3.78] },
  { label: "Lucky = losing by 3+ pawns", est: 1.92, ci: [0.51, 3.33] },
], { x: M, y: 1.3, w: 6.6, rowH: 0.47, labelW: 2.6, lo: -2, hi: 5, ticks: [-2, 0, 2, 4], unit: "cp",
     axisTitle: "Lucky minus deserved, cp (95% interval)" });
text(s, "Why checks", { x: 7.4, y: 1.3, w: 2.1, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
text(s, "A real effect should survive changes to the method.", { x: 7.4, y: 1.8, w: 2.1, h: 2.2 });
cite(s, "A mixed model with a separate starting level per player also gave 1.96 cp (95% interval 0.66 to 3.27)");
s.addNotes("We fixed five checks in advance, each changing one choice: only 10-minute games, removing rematches against the same opponent, each rating band separately, and a stricter definition of lucky. Every one points the same way, between 1.8 and 2.3 centipawns. One band's interval just touches zero because it has half the data.");

s = slide();
title(s, "The type of win itself still barely matters: every gap stayed within about 3 cp");
ciPlot(s, [
  { label: "Time minus checkmate", est: -0.54, ci: [-2.09, 1.01] },
  { label: "Resignation minus checkmate", est: 0.97, ci: [-0.60, 2.54] },
  { label: "Time minus resignation", est: -1.51, ci: [-3.05, 0.03], highlight: true },
], { x: M, y: 1.45, w: 5.9, rowH: 0.72, labelW: 2.4, lo: -4, hi: 4, ticks: [-4, -2, 0, 2, 4], band: 3, unit: "cp",
     axisTitle: "Difference in next-game ACPL, cp (90% interval)" });
text(s, "Verdict: inconclusive", { x: 6.6, y: 1.35, w: 2.9, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
bullets(s, ["No gap was significant (p = 0.26)", "One interval misses the zone by 0.05 cp"], { x: 6.6, y: 1.85, w: 2.9, h: 3.0 });
cite(s, "About 6,000 pairs per group after a win on time, by checkmate and by resignation; Holm-corrected tests");
s.addNotes("The repeat of study 1's question. None of the differences between time, checkmate and resignation wins was significant. Two comparisons were inside the plus or minus 3 zone; the third missed it by five hundredths of a centipawn. So formally inconclusive, but in practice the same story as study 1: the type of win matters very little.");

s = slide();
title(s, "Two separate studies on different games point the same way");
ciPlot(s, [
  { label: "Study 1: lucky vs checkmate (unplanned, n = 1,288)", est: 2.23, ci: [-0.83, 5.28] },
  { label: "Study 2: lucky vs deserved (planned, n = 12,033)", est: 1.96, ci: [0.66, 3.27], highlight: true },
], { x: M, y: 1.6, w: 6.4, rowH: 0.95, labelW: 3.0, lo: -2, hi: 6, ticks: [-2, 0, 2, 4, 6], unit: "cp",
     axisTitle: "Extra next-game mistakes after a lucky win, cp (95% interval)" });
text(s, "9× more data", { x: 7.2, y: 1.45, w: 2.3, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
text(s, "Same direction, similar size, much tighter interval.", { x: 7.2, y: 2.0, w: 2.3, h: 2.2 });
cite(s, "Study 1: 1 to 5 Aug and 1 to 5 Sep 2026. Study 2: 6 to 30 Sep 2026. No game appears in both.");
s.addNotes("Study 1's hint and study 2's planned test used completely different games and found almost the same number: 2.2 and 1.96. Study 2's interval is much narrower because it had nine times as many lucky wins. When an unplanned hint comes back in a planned test, that is how science is supposed to work.");

// ================= Part 5 =================
SEC = section("Part 5", "What it means", "Finally, what the result means and what it cannot tell us.");

s = slide();
title(s, "An undeserved win leaves a small after-effect, worth about 53 rating points");
text(s, "What we can say", { x: M, y: 1.3, w: 4.3, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
bullets(s, ["Lucky winners play slightly worse next game", "The effect is consistent, not chance", "It sits on our 'matters' threshold"], { x: M, y: 1.8, w: 4.3, h: 3.0 });
text(s, "What we cannot say", { x: 5.2, y: 1.3, w: 4.3, h: 0.4, fontSize: F.header, bold: true, color: HEX.amber });
bullets(s, ["Why it happens", "Anything about blitz or bullet", "Anything beyond moves 15–30"], { x: 5.2, y: 1.8, w: 4.3, h: 3.0 });
cite(s, "Other limits: one month of data; ratings 1200–2000; run before teacher approval of the plan");
s.addNotes("What this means: escaping with an undeserved win seems to leave a small mark on the next game, roughly what you would expect from a player about 53 rating points weaker. What it does not tell us: why. It could be adrenaline, overconfidence or something else. And we only looked at rapid games and the middle part of each game.");

pres.addSection({ title: "Conclusions" });
s = pres.addSlide({ masterName: "CLOSE_DARK", sectionTitle: "Conclusions" });
s.addText("Conclusions", { placeholder: "title" });
text(s, [
  { text: "1. Lucky time winners played worse next game: ", options: { bold: true, breakLine: false } },
  { text: "+1.96 cp per move (p = 0.003), about 53 rating points.", options: { breakLine: true } },
  { text: "2. 'Players reset' was not supported, ", options: { bold: true, breakLine: false } },
  { text: "but the result sits 0.04 cp short of the planned 'refuted' bar.", options: { breakLine: true } },
  { text: "3. How you win barely matters; whether you deserved it might.", options: { bold: true } },
], { x: M, y: 0.95, w: W, h: 3.4, fontSize: F.body, color: C.background1, paraSpaceAfter: 18 });
text(s, "Code, data and both preregistrations: github.com/KaranaGulati/ContinuedLearningResearch", { x: M, y: 4.8, w: W, h: 0.4, fontSize: 14, color: HEX.light });
s.addNotes("To sum up. Lucky winners played slightly but clearly worse in their next game. My prediction that players reset was not supported, though the effect landed just under the size we decided in advance would count. Across both studies, how you win barely matters, but whether you deserved the win might. Questions and feedback welcome.");

// ================= Backup =================
pres.addSection({ title: "Backup" });
SEC = "Backup";
s = slide();
title(s, "References");
const refs = [
  "Backus, Cubel, Guid, Sanchez-Pages & Lopez Manas (2023). Quantitative Economics, 14(1), 349-380.",
  "Chowdhary, Iacopini & Battiston (2023). Scientific Reports, 13, 2113.",
  "Gee, Seese, Curley & Ward (2025). Journal of Quantitative Analysis in Sports, 22(2), 117-132. Preprint arXiv:2503.21713.",
  "Guid & Bratko (2006). Computer analysis of world chess champions. ICGA Journal, 29(2), 65-73.",
  "Lichess open database (2026). database.lichess.org, CC0.",
  "Karana Gulati (2026). Study 1 and study 2 preregistrations and results. github.com/KaranaGulati/ContinuedLearningResearch.",
];
text(s, refs.map((r, i) => ({ text: r, options: { breakLine: i < refs.length - 1 } })), { x: M, y: 1.3, w: W, h: 3.7, fontSize: 14, paraSpaceAfter: 10 });
s.addNotes("Backup slide, not presented.");

s = slide();
title(s, "Appendix: glossary of every term used");
table(s, [
  [th("Term"), th("Meaning")],
  ["Centipawn (cp)", "1/100 of a pawn; the unit of a chess computer's score"],
  ["ACPL", "average score lost per move; lower is better"],
  ["Lucky time win", "won on time while losing by more than 1 pawn"],
  ["Regression", "line of best fit that separates several effects"],
  ["Standard error (SE)", "how much an estimate would wobble with other games"],
  ["Confidence interval", "range of values the data can believe"],
  ["p-value", "how often a gap this big appears if there is no real effect"],
  ["Equivalence test (TOST)", "checks a difference is inside a 'too small to matter' zone"],
  ["Preregistration", "the plan, dated and saved before scoring the data"],
], { y: 1.2, colW: [2.7, 6.3], rowH: 0.36, fontSize: 13 });
s.addNotes("Backup slide: definitions for every technical term in the deck.");

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
