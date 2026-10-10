const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/2a801b73-387a-4a8f-a933-cd1229816463_1e1899ee-efee-4430-b963-be75ebe16f62/pptx/scripts/apply_theme.js");

const OUT = process.argv[2] || "proposal-presentation.pptx";

const THEME = {
  name: "Chess Research",
  headFontFace: "Arial",
  bodyFontFace: "Arial",
  colors: {
    dk1: "2D2D2D", lt1: "FFFFFF", dk2: "1F4E79", lt2: "EBF3FA",
    accent1: "2E75B6", accent2: "1F4E79", accent3: "C27C0E",
    accent4: "777777", accent5: "A0BBDD", accent6: "FFF2CC",
    hlink: "2E75B6", folHlink: "1F4E79",
  },
};
const HEX = { navy: "1F4E79", blue: "2E75B6", amber: "C27C0E", gray: "777777", grid: "D9D9D9",
              band: "EBF3FA", body: "2D2D2D", light: "A0BBDD", callout: "FFF2CC" };

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Does how you win change how you play next?";
pres.author = "Karana Gulati";
const C = pres.SchemeColor;

const M = 0.5;
const W = 10 - 2 * M;
const F = { title: 26, header: 20, body: 20, label: 16, cite: 12 };

pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: HEX.navy },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 1.2, w: 8.6, h: 1.7,
        fontSize: 34, bold: true, color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.7, y: 3.1, w: 8.6, h: 1.2,
        fontSize: 18, color: C.accent5, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: "FFFFFF" },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.25, w: W, h: 0.9,
        fontSize: F.title, bold: true, color: C.text2, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 9.1, y: 5.2, w: 0.5, h: 0.3, fontSize: 11, color: HEX.gray, fontFace: "Arial" },
});
pres.defineSlideMaster({
  title: "CLOSE_DARK",
  background: { color: HEX.navy },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.3, w: W, h: 0.5,
        fontSize: 20, bold: false, color: C.accent5, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});

const nb = (t) => typeof t === "string" ? t.replace(/(\d) cp/g, "$1\u00A0cp") : t.map((r) => ({ ...r, text: nb(r.text) }));
function text(slide, t, o) {
  t = nb(t);
  slide.addText(t, Object.assign({ isTextBox: true, fontFace: "Arial", color: C.text1, valign: "top", margin: 0 }, o));
}
function cite(slide, t) {
  text(slide, t, { x: M, y: 5.15, w: 8.4, h: 0.3, fontSize: F.cite, color: HEX.gray, valign: "middle" });
}

