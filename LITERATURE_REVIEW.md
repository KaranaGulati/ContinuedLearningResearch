# Literature review

Checked 13 October 2026. This file does two things. First, it checks every source the project has cited so far (in `README.md`, `the research explained.md`, the results summaries and both slide decks) against the source's own text. Second, it sets out the literature the two studies sit in, in more detail than the README did.

## How it was checked

Each source was downloaded and read in the original: the PDF, the publisher's full text on Europe PMC, or the page itself. Every factual statement below has an exact supporting passage in a claims ledger, and a script confirmed that each passage appears word for word in the downloaded text. Nothing here comes from search-result snippets or from memory. Bibliographic details (volume, issue, pages) come from the Crossref record for each DOI. Where only a working-paper or preprint version could be read, the review says so.

Where a source reports another study's finding, that finding is attributed to the original study with "as cited by", and the original was not read.

## Verdicts on what we have cited so far

| Our claim (where) | Verdict | What the source says |
|---|---|---|
| Gee, Seese, Curley and Ward fitted a hierarchical Bayesian model to Lichess games and found little evidence of winner-loser effects, with player-level effects on next-game win probability from -0.02 to 0.03 and most intervals containing zero (README, research explained, decks) | Verified | "range from -0.02 to 0.03. The majority of 95% posterior intervals contain 0" |
| Extending the history from one game to ten changed nothing (README) | Verified | "It does not appear that a longer term history provides additional evidence for the presence of strong or persistent experiential effects" |
| They did not separate winner and loser effects or let them differ in size (README) | Verified | "not attempted to separate out winner and loser effects or allow them to have different magnitudes" |
| 24% of bullet games in their grandmaster cohort were won on time, and such wins may affect later play differently (README, research explained, proposal deck) | Verified | "(24% of bullet games in the GM cohort) and results of this form may have a different impact on future performance than other endings" |
| Gee et al. (2025), arXiv:2503.21713 (all references) | Corrected | Now published: Journal of Quantitative Analysis in Sports 22(2), 117-132. The journal text keeps every statement above. |
| Chowdhary, Iacopini and Battiston found wins and losses cluster more than chance against a within-player shuffle null, with cold streaks longer than hot ones (README) | Verified | The null "shuffles the temporal order of the player's games"; they found "statistically significant hot streaks", and cold streaks "typically longer than hot ones" |
| Their outcome is the win or loss itself, measured on blitz games and openings only (README) | Corrected | Blitz is right: "restricted to Blitz games" from 2013 to 2016. "Openings only" is not. That limitation applies to their analysis of skill differences, not to the streaks, which use all blitz results. |
| Scientific Reports 13:2113 (2023) | Verified | Crossref: volume 13, article 2113. An author correction (13:4787) fixed swapped axis labels in Figure 2b and does not touch the streak results. |
| Moves 15 to 30 "is Backus et al.'s convention" (README) | Corrected | Backus et al. use moves 15 to 30, but they took the window from Guid and Bratko: "Following Guid and Bratko (2006, 2011), we base our quality of play variable on the analysis of moves n = 15, ..., 30". |
| Backus et al. used Houdini 1.5a at depth 15 and found a mean error of 16.5 (README, research explained) | Verified | "Houdini 1.5a x64", "a search depth of 15", "mean error of 16.5 (17.3 for opponents)". Their games were over-the-board tournament games, which matters when comparing numbers (see below). |
| Backus et al. (2023), Quantitative Economics 14(1) | Verified | Pages 349-380 added. |
| Kuenn, Seel and Zegners used Stockfish 11 at depth 25 and drop the first 15 moves "as in Backus et al." (README) | Verified | Checked in the IZA discussion paper: "We restrict Stockfish 11 to a search depth of 25 moves ahead" and the first 15 moves are removed "as in Backus et al., 2016" (the working-paper version of Backus et al.). |
| Kuenn et al.'s worked example: -0.13 before, -1.09 after, so 0.96 pawns (README) | Verified | "The error of black is computed as -0.13 - (-1.09) = 0.96." |
| Kuenn, Seel and Zegners, IZA DP 13491 (README, research explained) | Verified, with the journal version added | Published as "Cognitive Performance in Remote Work: Evidence from Professional Chess", The Economic Journal 132(643), 1218-1232. Only the discussion paper was read, so its engine settings are not checked for the journal version. |
| Sunde, Zegners and Strittmatter showed the time-pressure coefficient flips sign depending on whether decision time is conditioned on (README, research explained) | Verified, with a scope warning | In the 2022 working paper the coefficient on remaining time is -0.0019 on its own and +0.0006 once time spent on the move is controlled: "once conditioning on decision time, the sign of the effect of remaining time budget turns positive and significant". The games were elite over-the-board classical games, and quality was whether the best move was played. It says nothing directly about online bullet or blitz. |
| Sunde et al., "full reference to be added" (research explained) | Added | Working paper: arXiv:2201.10808 (2022). Published: "Speed and quality of complex strategic decisions", PNAS 123(20), e2531472123 (2026). |
| Guid and Bratko (2006), ICGA Journal, origin of the method, using CRAFTY (README) | Verified | ICGA Journal 29(2), 65-73. The authors describe analysing World Championship moves "with the chess program CRAFTY" and scoring the "average deviation between computer's evaluations of moves played by the human and machine-preferred moves". |
| Guid and Bratko used fixed depth so that complex positions get more computation and results reproduce on another machine (README) | Could not verify | The 2006 paper could not be downloaded. The authors' own later summary confirms only that the 2006 search depth was 12 plies. Our reasons for fixed depth stand as our own reasoning, not as their stated rationale. |
| Regan, Biswas and Zhou: centipawn units are not comparable across engines, and Stockfish runs about 1.5 times higher in magnitude than most programs (README, research explained) | Verified, with a date warning | "versions of Stockfish give values about 1.5 times higher magnitude than most programs, while Rybka, Houdini, and Komodo are close to each other". The engines tested were 2014 versions (Stockfish DD and 4). The 1.5 figure should not be assumed for Stockfish 16. |
| About 6% of Lichess games carry [%eval] comments (README) | Verified | "About 6% of the games include Stockfish analysis evaluations" |
| The Lichess known-issues dates the README excludes (README) | Verified | All five entries match the Lichess known-issues list: 12 March 2021, 9 February 2021, June 2020 and before March 2016, December 2016 and before 2016, July to August 2020. |
| %clk clock comments exist from April 2017 (README) | Verified | "clock information down to the second as PGN %clk comments since April 2017" |
| About 30 GB and 90 million games a month (README) | Verified | The most recent monthly file listed was 29.2 GB with 89,616,462 games. |
| The evaluation database holds about 416 million positions (README) | Verified | 416,442,401 positions. |
| Ratings are "Elo" (all documents) | Corrected | Lichess: "The WhiteElo and BlackElo tags contain Glicko2 ratings." Our band of 1200 to 2000 is on the Lichess Glicko-2 scale, not FIDE Elo. |
| The Termination tag values `Normal`, `Time forfeit` and so on (README) | Not a citation | This is not stated on the database page. It was checked against the data itself when the classifier was built and tested. |
| Plotting against time remaining shows a spike at 50% of the clock from berserk players, documented by the chess-blunders project, which also puts games with clock and eval data at 2 to 5% (README) | Corrected | The project reports "a small dip in blunder-rates at 50% of starting time", which the author attributes to berserk players: a dip, not a spike. The 2 to 5% figure is right. It is a hobby project's GitHub README, not a peer-reviewed source. |
| A full verified literature review with 221 claims is in `research/chess-behavioral-lit/REPORT.md` (README) | Corrected | That file does not exist in the repository. The README now points here. |

