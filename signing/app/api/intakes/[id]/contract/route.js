import * as db from "@/lib/db";
import { route, httpError } from "@/lib/http";
import { contractFromIntake } from "@/lib/intake";

export const POST = route(async (req, { id }) => {
  const intake = await db.get("intakes", id);
  if (!intake) throw httpError("Not found", 404);
  const { recipients, values, send } = await req.json();
  return contractFromIntake(intake, { recipients, values, send });
});
