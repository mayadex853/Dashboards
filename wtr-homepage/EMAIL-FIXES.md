# Post-purchase email fixes (Kajabi → Automations)

Status as of 2026-10-19. Applied through the Kajabi connection unless marked **manual**.

## 1. Broken login link (all welcome emails): done, except Inner Circle
`www.jodyfriedman.com/login` returns a 404: jodyfriedman.com only forwards its home page.
Replaced with `https://www.wrecktheroom.com/login` (both the link and the visible text) in:

| Automation | Email | Status |
|---|---|---|
| 869762 | Blueprint purchased: "Welcome to Wreck the Room" | Done |
| 890989 | Blueprint granted: "Welcome to Wreck the Room: Blueprint" | Done |
| 869846 | Council purchased: "Welcome to Wreck the Room: Council" (2 links) | Done |
| 890985 | Council granted: same email (2 links) | Done |
| 869761 | Inner Circle purchased/granted: "Welcome to Wreck the Room" (`http://` version) | **Manual** (see below) |

## 2. Blueprint emails told buyers they're in Council (869762, 890989): done
"You're not the only one in Council right now." → "You're not the only one doing this work right now."

## 3. Community name and workbook
- Council (869846, 890985): "Access to the Activated Architects community" → "Access to the Architects community". Done.
- Inner Circle (869761): **manual**, see below.

### Inner Circle (869761): manual edit
This automation has two triggers (purchased + granted) feeding one email, and the Kajabi connection can't edit
steps in that shape yet. Open https://app.kajabi.com/admin/workflows/869761/edit, open the email, and make three edits:

1. **Workbook (Step 1).** Replace the line "First, Download your Workbook here." (it links to the old Google Doc) with:
   > First, go to your workbook: [workbook.wrecktheroom.com](https://workbook.wrecktheroom.com/)
   >
   > Quick heads up: your answers live in your browser. Export or save a backup copy as you go — you'll see instructions for that inside.
2. **Login link (Step 1).** Change `http://www.jodyfriedman.com/login` to `https://www.wrecktheroom.com/login`, and the visible text to `www.wrecktheroom.com/login`.
3. **Community name (Step 3).** "immediate access to **Activated Architects**" → "immediate access to **Architects**".

## 4. Offers with no welcome email: drafted
Each one has a short "you're in, here's what to do next" email, built as a **draft** automation (trigger: offer purchased).
Drafts send nothing. Review each one and click Publish in Kajabi to turn it on.

| Offer | Draft automation | Subject |
|---|---|---|
| Clarity Session ($1,000) | [1164023](https://app.kajabi.com/admin/workflows/1164023/edit) | Your Clarity Session with Jody: next steps |
| Blueprint Add-On ($2,000) | [1164024](https://app.kajabi.com/admin/workflows/1164024/edit) | Your 3 alignment sessions with Jody: next steps |
| Drifting ($997) | [1164025](https://app.kajabi.com/admin/workflows/1164025/edit) | Welcome to Wreck the Room: Drifting |
| Stalling ($997) | [1164026](https://app.kajabi.com/admin/workflows/1164026/edit) | Welcome to Wreck the Room: Stalling |
| Renovating ($997) | [1164027](https://app.kajabi.com/admin/workflows/1164027/edit) | Welcome to Wreck the Room: Renovating |
| Rebuilding ($997) | [1164028](https://app.kajabi.com/admin/workflows/1164028/edit) | Welcome to Wreck the Room: Rebuilding |

They follow the thank-you page steps:
- **Sessions:** log in, open the coaching product in the library, and book a time. The Clarity email asks the buyer to bring one honest question. The Add-On email times the three sessions to Lesson 1, the halfway point and the finish.
- **Guided Transformations:** log in, open the program, do the exercise after every lesson, and give it five weeks. Each email opens with one line from its offer description, and each ends with an invitation to ask for more support (an upgrade path).

Not done: Blueprint and Council have separate "offer granted" automations for comped access. These drafts cover purchases only.
Add an "offer is granted" trigger to a draft if you plan to give that offer away.