In short: 28 cited statements checked. 16 verified as cited, 3 verified with a warning or an added detail, 7 corrected or completed, 1 could not be verified, and 1 turned out not to be a citation at all.

## The literature in detail

### 1. Does the last result change the next one?

The idea of a winner or loser effect comes from animal behaviour. Gee et al. define it as "success (or failure) in recent competition leading to an increased probability of success (or failure) in future competition", following Dugatkin (1997). They summarise the animal work as showing that "loser effects appear to consistently be stronger than winner effects", citing studies of sticklebacks, crayfish and copperhead snakes. In human sport they cite evidence from tennis, football and judo. As cited by Gee et al., judoists who won their previous contest are more likely to win the next (Cohen-Zada, Krumer and Shtudiner, 2017), and male tennis players who win a close tiebreak are more likely to win the next set against an evenly matched opponent, an effect not seen in female players (Page and Coates, 2017). Winner and loser effects have also been shown experimentally in competitive video games (Smith and Dukas, 2024, as cited by Gee et al.).

**Gee, Seese, Curley and Ward (2025)** is the closest study to ours. They used a Bayesian hierarchical logistic regression on Lichess games, with the outcome being whether the player won the current game. The predictor was the player's recent win rate within the same session, measured against their long-run win rate, and they controlled for colour and the rating difference with the opponent. A session was defined as games starting within 5 minutes of the previous game's start, and in the grandmaster cohort 88.6% of games were played within 5 minutes of the previous one.