// Horizontal confidence-interval plot drawn with native shapes.
function ciPlot(slide, rows, o) {
  const { x, y, w, rowH, labelW, lo, hi, ticks, band, unit } = o;
  const px0 = x + labelW, pw = w - labelW;
  const X = (v) => px0 + ((v - lo) / (hi - lo)) * pw;
  const plotH = rows.length * rowH;
  if (band) {
    slide.addShape(pres.shapes.RECTANGLE, { x: X(-band), y, w: X(band) - X(-band), h: plotH,
      fill: { color: HEX.band }, line: { color: HEX.band, width: 0 }, objectName: "equivalence band" });
    text(slide, `equivalence zone ±${band} ${unit}`, { x: X(-band), y: y + plotH + 0.38, w: X(band) - X(-band), h: 0.3,
      fontSize: 13, color: HEX.blue, align: "center" });
  }
  slide.addShape(pres.shapes.LINE, { x: X(0), y: y - 0.05, w: 0, h: plotH + 0.1,
    line: { color: HEX.gray, width: 1, dashType: "dash" }, objectName: "zero line" });
  rows.forEach((r, i) => {
    const cy = y + i * rowH + rowH / 2;
    const col = r.highlight ? HEX.amber : HEX.navy;
    text(slide, r.label, { x, y: cy - 0.2, w: labelW - 0.15, h: 0.4, fontSize: F.label, valign: "middle",
      color: r.highlight ? HEX.amber : C.text1, bold: !!r.highlight });
    slide.addShape(pres.shapes.LINE, { x: X(r.ci[0]), y: cy, w: X(r.ci[1]) - X(r.ci[0]), h: 0,
      line: { color: col, width: 2.5 }, objectName: `ci ${r.label}` });
    slide.addShape(pres.shapes.OVAL, { x: X(r.est) - 0.08, y: cy - 0.08, w: 0.16, h: 0.16,
      fill: { color: col }, line: { color: col, width: 0 }, objectName: `estimate ${r.label}` });
    text(slide, `${r.est > 0 ? "+" : ""}${r.est.toFixed(2)}`, { x: X(r.ci[1]) + 0.08, y: cy - 0.14, w: 0.6, h: 0.28,
      fontSize: 13, color: col, align: "left", bold: true, valign: "middle" });
  });
  const axisY = y + plotH + 0.05;
  slide.addShape(pres.shapes.LINE, { x: px0, y: axisY, w: pw, h: 0, line: { color: HEX.gray, width: 1 }, objectName: "axis" });
  ticks.forEach((t) => text(slide, `${t > 0 ? "+" : ""}${t}`, { x: X(t) - 0.3, y: axisY + 0.04, w: 0.6, h: 0.25,
    fontSize: 13, color: HEX.gray, align: "center" }));
  text(slide, o.axisTitle, { x: px0, y: axisY + 0.62, w: pw, h: 0.28, fontSize: 13, color: HEX.gray, align: "center" });
}

function bullets(slide, items, o) {
  const runs = items.map((t, i) => ({ text: nb(t), options: { bullet: true, breakLine: i < items.length - 1 } }));
  slide.addText(runs, Object.assign({ isTextBox: true, fontFace: "Arial", fontSize: F.body, color: C.text1,
    valign: "top", paraSpaceAfter: 10, margin: 0 }, o));
}

// ---------- 1. Title ----------
pres.addSection({ title: "Introduction" });
let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Introduction" });
s.addText(nb("Does how you win change how you play next?"), { placeholder: "title" });
s.addText([
  { text: "Evidence from 18,002 online chess games, and a proposal to test undeserved wins", options: { breakLine: true } },
  { text: " ", options: { breakLine: true } },
  { text: "Karana Gulati  ·  October 2026", options: { color: HEX.light } },
], { placeholder: "body" });
s.addNotes("This talk has two parts. First, a study I have already run on how the way you win a chess game affects your next game. Second, a proposal for a sharper follow-up study, which is what I would like approval for.");

// ---------- 2. Win types ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Introduction" });
s.addText(nb("Wins on time, by checkmate and by resignation count the same, but they are different events"), { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Share of decisive rapid games", labels: ["On time", "Checkmate", "Resignation"], values: [11.4, 30.0, 58.6] }], {
  x: M, y: 1.3, w: 5.2, h: 3.6, barDir: "col",
  chartColors: [HEX.amber, HEX.blue, HEX.blue],
  showValue: true, dataLabelFormatCode: '0"%"', dataLabelPosition: "outEnd", dataLabelColor: HEX.body, dataLabelFontSize: F.label,
  dataLabelFontFace: "+mn-lt", catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt",
  catAxisLabelColor: HEX.body, catAxisLabelFontSize: F.label, valAxisHidden: true,
  valGridLine: { style: "none" }, catGridLine: { style: "none" }, valAxisMaxVal: 70, valAxisMinVal: 0,
  showLegend: false, showTitle: true, title: "Share of decisive rapid games (%)", titleFontSize: 14, titleColor: HEX.gray,
});
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.0, y: 1.5, w: 3.5, h: 1.75, fill: { color: HEX.callout },
  line: { color: HEX.amber, width: 1 }, rectRadius: 0.08, objectName: "callout lucky" });
