import { useEffect, useState } from "react";
import {
  Button,
  Card,
  CardContent,
  Grid,
  Stack,
  TextField,
  Typography
} from "@mui/material";
import { DataGrid, GridColDef, GridToolbar } from "@mui/x-data-grid";
import { api } from "../services/api";
import { formatJPY } from "../utils/currency";

interface BudgetSummaryRow {
  category_id: number;
  budget_total: string;
  commit_total: string;
  actual_total: string;
  remaining: string;
}

interface MonthlySummaryRow {
  month: string;
  plan_total: string;
  actual_total: string;
}

interface UnplannedSummary {
  count: number;
  total_amount: string;
}

const ReportsPage = () => {
  const [fiscalYear, setFiscalYear] = useState(2026);
  const [departmentId, setDepartmentId] = useState(1);
  const [budgetRows, setBudgetRows] = useState<BudgetSummaryRow[]>([]);
  const [monthlyRows, setMonthlyRows] = useState<MonthlySummaryRow[]>([]);
  const [unplanned, setUnplanned] = useState<UnplannedSummary | null>(null);

  const loadReports = () => {
    api
      .get<BudgetSummaryRow[]>("/api/reports/budget-summary", {
        params: { fiscal_year: fiscalYear, department_id: departmentId }
      })
      .then((res) => setBudgetRows(res.data))
      .catch(() => setBudgetRows([]));

    api
      .get<MonthlySummaryRow[]>("/api/reports/monthly-summary", {
        params: { fiscal_year: fiscalYear, department_id: departmentId }
      })
      .then((res) => setMonthlyRows(res.data))
      .catch(() => setMonthlyRows([]));

    api
      .get<UnplannedSummary>("/api/reports/unplanned-requests")
      .then((res) => setUnplanned(res.data))
      .catch(() => setUnplanned(null));
  };

  useEffect(() => {
    loadReports();
  }, []);

  const budgetColumns: GridColDef[] = [
    { field: "category_id", headerName: "大分類", width: 120 },
    { field: "budget_total", headerName: "予算枠", width: 140, valueFormatter: (value) => formatJPY(value) },
    { field: "commit_total", headerName: "引当", width: 120, valueFormatter: (value) => formatJPY(value) },
    { field: "actual_total", headerName: "実績", width: 120, valueFormatter: (value) => formatJPY(value) },
    { field: "remaining", headerName: "残予算", width: 120, valueFormatter: (value) => formatJPY(value) }
  ];

  const monthlyColumns: GridColDef[] = [
    { field: "month", headerName: "月", width: 120 },
    { field: "plan_total", headerName: "計画", width: 140, valueFormatter: (value) => formatJPY(value) },
    { field: "actual_total", headerName: "実績", width: 140, valueFormatter: (value) => formatJPY(value) }
  ];

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        レポート
      </Typography>

      <Card>
        <CardContent>
          <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="center">
            <TextField
              label="年度"
              type="number"
              value={fiscalYear}
              onChange={(e) => setFiscalYear(Number(e.target.value))}
            />
            <TextField
              label="部門"
              type="number"
              value={departmentId}
              onChange={(e) => setDepartmentId(Number(e.target.value))}
            />
            <Button variant="contained" onClick={loadReports}>
              更新
            </Button>
          </Stack>
        </CardContent>
      </Card>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600}>
                予算枠 vs 引当 vs 実績 vs 残
              </Typography>
              <div style={{ height: 360, marginTop: 16 }}>
                <DataGrid
                  rows={budgetRows}
                  columns={budgetColumns}
                  pageSizeOptions={[10, 20]}
                  slots={{ toolbar: GridToolbar }}
                  getRowId={(row) => row.category_id}
                />
              </div>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600}>
                月次予実
              </Typography>
              <div style={{ height: 360, marginTop: 16 }}>
                <DataGrid
                  rows={monthlyRows}
                  columns={monthlyColumns}
                  pageSizeOptions={[10, 20]}
                  slots={{ toolbar: GridToolbar }}
                  getRowId={(row) => row.month}
                />
              </div>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="subtitle1" fontWeight={600}>
            計画外申請
          </Typography>
          <Typography variant="body2" color="text.secondary">
            件数: {unplanned?.count ?? "-"} / 金額: {formatJPY(unplanned?.total_amount)}
          </Typography>
        </CardContent>
      </Card>
    </Stack>
  );
};

export default ReportsPage;
