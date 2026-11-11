# Quiz follow-up: program offer for people who didn't book a call

Someone takes "The Room You're In" quiz, gets their result (Drifting, Stalling, Renovating or Rebuilding), and doesn't book a
strategy call. A week later they get a 4-email offer for the Guided Transformation that matches their result, with
**50% off using code QUIZ50 for 5 days**. The emails never state a price.

The copy follows Jody's framework (see `OUTCOME-COPY-DRAFT.md`): Drifting = unaware, not acting; Stalling = aware, not acting;
Renovating = acting on the wrong things; Rebuilding = aware and acting, but plateauing.

Everything below is built in Kajabi as a **draft**. Nothing sends until it's published (see the checklist at the bottom).

## Timeline (day 0 = the day they take the quiz)

| Day | What happens | Already existed? |
|---|---|---|
| 0 | Result email; "X Email Sent" tag added | Yes |
| 1–6 | "Did Not Book Strategy Call" sequence (4 emails) | Yes |
| 7 | Program offer starts, unless they booked a call or bought anything. Tag `Quiz Bonus Window: Open` added | **New** |
| 7 | E1: "You didn't jump into Wreck the Room. That's okay." (pain, who they'll be, QUIZ50) | **New** |
| 9 | E2: "Who you'll be in five weeks" | **New** |
| 10 | E3: The excuse that fits their room | **New** |
| 11 | E4: "Last day for your 50% off" | **New** |
| 12 | Offer window closes (tag removed) | **New** |

Booking a call or buying any Wreck the Room offer stops the emails right away.

## What was built in Kajabi

**Sequences** (4 emails each, drafts)

| Result | Sequence | E3 excuse |
|---|---|---|
| Drifting | [2148907277](https://app.kajabi.com/admin/email_sequences/2148907277/edit) | "Things are fine, really" |
| Stalling | [2148907278](https://app.kajabi.com/admin/email_sequences/2148907278/edit) | "Now isn't the right time" |
| Renovating | [2148907279](https://app.kajabi.com/admin/email_sequences/2148907279/edit) | "I just need the right strategy" |
| Rebuilding | [2148907280](https://app.kajabi.com/admin/email_sequences/2148907280/edit) | "I should be able to figure this out myself" |

**Automations** (drafts)

| Automation | What it does |
|---|---|
| [1164063](https://app.kajabi.com/admin/workflows/1164063/edit) Start Drifting offer | "Drifting Email Sent" tag → wait 7 days → skip if booked/customer → offer tag, subscribe, wait 5 days, remove tag |
| [1164065](https://app.kajabi.com/admin/workflows/1164065/edit) Start Stalling offer | Same, for Stalling |
| [1164066](https://app.kajabi.com/admin/workflows/1164066/edit) Start Renovating offer | Same, for Renovating |
| [1164067](https://app.kajabi.com/admin/workflows/1164067/edit) Start Rebuilding offer | Same, for Rebuilding |
| [1164068](https://app.kajabi.com/admin/workflows/1164068/edit) Stop when a call is booked | "Booked Strategy Call" tag → unsubscribe from all 4, remove offer tag |
| [1164069](https://app.kajabi.com/admin/workflows/1164069/edit) Stop on purchase | Any of the 7 WTR offers purchased → unsubscribe from all 4, remove offer tag |

Tag: `Quiz Bonus Window: Open` (2150403266). Coupon: `QUIZ50` (50% off, works on all four programs; Jody created it).

Kajabi's "exit conditions" feature isn't enabled on this account, so stopping is handled by the two stop automations,
the same way the existing "Did Not Book" sequence is stopped.

## Offer pages (live)

| Program | Page |
|---|---|
| Drifting | https://www.wrecktheroom.com/drifting-program |
| Stalling | https://www.wrecktheroom.com/stalling-program |
| Renovating | https://www.wrecktheroom.com/renovating-program |
| Rebuilding | https://www.wrecktheroom.com/rebuilding-program |

The emails link to these pages with `?bonus=1`, which shows the "Quiz offer" banner and adds `coupon_code=QUIZ50` to the
checkout links, so the discount is already applied. Without `?bonus=1` the pages are full price.
(`/drifting`, `/stalling`, etc. are the existing quiz-result pages; they only offer the strategy call.)
Each page is a Kajabi landing page whose Code block loads `programs.js` from jsDelivr pinned to a commit. After changing the
pages, rebuild, push, and update the commit in the four Code blocks.

## Publishing checklist

1. ~~Create the four landing pages~~ Done.
2. Move the older `[SEQUENCE] Quiz Offer = …` sequences (2148906775 to 2148906778 and 2148906787 to 2148906790) to the
   "NOT USING" folder. Only the four ending in `(QUIZ50)` are in use.
3. **Read the 16 emails** in the four `(QUIZ50)` sequences, then publish each one (Kajabi creates sequence emails as drafts).
4. **Publish the 6 automations** (a person has to click Publish; the Kajabi connection can't). Publish the two "stop"
   automations (1164068, 1164069) *first*, then the four "start" automations.

New quiz-takers enter the flow from the day you publish. The ~40 people already tagged "X Email Sent" won't get it
automatically. To reach them, send a one-time broadcast per result, or add them to the matching sequence by hand.
