import { describe, expect, it } from "vitest";
import { buildExecutionColumns } from "./executions";

describe("buildExecutionColumns", () => {
  it("resolves plan fields via request mapping", () => {
    const plans = {
      1: {
        id: 1,
        product_name: "Service",
        vendor: "VendorA",
        planned_month: "2026-03",
        contract_type: "SUBSCRIPTION",
        amount: "30000",
        plan_type: "OPEX",
        note: "monthly"
      }
    };
    const requests = {
      20: { id: 20, plan_id: 1, requested_amount: "30000", status: "APPROVED" }
    };
    const columns = buildExecutionColumns(plans, requests);
    const row = { id: 99, request_id: 20, status: "ORDERED", actual_amount: null };

    const planVendor = columns.find((col) => col.field === "plan_vendor")?.valueGetter as any;
    const planId = columns.find((col) => col.field === "plan_id")?.valueGetter as any;

    expect(planVendor(undefined, row)).toBe("VendorA");
    expect(planId(undefined, row)).toBe(1);
    expect(columns[0].headerName).toBe("執行ID");
    expect(columns[1].headerName).toBe("申請ID");
    expect(columns[2].headerName).toBe("計画ID");
  });

  it("handles missing request or plan safely", () => {
    const columns = buildExecutionColumns({}, {});
    const row = { id: 100, request_id: 999, status: "ORDERED", actual_amount: null };

    const planProduct = columns.find((col) => col.field === "plan_product_name")?.valueGetter as any;
    const planId = columns.find((col) => col.field === "plan_id")?.valueGetter as any;

    expect(planProduct(undefined, row)).toBe("-");
    expect(planId(undefined, row)).toBe("計画外");
  });
});
