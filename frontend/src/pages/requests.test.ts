import { describe, expect, it } from "vitest";
import { buildRequestColumns } from "./requests";

describe("buildRequestColumns", () => {
  it("resolves plan fields with row argument", () => {
    const plans = {
      1: {
        id: 1,
        product_name: "Laptop",
        vendor: "ACME",
        planned_month: "2026-02",
        contract_type: "BUY",
        amount: "120000",
        plan_type: "CAPEX",
        note: "urgent"
      }
    };
    const columns = buildRequestColumns(true, plans, () => undefined);
    const row = { id: 10, plan_id: 1, requested_amount: "50000", status: "DRAFT" };

    const planProduct = columns.find((col) => col.field === "plan_product_name")?.valueGetter as any;
    const planId = columns.find((col) => col.field === "plan_id")?.valueGetter as any;

    expect(planProduct(undefined, row)).toBe("Laptop");
    expect(planId(undefined, row)).toBe(1);
    expect(columns[0].headerName).toBe("申請ID");
    expect(columns[1].headerName).toBe("計画ID");
  });

  it("handles missing plan safely", () => {
    const columns = buildRequestColumns(true, {}, () => undefined);
    const row = { id: 11, plan_id: null, requested_amount: "50000", status: "DRAFT" };

    const planProduct = columns.find((col) => col.field === "plan_product_name")?.valueGetter as any;
    const planId = columns.find((col) => col.field === "plan_id")?.valueGetter as any;

    expect(planProduct(undefined, row)).toBe("-");
    expect(planId(undefined, row)).toBe("計画外");
  });
});
