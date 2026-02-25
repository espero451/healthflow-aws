export type FieldType = "string" | "number" | "datetime";

export type FieldDef = {
  type: FieldType;
  required: boolean;
  description?: string;
};

export type ModelDef = {
  name: string;
  fields: Record<string, FieldDef>;
};

export function stringField(options: Partial<FieldDef> = {}): FieldDef {
  return { type: "string", required: true, ...options };
}

export function numberField(options: Partial<FieldDef> = {}): FieldDef {
  return { type: "number", required: true, ...options };
}

export function datetimeField(options: Partial<FieldDef> = {}): FieldDef {
  return { type: "datetime", required: true, ...options };
}

export function model(name: string, fields: Record<string, FieldDef>): ModelDef {
  return { name, fields };
}
