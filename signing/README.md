# HD Sign

Your own internal e-signature system for signings and paperwork. It's built for internal use only, not for resale.

- **Intake → contract.** Send a new artist, composer, producer, songwriter or catalog owner a short intake form. Their answers (legal name, address, PRO/IPI, publisher…) fill your contract template automatically. You review it and click send, or have it send automatically.
- **Templates.** Upload each contract PDF once, then drag on signature, initials, date, text and checkbox fields. Text fields can auto-fill from the signee's intake answers (`intake.legal_name`), your info (`profile.company`) or deal terms you type when sending (`deal.advance`).
- **Signing order.** Signers are emailed one after another. Signers who share an order number sign at the same time. Your countersignature uses your saved signature with one click.
- **Quick Sign.** Someone sent you a form? Upload it. Fillable fields are auto-filled from your saved info, and you click to drop your name, address, signature or today's date anywhere. Then download it or email it back from your M365 address.
- **Audit trail.** Each completed document gets a Certificate of Completion page: every signer's consent, view and sign times, IP address and device, plus SHA-256 fingerprints. Everyone gets the final PDF by email.

## Setup (about 30 minutes, once)

### 1. Supabase (database + file storage) — free tier is fine
1. Create a project at [supabase.com](https://supabase.com).
2. **SQL Editor → New query**, paste [`supabase/schema.sql`](supabase/schema.sql), and run it.
3. **Project Settings → API**: copy the **Project URL** and the **service_role** key. Keep the service_role key secret, because it has full access.

### 2. Microsoft 365 email (sends as jody@hdmusicnow.com)
1. [Azure Portal](https://portal.azure.com) → **Microsoft Entra ID → App registrations → New registration**. Name it "HD Sign" and choose single tenant.
2. Copy the **Application (client) ID** and **Directory (tenant) ID**.
3. **Certificates & secrets → New client secret**. Copy the secret's **Value**.
4. **API permissions → Add → Microsoft Graph → Application permissions → `Mail.Send`**, then **Grant admin consent**.
5. *(Recommended)* By default this permission can send as any mailbox in your tenant. To lock it to just your mailbox, run this in Exchange Online PowerShell:
   ```powershell
   New-DistributionGroup -Name "HD Sign Senders" -Type Security -Members jody@hdmusicnow.com
   New-ApplicationAccessPolicy -AppId <client-id> -PolicyScopeGroupId "HD Sign Senders" -AccessRight RestrictAccess -Description "HD Sign"
   ```

You can skip this step at first. The app still works and shows each signing link for you to copy and send yourself.

### 3. Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) → **Add New Project** → import this GitHub repo.
2. Set **Root Directory** to `signing`.
3. Add the environment variables from [`.env.example`](.env.example):
   `APP_URL`, `ADMIN_PASSWORD`, `SESSION_SECRET`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `MS_TENANT_ID`, `MS_CLIENT_ID`, `MS_CLIENT_SECRET`, `MAIL_FROM`, `MAIL_FROM_NAME`.
4. Deploy. *(Optional)* Add a custom domain such as `sign.hdmusicnow.com` and set `APP_URL` to match.

### 4. First run
1. Sign in with your `ADMIN_PASSWORD`.
2. **My info & signature**: fill in your details and create your signature and initials.
3. **Templates**: upload each contract, set its roles (usually *Signee* then *Me*), and place fields.

## Try it locally
```bash
cd signing
npm install
ADMIN_PASSWORD=test npm run dev
```
With no Supabase variables set, the app runs in **local mode** and stores data in `signing/.data/`. This is for testing only.

## Daily use
| I want to… | Go to |
|---|---|
| Sign a form someone emailed me | **Quick Sign** |
| Onboard a new signee | **Intake** → pick type + template → they fill the form → **Review & send** |
| Send a contract to several people in order | **Send for signature** |
| See who still needs to sign / resend / get a link | **Dashboard** → click the document |

## Notes
- **Legal.** E-signatures with consent, intent and an audit trail are valid under the U.S. ESIGN Act and UETA for most entertainment agreements. A few document types (wills, some real-estate and court filings) need wet ink or notarization. Have your attorney review your templates once.
- **Tax info.** The intake deliberately does not collect SSNs. Collect W-9/W-8BEN forms separately.
- **Attachments.** Completed PDFs over about 2.8 MB are too large for Graph's simple send. The email still goes out, but asks the recipient to reply for a copy. You can always download the file from the dashboard.
- Signing links are single-use secrets, stored only as hashes. Your saved signature is offered on a signing page only when you're logged in and it's your signer slot.