Their data were narrow in two ways that matter for us. They used only 60+0 bullet and 180+0 blitz, and a small number of players: 40 sampled in each of three rating bands plus 25 grandmaster accounts. Table 1 shows 36 players and 590,253 bullet games in the 1700-1900 cohort and 23 grandmasters with 196,522 bullet games. So the result is very precise for each player but rests on few players.

The finding was "little evidence for experiential effects that are consistent across all players, with some individual players showing some evidence for such effects". Posterior mean effects on win probability ran from -0.02 to 0.03, and using ten previous games instead of one added nothing. Their future-work section raises two points our studies took up directly: 24% of grandmaster bullet games are won on time, and such results "may have a different impact on future performance than other endings"; and they did not separate winner and loser effects. Their model also ignores draws.

**How our studies relate.** Gee et al. ask whether the last result predicts the next result. We ask whether the way the last game was won changes how well the next game is played. Our session rule (next game within 30 minutes) and controls (colour, rating gap) mirror theirs. Our outcome is move quality, not the result, and our games are rapid, not bullet or blitz. Study 1's null result on win type agrees with their general finding. Study 2's lucky-win gap of 1.96 cp is about what Gee et al. flagged but did not test: wins on time that were not earned on the board.

**Chowdhary, Iacopini and Battiston (2023)** used all Lichess games from 2013 to 2016, 123 million games between 0.98 million players, restricted the analysis to blitz, and compared each player's hot and cold streaks with a null that shuffles the order of that player's games while keeping their totals of wins, losses and draws. They found "statistically significant hot streaks", cold streaks "typically longer than hot ones", and longer hot streaks for weaker players than for stronger ones. In the published version they checked some alternative explanations. Hot-streak length was only "slightly correlated" with the average rating advantage over opponents, time gaps between games had "a significant but very weak correlation", and repeated games against one opponent were rare, with only 1.6% of player pairs meeting more than 5 times. Their skill measure was each player's average rating, excluding the first 100 games, which they list as a limitation.

So results do cluster beyond chance, but Gee et al. found almost no game-to-game effect on results once rating and colour are controlled. These fit together if most of the clustering comes from things that drift slowly, like form or the strength of opponents, rather than one game changing the next. Neither paper measured how well the moves were played.

### 2. Measuring move quality with an engine

**Guid and Bratko (2006)** started the method of scoring human moves by how far they fall from an engine's choice. They analysed World Championship games with CRAFTY, scoring each champion by the average difference between the engine's evaluation of the played move and its preferred move, and also built a measure of position complexity. Their search depth was 12 plies. The study drew criticism. Readers' "main two objections" were that CRAFTY was too weak and that 12 plies was too shallow. In a ChessBase response, Soren Riis argued that the method measures "which of the world champions played chess most in the style of the 'amputated' version of Crafty". In follow-up work (Guid, Perez and Bratko, 2008; Guid and Bratko, 2011), they report that scores change with search depth and "differ significantly when using different programs", but that the ranking of players who differ clearly stays stable across engines and depths.

**Backus, Cubel, Guid, Sanchez-Pages and Lopez Manas (2023)** brought the method into economics. They used Houdini 1.5a at depth 15 on moves 15 to 30, following Guid and Bratko, for two reasons: to limit computation, and because the middle game "is least likely to follow an established plan" since strong players prepare openings and practise endgames. A move's error is the engine's best-move value minus the value after the played move, set to at least zero, which is the same arithmetic we use. Their data were over-the-board tournament games from The Week in Chess, 2012 to mid-2013: 79,242 games, of which 28,799 games by 2,504 players formed the analysis sample. The mean error was 16.5, against about 5 for world champions in Guid and Bratko (2011), and it was negatively correlated with rating (rho = -0.18). Their main result was that women's mean error between moves 15 and 30 rose by about 11% against male opponents. A footnote notes that each extra move of search depth roughly doubles computing time, which is why depth 15 was chosen.

**Kuenn, Seel and Zegners (2020; journal version 2022)** used the same approach to compare elite players' online and over-the-board games during COVID-19. They removed each player's first 15 moves "as in Backus et al., 2016" and used Stockfish 11 at depth 25. Their appendix gives the worked example our README borrowed: an evaluation of -0.13 before the move and -1.09 after gives an error of 0.96 pawns. The sample was small, 8,260 online moves in 123 games and 19,007 offline moves in 318 games, and conditional on making an error, players made errors 16.8% larger online. The data come from the top players in the world, not from typical online players.