text(s, [
  { text: "21%", options: { fontSize: 36, bold: true, color: HEX.amber, breakLine: true } },
  { text: "of winners on time were losing on the board when the clock ran out", options: { fontSize: F.label } },
], { x: 6.2, y: 1.62, w: 3.1, h: 1.55 });
text(s, "A win on time can be a lucky escape. Checkmate never is.", { x: 6.0, y: 3.5, w: 3.5, h: 1.2, fontSize: F.body });
cite(s, "Lichess rated rapid. Shares: first 2M games of Sep 2026. 21%: 6,500 time wins from study 1, final positions scored with Stockfish 16");
s.addNotes("On a player's profile all three kinds of win look identical. But about one win in nine comes on time, and in one in five of those, Stockfish says the winner was actually losing on the board when the opponent's clock ran out. That is a very different experience from delivering checkmate.");

// ---------- 3. Literature gap ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Introduction" });
s.addText(nb("Earlier studies looked at results after a win, but never split wins by type or measured move quality"), { placeholder: "title" });
const th = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: HEX.navy } } });
s.addTable([
  [th("Study"), th("What it measured"), th("Splits kinds of win?")],
  ["Gee et al. (2025)", "Chance of winning the next game", "No"],
  ["Chowdhary et al. (2023)", "Streaks of wins and losses", "No"],
  [{ text: "This project", options: { bold: true, color: HEX.amber } }, { text: "Engine-measured move quality in the next game", options: { bold: true } }, { text: "Yes", options: { bold: true, color: HEX.amber } }],
], { x: M, y: 1.35, w: W, colW: [2.6, 4.4, 2.0], fontFace: "Arial", fontSize: F.label, color: HEX.body,
  border: { type: "solid", pt: 0.75, color: HEX.grid }, rowH: 0.55, valign: "middle", margin: 0.08 });
text(s, "Gee et al. found next-game effects between -0.02 and 0.03, and named wins on time as an open question.",
  { x: M, y: 4.1, w: W, h: 0.9, fontSize: F.body });
cite(s, "Gee, Seese, Curley & Ward (2025), arXiv:2503.21713; Chowdhary, Iacopini & Battiston (2023), Sci. Rep. 13:2113");
s.addNotes("Two recent studies are closest. Gee and colleagues found almost no winner effect on the chance of winning the next game, and in their own future-work section they point out that wins on time might affect later play differently. Chowdhary and colleagues found that wins and losses come in streaks. Neither looked at how well the next game was actually played, or separated the kinds of win.");

// ---------- 4. Study 1 result ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Introduction" });
s.addText(nb("Study 1: across 18,002 games, win type changed next-game accuracy by under 1 cp"), { placeholder: "title" });
ciPlot(s, [
  { label: "Time minus checkmate", est: 0.88, ci: [-0.62, 2.38] },
  { label: "Resignation minus checkmate", est: 0.56, ci: [-0.95, 2.07] },
  { label: "Time minus resignation", est: 0.31, ci: [-1.18, 1.81] },
], { x: M, y: 1.55, w: 5.6, rowH: 0.72, labelW: 2.3, lo: -4, hi: 4, ticks: [-4, -2, 0, 2, 4], band: 3, unit: "cp",
     axisTitle: "Adjusted difference in next-game ACPL, cp (90% CI)" });
