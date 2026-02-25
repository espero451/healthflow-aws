import fs from "node:fs";
import path from "node:path";
import { models } from "./definitions.js";

const outDir = path.resolve("generated");
fs.mkdirSync(outDir, { recursive: true });

const schemas: Record<string, unknown> = {};
const typeLines: string[] = ["// Generated types", ""]; 

for (const model of models) {
  const required = Object.entries(model.fields)
    .filter(([, field]) => field.required)
    .map(([name]) => name);
  const properties: Record<string, unknown> = {};
  for (const [name, field] of Object.entries(model.fields)) {
    const schemaType = field.type === "datetime" ? "string" : field.type;
    properties[name] = {
      type: schemaType,
      description: field.description
    };
  }
  schemas[model.name] = {
    type: "object",
    required,
    properties
  };

  typeLines.push(`export type ${model.name} = {`);
  for (const [name, field] of Object.entries(model.fields)) {
    const optional = field.required ? "" : "?";
    const tsType = field.type === "datetime" ? "string" : field.type;
    typeLines.push(`  ${name}${optional}: ${tsType};`);
  }
  typeLines.push("};", "");
}

fs.writeFileSync(path.join(outDir, "schemas.json"), JSON.stringify(schemas, null, 2));
fs.writeFileSync(path.join(outDir, "types.ts"), typeLines.join("\n"));
