import { describe, expect, it } from "vitest";
import { resolveCategoryName, resolveSubcategoryName } from "./planLabels";

const categories = [{ id: 1, name: "IT" }];
const subcategories = [{ id: 10, category_id: 1, name: "SaaS" }];

describe("planLabels", () => {
  it("returns '-' for missing rows", () => {
    expect(resolveCategoryName(undefined, categories)).toBe("-");
    expect(resolveSubcategoryName(undefined, subcategories)).toBe("-");
  });

  it("resolves names when found", () => {
    expect(resolveCategoryName({ category_id: 1 }, categories)).toBe("IT");
    expect(resolveSubcategoryName({ subcategory_id: 10 }, subcategories)).toBe("SaaS");
  });

  it("returns id when name missing", () => {
    expect(resolveCategoryName({ category_id: 99 }, categories)).toBe(99);
    expect(resolveSubcategoryName({ subcategory_id: 99 }, subcategories)).toBe(99);
  });
});
