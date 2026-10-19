# Post-purchase email fixes (to apply in Kajabi → Automations)

These couldn't be applied from here: the Kajabi connection lacks the "Create and edit automations" permission.

## 1. Broken login link (all welcome emails)
`www.jodyfriedman.com/login` returns a 404: jodyfriedman.com only forwards its home page.
Replace it with `https://www.wrecktheroom.com/login` (both the link and the visible text) in:

| Automation | Email |
|---|---|
| 869762 | Blueprint purchased: "Welcome to Wreck the Room" |
| 890989 | Blueprint granted: "Welcome to Wreck the Room: Blueprint" |
| 869846 | Council purchased: "Welcome to Wreck the Room: Council" (2 links) |
| 890985 | Council granted: same email (2 links) |
| 869761 | Inner Circle purchased/granted: "Welcome to Wreck the Room" (`http://` version) |

## 2. Blueprint emails tell buyers they're in Council (869762, 890989)
"You're not the only one in Council right now." → "You're not the only one doing this work right now."

## 3. Inner Circle email (869761)
- Its workbook link is the old Google Doc; Blueprint and Council now use workbook.wrecktheroom.com.
- It names the community "Activated Architects"; the others call it "Architects".

## 4. Offers with no welcome email
Clarity Session ($1,000), Blueprint Add-On ($2,000), and the four $997 Guided Transformations only get Kajabi's
system receipt. Each should get a short "you're in, here's what to do next" email (same steps as its thank-you page).
