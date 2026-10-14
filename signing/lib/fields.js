// Shared definitions: your profile fields, intake questions per signing type, and
// the data keys templates use to auto-fill ("profile.full_name", "intake.legal_name", "deal.advance").

export const PROFILE_FIELDS = [
  { key: "full_name", label: "Full legal name" },
  { key: "title", label: "Title" },
  { key: "company", label: "Company" },
  { key: "email", label: "Email" },
  { key: "phone", label: "Phone" },
  { key: "address_line1", label: "Address line 1" },
  { key: "address_line2", label: "Address line 2" },
  { key: "city", label: "City" },
  { key: "state", label: "State" },
  { key: "postal_code", label: "ZIP / postal code" },
  { key: "country", label: "Country" },
  { key: "pro", label: "PRO (ASCAP/BMI/…)" },
  { key: "ipi", label: "IPI / CAE #" },
  { key: "publisher", label: "Publishing company" },
  { key: "publisher_ipi", label: "Publisher IPI #" },
  { key: "website", label: "Website" },
];

export const CATEGORIES = [
  { key: "artist", label: "Artist" },
  { key: "composer", label: "Composer" },
  { key: "producer", label: "Producer" },
  { key: "songwriter", label: "Songwriter" },
  { key: "catalog_owner", label: "Catalog owner" },
  { key: "other", label: "Other" },
];

const PROS = ["ASCAP", "BMI", "SESAC", "GMR", "SOCAN", "PRS", "APRA AMCOS", "GEMA", "SACEM", "None", "Other"];

const COMMON = [
  { section: "About you" },
  { key: "legal_name", label: "Full legal name", required: true },
  { key: "professional_name", label: "Professional / artist name" },
  { key: "email", label: "Email", type: "email", required: true },
  { key: "phone", label: "Phone", type: "tel" },
  { key: "date_of_birth", label: "Date of birth", type: "date" },
  { key: "address_line1", label: "Street address", required: true },
  { key: "address_line2", label: "Apt / suite" },
  { key: "city", label: "City", required: true },
  { key: "state", label: "State / province" },
  { key: "postal_code", label: "ZIP / postal code" },
  { key: "country", label: "Country", required: true },
  { key: "entity_name", label: "Signing through a company (loan-out)? Company name", help: "Leave blank if signing personally" },
];

const WRITER = [
  { section: "Publishing & PRO" },
  { key: "pro", label: "PRO affiliation", type: "select", options: PROS },
  { key: "ipi", label: "Writer IPI / CAE #" },
  { key: "publisher", label: "Your publishing company (if any)" },
  { key: "publisher_ipi", label: "Publisher IPI #" },
  { key: "admin", label: "Current publishing administrator (if any)" },
];

const RECORDING = [
  { section: "Recordings" },
  { key: "isni", label: "ISNI (if known)" },
  { key: "soundexchange", label: "Registered with SoundExchange?", type: "select", options: ["Yes", "No", "Not sure"] },
  { key: "distributor", label: "Current distributor / label" },
  { key: "spotify_url", label: "Spotify / Apple Music link" },
];

const TEAM = [
  { section: "Your team" },
  { key: "manager", label: "Manager name & email" },
  { key: "attorney", label: "Attorney name & email" },
  { key: "social", label: "Instagram / TikTok / website" },
  { key: "notes", label: "Anything else we should know?", type: "textarea" },
];

const EXTRA = {
  artist: [...WRITER, ...RECORDING],
  composer: [...WRITER, { key: "libraries", label: "Other music libraries you're signed with", type: "textarea" }, { key: "daw", label: "Primary DAW / setup" }],
  producer: [...WRITER, ...RECORDING, { key: "producer_points", label: "Typical producer points / royalty", help: "e.g. 3% of SRLP" }],
  songwriter: [...WRITER],
  catalog_owner: [
    { section: "Catalog" },
    { key: "catalog_name", label: "Catalog name" },
    { key: "catalog_type", label: "What does the catalog include?", type: "select", options: ["Publishing (compositions)", "Masters (recordings)", "Both"] },
    { key: "catalog_size", label: "Approx. number of works / masters" },
    { key: "ownership_share", label: "Your ownership share", help: "e.g. 100% of publisher share" },
    { key: "existing_deals", label: "Existing admin / distribution deals and their end dates", type: "textarea" },
    { key: "annual_revenue", label: "Approx. annual revenue (last 3 years)" },
    ...WRITER.slice(1),
  ],
  other: [...WRITER],
};

/** Intake questionnaire for a signing type. */
export function intakeQuestions(category) {
  return [...COMMON, ...(EXTRA[category] || EXTRA.other), ...TEAM];
}

/** All intake keys (for the template editor's key picker). */
export const ALL_INTAKE_KEYS = Array.from(
  new Map(
    CATEGORIES.flatMap((c) => intakeQuestions(c.key))
      .filter((q) => q.key)
      .map((q) => [q.key, q.label])
  ),
  ([key, label]) => ({ key, label })
);

/** Computed helper values available to templates. */
function derived(src = {}) {
  const addr = [src.address_line1, src.address_line2].filter(Boolean).join(", ");
  const cityLine = [src.city, [src.state, src.postal_code].filter(Boolean).join(" ")].filter(Boolean).join(", ");
  return { full_address: [addr, cityLine, src.country].filter(Boolean).join(", ") };
}

export const today = () => new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });

/** Resolve "profile.x" / "intake.x" / "deal.x" / "today" to a value. */
export function resolveKey(key, ctx) {
  if (!key) return undefined;
  if (key === "today") return today();
  const [ns, ...rest] = key.split(".");
  const name = rest.join(".");
  const src = ctx[ns];
  if (!src) return undefined;
  const v = src[name] ?? derived(src)[name];
  return v === "" ? undefined : v;
}

export const FIELD_TYPES = [
  { type: "signature", label: "Signature", w: 0.26, h: 0.05 },
  { type: "initials", label: "Initials", w: 0.09, h: 0.04 },
  { type: "date", label: "Date signed", w: 0.18, h: 0.025 },
  { type: "text", label: "Text", w: 0.26, h: 0.025 },
  { type: "checkbox", label: "Checkbox", w: 0.025, h: 0.02 },
];