**Regan, Biswas and Zhou (2014)** is the warning about units. Running 726,120 positions from 2010 to 2012 tournaments through four engines, they found that engines "may differ in how they scale these units", with Stockfish giving values about 1.5 times larger in magnitude than Rybka, Houdini and Komodo. They also found that average error per move "scales uniformly higher the more advantage is enjoyed by either side", much more sharply for humans than for computers, and that humans score 2–3% worse when it is their turn to move.

**What this means for our numbers.** Our players lose about 72 cp per move. Backus et al. report 16.5. The two numbers cannot be compared directly: different engine (Stockfish 16 against Houdini 1.5a), different players (Lichess rapid at 1200 to 2000 against rated tournament players), and different time controls. Regan et al. and Guid and Bratko both show that the engine alone changes the scale. Our comparisons are all within one engine, one depth and one data source, so the differences between groups can be compared with each other, but the absolute level cannot be compared with other studies. Regan et al.'s finding that error rises with the size of the advantage also matters for anyone tempted to measure move quality inside a lucky win itself: a player who is losing badly would be expected to show larger errors anyway.

### 3. Time and the quality of decisions

**Sunde, Zegners and Strittmatter** studied how the time spent on a move relates to its quality. The 2022 working paper used over 80,000 moves from about 1,600 elite over-the-board games, 2014 to 2017, at classical time controls of at least 2 hours, between players rated at least 2,500, with Stockfish 14 at depth 24. Quality was whether the best move was played. Faster decisions went with better moves. The remaining-time coefficient is the one our README cites: -0.0019 when entered on its own, +0.0006 once the time spent on the move is controlled. In words, more time on the clock looks harmful until you account for how long the player thought about the move, and then it looks helpful.

The published PNAS version (2026) is larger: over 215,000 moves from about 3,600 games, in classical, rapid and blitz formats, using Stockfish 17. It confirms that faster decisions go with higher quality "even after accounting for computational complexity" and that, conditional on decision time, "a larger time budget is associated with higher decision quality". It also finds the time-quality relationship "quantitatively much larger" in rapid and blitz. The PNAS main text shows the conditional coefficients; the unconditional one that makes the sign flip visible is in the working paper.

For our design, this supports the README's point that time pressure and move quality are tangled, and that the tangle is stronger in faster formats. It is evidence from elite over-the-board chess, though, not from online games at 1200 to 2000.

**Lichess-specific timing effects.** The chess-blunders project, a hobby analysis linked from the Lichess database page, looked at blunder rates (a 200 centipawn loss) in 68 million online games. It reports a bump in blunders at the moment Lichess plays its low-time alarm, including the 60-second mark in 10-minute games, and a small dip at 50% of the starting time, which the author puts down to berserking players in arena tournaments. It used games that already carried evaluations, which it puts at 2 to 5% of games with clock data. These are suggestive patterns, not peer-reviewed results, but they bear on study 2: a win on time ends in exactly the low-time phase where these effects sit.

### 4. The data source

The Lichess database is released under CC0. About 6% of standard games carry Stockfish [%eval] comments. The page does not say how those games are chosen, and the README's concern that they are not a random 6% is why both studies ran Stockfish themselves on a random sample instead of using them. Clock comments exist from April 2017. Bot accounts are tagged with the title BOT, which our filters use. The ratings in the WhiteElo and BlackElo tags are Glicko-2 ratings.

The known-issues list includes dates that would directly damage a design like ours: fake resignations on 9 February 2021, wrong results after the datacenter fire on 12 March 2021, and players able to play themselves in June 2020 and before March 2016. Both studies used 2026 data, which none of these entries affect.

## Where the two studies fit

| | Gee et al. | Chowdhary et al. | Study 1 | Study 2 |
|---|---|---|---|---|
| Data | Lichess bullet and blitz, a few dozen players per cohort | Lichess blitz 2013 to 2016, all players | Lichess rapid, 1 to 5 August and 1 to 5 September 2026 | Lichess rapid, 6 to 30 September 2026, no overlap with study 1 |
| Outcome | Result of the next game | Lengths of win and loss streaks | Move quality in the next game | Move quality in the next game |
| Splits wins by type | No (flagged as future work) | No | Time, checkmate, resignation | Lucky against deserved time wins |
| Finding | Almost no effect | Streaks longer than chance | Differences under 1 cp, inside the preregistered plus or minus 3 cp | Lucky winners 1.96 cp worse (95% CI 0.66 to 3.27); inconclusive under the 2 cp rule |

