// Guess which of your saved values belongs in a PDF form field, from the field's name.
import { today, PROFILE_FIELDS } from "@/lib/fields";

const STANDARD = new Set(PROFILE_FIELDS.map((f) => f.key));

const RULES = [
  [/sign(ature)?/, null], // signature boxes need a placed signature image, not text
  [/initial/, null],
  [/^date|dated|date$|todaysdate|signdate|datesigned/, () => today()],
  [/email|e-?mail/, "email"],
  [/phone|tel|mobile|cell/, "phone"],
  [/zip|postal/, "postal_code"],
  [/country/, "country"],
  [/city|town/, "city"],
  [/^state|state$|province|region/, "state"],
  [/address2|addressline2|apt|suite|unit/, "address_line2"],
  [/address|street|addr/, "address_line1"],
  [/ipi|cae/, "ipi"],
  [/^pro$|society|prtaffil|proaffil/, "pro"],
  [/publisher/, "publisher"],
  [/company|business|entity|organi[sz]ation|employer|firm/, "company"],
  [/title|position|capacity/, "title"],
  [/website|url|web/, "website"],
  [/fullname|yourname|printedname|printname|legalname/, "full_name"],
  [/firstname|^fname|^first|givenname/, (d) => (d.full_name || "").split(/\s+/)[0]],
  [/lastname|^lname|^last|surname|familyname/, (d) => (d.full_name || "").split(/\s+/).slice(1).join(" ")],
  [/name|print/, "full_name"],
];

export function autoMatch(fieldName, data = {}) {
  const n = fieldName.toLowerCase().replace(/[^a-z0-9]/g, "");
  if (/sign|initial/.test(n)) return undefined;
  // your custom saved values first (e.g. "soundexchange_id")
  for (const [k, v] of Object.entries(data)) if (!STANDARD.has(k) && k.length > 3 && n.includes(k.replace(/[^a-z0-9]/g, ""))) return v;
  for (const [re, target] of RULES) {
    if (!re.test(n)) continue;
    if (target === null) return undefined;
    if (typeof target === "function") return target(data) || undefined;
    return data[target] || undefined;
  }
  return undefined;
}
