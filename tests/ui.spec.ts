import { test, expect } from "@playwright/test";

test("UI flow submits an observation", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Username").fill("patient-ui");
  await page.getByLabel("Password").fill("demo");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page.getByText("Submit symptom score")).toBeVisible();
});