text(s, "What to take away", { x: 6.45, y: 1.35, w: 3.05, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
bullets(s, ["All three intervals sit inside ±3 cp", "Largest gap ≈ 1% of typical loss", "Preregistered prediction supported"],
  { x: 6.45, y: 1.85, w: 3.05, h: 2.9 });
cite(s, "Lichess rated rapid, 1–5 Aug and 1–5 Sep 2026; Stockfish 16, depth 15, moves 15–30; ACPL = average centipawn loss");
s.addNotes("I compared about six thousand next games after each kind of win, matched on rating and time control, and adjusted for opponent strength and colour. Every difference is under one centipawn, which is a hundredth of a pawn per move. All three confidence intervals sit inside the plus or minus 3 centipawn zone I fixed in advance, so the preregistered prediction, that a win is a win, is supported. None of the seven robustness checks found a significant difference.");

// ---------- 5. Exploratory hint ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Introduction" });
s.addText(nb("Exploratory hint: winners who were losing on the board played 2.2 cp worse in their next game"), { placeholder: "title" });
ciPlot(s, [
  { label: "Resignation", est: 0.56, ci: [-1.23, 2.36] },
  { label: "Time, winner not losing", est: 0.51, ci: [-1.38, 2.40] },
  { label: "Time, winner losing (n = 1,288)", est: 2.23, ci: [-0.83, 5.28], highlight: true },
], { x: M, y: 1.55, w: 5.6, rowH: 0.72, labelW: 2.3, lo: -2, hi: 6, ticks: [-2, 0, 2, 4, 6],
     axisTitle: "Difference from checkmate in next-game ACPL, cp (95% CI)" });
text(s, "Why it matters", { x: 6.45, y: 1.35, w: 3.05, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
bullets(s, ["Not significant: p\u00A0=\u00A00.15", "Found after looking, so not evidence", "Needs its own preregistered test"],
  { x: 6.45, y: 1.85, w: 3.05, h: 2.9 });
cite(s, "Same sample as study 1; split into lucky and not-lucky time wins after the main analysis (exploratory)");
s.addNotes("After the main analysis I split the time wins by whether the winner was losing on the board. The lucky winners played about 2.2 centipawns worse next game. But the interval includes zero, the group is small, and I only looked because of the main result. So this is a hint, not a finding, and it needs a proper test on fresh data.");

// ---------- 6. Research questions ----------
pres.addSection({ title: "Research questions" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Research questions" });
s.addText(nb("The proposed study asks whether study 1 holds at full scale, and whether an undeserved win matters"), { placeholder: "title" });
function rqBox(x, tag, q, h) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.4, w: 4.35, h: 2.9, fill: { color: HEX.band },
    line: { color: HEX.blue, width: 1.25 }, rectRadius: 0.08, objectName: `${tag} box` });
  text(s, tag, { x: x + 0.25, y: 1.55, w: 3.9, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
  text(s, q, { x: x + 0.25, y: 2.05, w: 3.9, h: 1.3, fontSize: F.body, color: C.text2 });
  text(s, h, { x: x + 0.25, y: 3.0, w: 3.9, h: 1.6, fontSize: F.body, color: C.text1 });
}
rqBox(M, "RQ1", "Does the type of win change next-game accuracy?", "H1: No. Every difference within ±3 cp (replication of study 1).");
rqBox(5.15, "RQ2", "Does an undeserved win change the next game?", "H2: Lucky time winners play worse than deserved time winners. Tested two-tailed.");
s.addNotes("Two questions. The first repeats study 1 on new data, to see whether the null result replicates. The second is new: compare winners on time who were losing on the board with winners on time who were not. I predict the lucky ones play worse, based on the hint, but the test is two-tailed, so better play would also be detected and reported.");

// ---------- 7. Data pipeline ----------
pres.addSection({ title: "Methods" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Methods" });
s.addText(nb("Data: about 157 million new Lichess games, turned into win-then-next-game pairs"), { placeholder: "title" });
const steps = [
  ["Download", "Lichess, Aug + Sep 2026, days 6–31"],
  ["Filter", "rated rapid, Elo 1200 to 2000, no bots"],
  ["Pair", "win → same player's next game within 30\u00A0min"],
  ["Classify", "time / mate / resign; lucky if losing at end"],
  ["Score", "Stockfish 16, depth 15, moves 15–30"],
];
const bw = 1.62, gap = 0.215;
steps.forEach(([h, d], i) => {
  const x = M + i * (bw + gap);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: bw, h: 2.05, fill: { color: i === 3 ? HEX.callout : HEX.band },
    line: { color: i === 3 ? HEX.amber : HEX.blue, width: 1 }, rectRadius: 0.06, objectName: `step ${h}` });
  text(s, h, { x: x + 0.1, y: 1.68, w: bw - 0.2, h: 0.4, fontSize: F.label, bold: true, color: i === 3 ? HEX.amber : HEX.navy });
  text(s, d, { x: x + 0.1, y: 2.12, w: bw - 0.2, h: 1.35, fontSize: F.label, color: C.text1 });
  if (i < steps.length - 1)
    s.addShape(pres.shapes.RIGHT_ARROW, { x: x + bw + 0.02, y: 2.42, w: 0.18, h: 0.2, fill: { color: HEX.gray },
      line: { color: HEX.gray, width: 0 }, objectName: `arrow ${i}` });
});
text(s, "Days 1–5 of each month are left out: study 1 already used them, so this is an independent test.",
  { x: M, y: 3.85, w: W, h: 0.8, fontSize: F.body });
cite(s, "Lichess open database (CC0), database.lichess.org; method follows Backus et al. (2023)");
s.addNotes("The pipeline is already built and tested from study 1. The main change is the data: the rest of August and September 2026, leaving out the nine days study 1 used, so the new study is fully independent. For the lucky-escape test, Stockfish also scores the final position of every winning game, to see whether the winner was losing when the clock ran out.");

// ---------- 8. Groups ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Methods" });
s.addText(nb("Lucky and deserved time wins differ only in who was winning on the board when the clock ran out"), { placeholder: "title" });
s.addTable([
  [th("Group"), th("Definition"), th("Pairs")],
  [{ text: "Lucky time win", options: { bold: true, color: HEX.amber } }, "Won on time while losing by more than 1 pawn", "13,000"],
  ["Deserved time win", "Won on time, not losing at the end", "13,000"],
  ["Checkmate", "Won by checkmate", "6,500"],
  ["Resignation", "Opponent resigned", "6,500"],
], { x: M, y: 1.35, w: W, colW: [2.6, 4.9, 1.5], fontFace: "Arial", fontSize: F.label, color: HEX.body,
  border: { type: "solid", pt: 0.75, color: HEX.grid }, rowH: 0.5, valign: "middle", margin: 0.08 });
text(s, "All groups matched to the same mix of rating and time control, one pair per player per group.",
  { x: M, y: 4.15, w: W, h: 0.8, fontSize: F.body });
s.addNotes("The key comparison is lucky against deserved time wins. Both are wins on time, so the clock situation is the same, and the only difference is whether the winner deserved it. Checkmate and resignation stay in as reference groups for RQ1. Every group is drawn to have the same mix of ratings and time controls, so skill differences cannot explain a gap.");

// ---------- 9. Analysis ----------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Methods" });
s.addText(nb("Analysis is fixed before scoring: regression with equivalence tests, sized to detect 2 cp"), { placeholder: "title" });
text(s, "Model", { x: M, y: 1.35, w: 4.3, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
bullets(s, ["Next-game ACPL by group", "Adjusted: rating, opponent, colour, time control", "Errors clustered by player"],
  { x: M, y: 1.85, w: 4.3, h: 2.2 });
text(s, "Decision rules", { x: 5.2, y: 1.35, w: 4.3, h: 0.4, fontSize: F.header, bold: true, color: HEX.blue });
bullets(s, ["H1: all 90% CIs within ±3 cp", "H2: two-tailed, α = 0.05", "Preregistered before any scoring"],
  { x: 5.2, y: 1.85, w: 4.3, h: 2.2 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 4.15, w: W, h: 0.75, fill: { color: HEX.callout },
  line: { color: HEX.amber, width: 1 }, rectRadius: 0.06, objectName: "power callout" });
text(s, "13,000 pairs per group: 80% power for a 2 cp gap  ·  about 9.5 h of Stockfish",
  { x: M + 0.2, y: 4.15, w: W - 0.4, h: 0.75, fontSize: F.label, bold: true, color: HEX.amber, valign: "middle" });
s.addNotes("The analysis is the same as study 1: a regression that compares groups while holding rating, opponent strength, colour and time control fixed. Both hypotheses and the decision rules will be written down and committed before any game is scored. The noise level measured in study 1 says 13,000 pairs per group are needed to detect a 2 centipawn difference, which is about nine and a half hours of engine time.");

// ---------- 10. Expected outcomes ----------
pres.addSection({ title: "Expected results" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Expected results" });
s.addText(nb("Every outcome of the lucky-escape test tells us something new about how players handle luck"), { placeholder: "title" });
s.addTable([
  [th("If lucky winners…"), th("It would mean")],
  [{ text: "play worse", options: { bold: true, color: HEX.amber } }, "An undeserved win disrupts the next game"],
  [{ text: "play better", options: { bold: true } }, "A near-loss makes players more careful"],
  [{ text: "play the same", options: { bold: true } }, "Players reset after every game, however they won"],
], { x: M, y: 1.35, w: W, colW: [3.0, 6.0], fontFace: "Arial", fontSize: F.body - 2, color: HEX.body,
  border: { type: "solid", pt: 0.75, color: HEX.grid }, rowH: 0.6, valign: "middle", margin: 0.08 });
text(s, "First test of whether deserving a win matters, using engine-measured move quality on a large sample.",
  { x: M, y: 4.05, w: W, h: 0.85, fontSize: F.body });
s.addNotes("This is a test where every outcome is useful. If lucky winners play worse, luck has an after-effect. If they play better, a near-loss sharpens players. If there is no difference, the most intuitive story about lucky wins is ruled out on a large sample. For RQ1, study 1 suggests the null result should replicate.");

// ---------- 11. Conclusions ----------
pres.addSection({ title: "Conclusions" });
s = pres.addSlide({ masterName: "CLOSE_DARK", sectionTitle: "Conclusions" });
s.addText(nb("Conclusions"), { placeholder: "title" });
text(s, [
  { text: "1. A win is a win: ", options: { bold: true, breakLine: false } },
  { text: "win type changed next-game accuracy by under 1 cp (18,002 games).", options: { breakLine: true } },
  { text: "2. Luck is the open question: ", options: { bold: true, breakLine: false } },
  { text: "undeserved time wins showed a 2.2 cp hint.", options: { breakLine: true } },
  { text: "3. The proposal: ", options: { bold: true, breakLine: false } },
  { text: "157M fresh games, four matched groups, about 2 days of computing after approval.", options: {} },
], { x: M, y: 0.95, w: W, h: 3.4, fontSize: F.body + 1, color: C.background1, paraSpaceAfter: 18 });
text(s, "Code, data pipeline and preregistration: github.com/KaranaGulati/ContinuedLearningResearch",
  { x: M, y: 4.8, w: W, h: 0.4, fontSize: 14, color: HEX.light });
s.addNotes("To sum up: the first study found that the way you win does not change how accurately you play next. The open question is luck, and I have a plan to test it properly on fresh data. I would like approval to go ahead. Questions and feedback welcome.");

// ---------- 12. References ----------
pres.addSection({ title: "Backup" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Backup" });
s.addText(nb("References"), { placeholder: "title" });
const refs = [
  "Backus, Cubel, Guid, Sanchez-Pages & Lopez Manas (2023). Quantitative Economics, 14(1).",
  "Chowdhary, Iacopini & Battiston (2023). Scientific Reports, 13, 2113.",
  "Gee, Seese, Curley & Ward (2025). arXiv:2503.21713.",
  "Guid & Bratko (2006). ICGA Journal.",
  "Lichess open database (2026). database.lichess.org, CC0.",
];
text(s, refs.map((r, i) => ({ text: r, options: { breakLine: i < refs.length - 1 } })),
  { x: M, y: 1.3, w: W, h: 3.6, fontSize: 14, color: C.text1, paraSpaceAfter: 12 });
s.addNotes("Backup slide, not presented.");

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
