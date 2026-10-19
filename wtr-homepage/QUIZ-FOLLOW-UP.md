# Quiz follow-up: program offer for people who didn't book a call

Someone takes "The Room You're In" quiz, gets their result (Drifting, Stalling, Renovating or Rebuilding), and doesn't book a
strategy call. A week later they get a 4-email offer for the $997 Guided Transformation that matches their result, with a
5-day bonus: a private 30-minute call with Jody at week 3.

Everything below is built in Kajabi as a **draft**. Nothing sends until it's published (see the checklist at the bottom).

## Timeline (day 0 = the day they take the quiz)

| Day | What happens | Already existed? |
|---|---|---|
| 0 | Result email; "X Email Sent" tag added | Yes |
| 1–6 | "Did Not Book Strategy Call" sequence (4 emails) | Yes |
| 7 | Program offer starts, unless they booked a call or bought anything. Tag `Quiz Bonus Window: Open` added | **New** |
| 7 | E1: "You didn't jump into Wreck the Room. That's okay." (offer + bonus) | **New** |
| 9 | E2: What the five weeks look like | **New** |
| 10 | E3: The objection that fits their result | **New** |
| 11 | E4: "Last day for your bonus call" | **New** |
| 12 | Bonus window closes (tag removed) | **New** |

Booking a call or buying any Wreck the Room offer stops the emails right away. A Guided Transformation bought while
the bonus tag is on sends the buyer a "your bonus call is locked in" email and emails team@jodyfriedman.com to
schedule it.

## What was built in Kajabi

**Sequences** (4 emails each, drafts)

| Result | Sequence | E3 objection |
|---|---|---|
| Drifting | [2148906775](https://app.kajabi.com/admin/email_sequences/2148906775/edit) | "I should be able to figure this out on my own" |
| Stalling | [2148906776](https://app.kajabi.com/admin/email_sequences/2148906776/edit) | "I should be able to figure this out on my own" |
| Renovating | [2148906777](https://app.kajabi.com/admin/email_sequences/2148906777/edit) | "I've already done so much work on myself" |
| Rebuilding | [2148906778](https://app.kajabi.com/admin/email_sequences/2148906778/edit) | "Things are already going pretty well" |

**Automations** (drafts)

| Automation | What it does |
|---|---|
| [1164063](https://app.kajabi.com/admin/workflows/1164063/edit) Start Drifting offer | "Drifting Email Sent" tag → wait 7 days → skip if booked/customer → bonus tag, subscribe, wait 5 days, remove tag |
| [1164065](https://app.kajabi.com/admin/workflows/1164065/edit) Start Stalling offer | Same, for Stalling |
| [1164066](https://app.kajabi.com/admin/workflows/1164066/edit) Start Renovating offer | Same, for Renovating |
| [1164067](https://app.kajabi.com/admin/workflows/1164067/edit) Start Rebuilding offer | Same, for Rebuilding |
| [1164068](https://app.kajabi.com/admin/workflows/1164068/edit) Stop when a call is booked | "Booked Strategy Call" tag → unsubscribe from all 4, remove bonus tag |
| [1164069](https://app.kajabi.com/admin/workflows/1164069/edit) Stop on purchase + deliver bonus | Any of the 7 WTR offers purchased → unsubscribe from all 4; if they bought a program inside the window: bonus email to buyer + notice to team |

New tag: `Quiz Bonus Window: Open` (2150403266).

Kajabi's "exit conditions" feature isn't enabled on this account, so stopping is handled by the two stop automations,
the same way the existing "Did Not Book" sequence is stopped.

## Offer pages

The emails link to `https://www.wrecktheroom.com/{drifting|stalling|renovating|rebuilding}?bonus=1`.
`?bonus=1` shows the bonus banner on the page. The pages come from `build_programs.py` (see README).

## Publishing checklist

1. **Create the four Kajabi landing pages** at `/drifting`, `/stalling`, `/renovating` and `/rebuilding`, each with a Code
   block holding that program's snippet from the README. If you use different URLs, change the links in the 16 emails.
2. **Read the 16 emails**, then publish each one inside its sequence (Kajabi creates sequence emails as drafts).
3. **Publish the 6 automations.** Publish the two stop automations (1164068, 1164069) *first*, then the four start automations.
4. **Decide who books the bonus calls.** The team email goes to team@jodyfriedman.com and promises the buyer a reply within 2 business days.

New quiz-takers enter the flow from the day you publish. The ~40 people already tagged "X Email Sent" won't get it
automatically. To reach them, send a one-time broadcast per result, or add them to the matching sequence by hand.
