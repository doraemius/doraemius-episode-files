# Narration — Kokoro TTS on a Mac

The words the video speaks, section by section. `{H}` marks a joke sentence and `{U}` a human
touch (a filler, a beat before a reveal); `voice.py` strips them before synthesis, and
`script-knobs.py` counts them (this script: Humor 32%, Human 10% of 60 sentences). `…` is a silent
beat. Lines in `[ ]` are on-screen cues, not read.

## 0. Cold open

`[AUDIO: clip D, 6 s, the old narration]`

> That's my channel's narrator. {H}Great voice. No pulse.
> It's Kokoro, a free text-to-speech model, and it runs right here on my Mac, with no GPU and no cloud.
> {H}And for five videos, it read every script like it was defusing a bomb, one full stop at a time.
> So I measured it, I compared it with people who talk for a living, and I fixed about half of it.
> {H}The other half is still… a robot.

## 1. What it is

`[SCREEN: model card — 82M, Apache 2.0, 8 languages, 54 voices]`

> Kokoro has eighty-two million parameters, which, for an AI model, is tiny.
> {H}Some of my browser tabs use more memory than that.
> It's Apache two point oh, so you can use it commercially, and it comes with eight languages and fifty-four voices.
> On my M1, it makes speech five to six times faster than real time.
> {U}So, you know, a four-minute video takes it under a minute.
> {H}That's faster than I can find the file it saved.

## 2. The speed knob

`[SCREEN: speed 1.0 vs 1.15, two waveforms, 115.7 s vs 106.5 s]`

> There's a speed setting, and I set it to one point one five, expecting fifteen percent faster.
> I got eight.
> {H}The knob is an optimist.
> But here's the real problem: at the default setting, it read my scripts at up to two hundred and twenty-three words a minute.
> A normal conversation runs about one fifty.
> {H}I wasn't narrating, I was reading the terms and conditions.
> So now I aim for one seventy-five to two hundred, and I check every scene after it's made, because the same setting reads faster or slower depending on the words.
> {H}Knobs, it turns out, have moods.

## 3. Where it trips

`[SCREEN: the SPOKEN table — "curl -LsSf" → "curl dash L s capital S f"]`

> Kokoro reads text, not intent.
> Give it a command like curl, dash L s capital S f, and it will try… its very best.
> {H}Its best is a sneeze.
> {U}So, uh, every episode gets a little cheat sheet: before a line is spoken, I swap the hard bits for how they sound.
> Then a second model listens back and writes down what it heard.
> {H}It's the only thing in my house that listens to me.
> On one episode, twenty-one of twenty-four scenes came back almost word for word, and the other three only argued about digits.
> {H}Honestly, same.

## 4. Why it sounds like a robot

`[GRAPHIC: pace and pauses — human speakers vs Kokoro, overlapping ranges; no names, no footage]`

> Then someone whose ear I trust said it: it sounds like a robot.
> {U}And, I mean… fair.
> My first guess was speed, because people speed up and slow down.
> So I measured my narrator against people who talk for a living.
> Its pace and its pauses were already inside their range.
> {H}So, guess one: wrong.

`[GRAPHIC: pitch curves — human speakers all different, Kokoro the same shape falling at every end]`

> Then I looked at pitch.
> Each of them shapes every phrase differently, but Kokoro sings almost every phrase to the same tune, and it drops hard at the end of each one.
> {H}Every sentence ends like it's hanging up on you.
> On a sameness score, the humans were around zero point zero five, and my narrator was zero point seven.
> {H}That's not a voice, that's a ringtone.

## 5. What the humans do

`[SCREEN: the counts — "but", questions, openers]`

> So I read how they talk, not their jokes, just how the jokes are built.
> They glue ideas together with and, but, and so, and they say "but" at least twice as often as my scripts did.
> {H}My scripts glued ideas together with full stops.
> They ask questions, and my last two scripts asked none.
> {H}Not one, very confident scripts.
> They set up for a while, and then they land it in four or five words.
> {H}Like this.
> {U}And right before the good part… they wait.

## 6. What fixed it

`[AUDIO: clip D, then clip E, same lines]`

> So I rewrote one minute of an old script the way a person would actually say it, and played both.
> By my score it was about a quarter less robotic, and to my ear it was a lot better.
> {U}Like, a lot.

`[AUDIO: clip F]`

> Then I added the human stuff: a pause before the reveal, the aside a little faster, a "you know" here and there.
> And here's the twist.
> By my own score, that version got worse.
> By ear, it was the best of the lot.
> {H}So now I trust my ears over my graphs, and my graphs are taking it personally.
> The lesson is simple: the model is half of it, and the other half is writing for the mouth, not the page.

## 7. Close

> All of this ran on one Mac, and the scripts and numbers are linked below.
> {U}Oh, and one more thing…
> {H}This whole video was read by Kokoro, so if it sounded human, thank the humans, and if it didn't, blame the ringtone.
