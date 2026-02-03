import type { PlanResponse, Category, Subcategory } from "../pages/plans";

export const resolveCategoryName = (row: Partial<PlanResponse> | undefined, categories: Category[]) => {
  if (!row || row.category_id === undefined || row.category_id === null) return "-";
  const category = categories.find((c) => c.id === row.category_id);
  return category ? category.name : row.category_id;
};

export const resolveSubcategoryName = (row: Partial<PlanResponse> | undefined, subcategories: Subcategory[]) => {
  if (!row || row.subcategory_id === undefined || row.subcategory_id === null) return "-";
  const sub = subcategories.find((s) => s.id === row.subcategory_id);
  return sub ? sub.name : row.subcategory_id;
};