As far as these sources show, no published study has measured next-game move quality by how the previous game was won, or tested lucky wins on time. The review covered only the sources above, so this is a statement about them, not a full search of the field.

## Corrections made to our documents

- `the research explained.md`: full references for all eight sources, with Sunde et al.'s reference added; the moves 15 to 30 window credited to Guid and Bratko via Backus et al.; a scope note on Sunde et al.; a note that "Elo" means the Lichess Glicko-2 rating.
- Both slide decks: complete references for Gee et al. (journal version), Backus et al. (pages) and Guid and Bratko (title, volume, pages). The decks were rebuilt.
- `README.md`: it is the original brief and is left as written, except that the broken link to a review file that does not exist now points here. Its errors are listed in the table above.

## Could not verify

- Guid and Bratko (2006) itself. The PDF and the publisher page were blocked. Its details come from the ChessBase republication header and from the authors' own 2011 summary. The README's statement that they chose fixed depth for reproducibility and so complex positions get more search is not confirmed.
- The journal version of Kuenn et al. (Economic Journal). Only the 2020 discussion paper was read.
- Whether Stockfish 16, the engine we used, still scales centipawns differently from other engines. Regan et al. tested 2014 versions.
- The original studies cited by Gee et al. (Dugatkin; Page and Coates; Cohen-Zada et al.; Smith and Dukas) were not read; they are reported only as Gee et al. describe them.
- Whether berserk gives "double points", as the README puts it. The chess-blunders README says "double the rating points"; the Lichess tournament rules were not checked.

## Sources read

- Gee, A., Seese, S. O., Curley, J. P. and Ward, O. G. (2025). Investigating experiential effects in online chess using a hierarchical Bayesian analysis. Journal of Quantitative Analysis in Sports 22(2), 117-132. https://doi.org/10.1515/jqas-2025-0035. Read in full: arXiv:2503.21713 PDF, plus the journal text from Europe PMC (PMC13265758) for the key passages.
- Chowdhary, S., Iacopini, I. and Battiston, F. (2023). Quantifying human performance in chess. Scientific Reports 13, 2113. https://doi.org/10.1038/s41598-023-27735-9. Read in full: arXiv:2207.07780 PDF and the journal text from Europe PMC (PMC9902564). Author correction, Sci Rep 13, 4787, read in full.
- Backus, P., Cubel, M., Guid, M., Sanchez-Pages, S. and Lopez Manas, E. (2023). Gender, competition, and performance: Evidence from chess players. Quantitative Economics 14(1), 349-380. https://doi.org/10.3982/qe1404. Read in full: published version from City Research Online.
- Kuenn, S., Seel, C. and Zegners, D. (2020). Cognitive performance in the home office: Evidence from professional chess. IZA DP 13491. https://docs.iza.org/dp13491.pdf. Read in full. Journal version (Economic Journal 132(643), 1218-1232) checked through Crossref only.
- Sunde, U., Zegners, D. and Strittmatter, A. (2022). Speed, quality, and the optimal timing of complex decisions: Field evidence. arXiv:2201.10808. Read in full. Published as Speed and quality of complex strategic decisions, PNAS 123(20), e2531472123 (2026), https://doi.org/10.1073/pnas.2531472123, read in full from Europe PMC (PMC13187726).
- Regan, K. W., Biswas, T. and Zhou, J. (2014). Human and computer preferences at chess. AAAI-14 Workshop on Advances in Preference Handling. https://cdn.aaai.org/ocs/ws/ws1274/8859-38007-1-PB.pdf. Read in full.
- Guid, M. and Bratko, I. (2006). Computer analysis of world chess champions. ICGA Journal 29(2), 65-73. Not read; details from the ChessBase republication page (https://en.chessbase.com/post/computer-analysis-of-world-champions), which mainly carries Soren Riis's critique, and from Guid and Bratko's own ChessBase article on their 2011 paper (https://en.chessbase.com/post/using-che-engines-to-estimate-human-skill).
- Lichess open database page, https://database.lichess.org/, read 13 October 2026.
- Antiochian, chess-blunders README, https://github.com/Antiochian/chess-blunders. Read in full.
- Crossref records for every DOI above, for volume, issue and page numbers.

## Verification

106 claims checked against the downloaded source text: 105 matched word for word and 1 matched except for letter case. None had to be dropped. Several were reworded during checking to match the source's exact wording. The ledger and the downloaded sources are kept outside the repository; ask if you want them added.
