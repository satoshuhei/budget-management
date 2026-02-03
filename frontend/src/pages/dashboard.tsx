import { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Grid,
  Stack,
  Typography,
  Chip,
  LinearProgress
} from "@mui/material";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { formatJPY } from "../utils/currency";

export interface SummaryResponse {
  budget_total: string;
  plan_total: string;
}

interface AuditLog {
  id: number;
  actor: string;
  action: string;
  target_type: string;
  target_id: number | null;
  reason: string | null;
  created_at: string;
}

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

interface Category {
  id: number;
  name: string;
}

export const buildSummaryCards = (summary: SummaryResponse | null) => [
  { label: "予算枠合計", value: formatJPY(summary?.budget_total) },
  { label: "計画合計", value: formatJPY(summary?.plan_total) },
  { label: "引当合計", value: "-" },
  { label: "実績合計", value: "-" },
  { label: "残予算", value: "-" }
];

const DashboardPage = () => {
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [budgetSummary, setBudgetSummary] = useState<BudgetSummaryRow[]>([]);
  const [monthlySummary, setMonthlySummary] = useState<MonthlySummaryRow[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const { profile } = useAuth();

  useEffect(() => {
    api
      .get<SummaryResponse>("/api/dashboard/summary", {
        params: { fiscal_year: 2026, department_id: 1 }
      })
      .then((res) => setSummary(res.data))
      .catch(() => setSummary(null));

    api
      .get<BudgetSummaryRow[]>("/api/reports/budget-summary", {
        params: { fiscal_year: 2026, department_id: 1 }
      })
      .then((res) => setBudgetSummary(res.data))
      .catch(() => setBudgetSummary([]));

    api
      .get<MonthlySummaryRow[]>("/api/reports/monthly-summary", {
        params: { fiscal_year: 2026, department_id: 1 }
      })
      .then((res) => setMonthlySummary(res.data))
      .catch(() => setMonthlySummary([]));

    api
      .get<Category[]>("/api/categories")
      .then((res) => setCategories(res.data))
      .catch(() => setCategories([]));

    if (profile?.role === "AUDITOR" || profile?.role === "BUDGET_ADMIN") {
      api
        .get<AuditLog[]>("/api/audit-logs/recent", { params: { limit: 8 } })
        .then((res) => setLogs(res.data))
        .catch(() => setLogs([]));
    }
  }, []);

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        ダッシュボード
      </Typography>
      <Grid container spacing={2}>
        {buildSummaryCards(summary).map((item) => (
          <Grid item xs={12} md={4} lg={2.4} key={item.label}>
            <Card>
              <CardContent>
                <Typography variant="caption" color="text.secondary">
                  {item.label}
                </Typography>
                <Typography variant="h6" fontWeight={700}>
                  {item.value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600}>
                大分類別サマリ
              </Typography>
              <Stack spacing={2} mt={2}>
                {budgetSummary.map((row) => {
                  const remaining = Number(row.remaining);
                  const total = Number(row.budget_total || 0);
                  const used = total > 0 ? ((total - remaining) / total) * 100 : 0;
                  const categoryName = categories.find((c) => c.id === row.category_id)?.name;
                  return (
                    <Box key={row.category_id}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2">
                          {categoryName ?? "カテゴリ"} {row.category_id}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          残予算 {formatJPY(row.remaining)}
                        </Typography>
                      </Stack>
                      <LinearProgress variant="determinate" value={used} sx={{ mt: 1 }} />
                    </Box>
                  );
                })}
                {budgetSummary.length === 0 && (
                  <Typography variant="body2" color="text.secondary">
                    サマリがありません
                  </Typography>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600}>
                月次予実（簡易チャート）
              </Typography>
              <Stack spacing={2} mt={2}>
                {monthlySummary.map((row) => {
                  const plan = Number(row.plan_total || 0);
                  const actual = Number(row.actual_total || 0);
                  const ratio = plan > 0 ? (actual / plan) * 100 : 0;
                  return (
                    <Box key={row.month}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2">{row.month}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          実績 {formatJPY(row.actual_total)} / 計画 {formatJPY(row.plan_total)}
                        </Typography>
                      </Stack>
                      <LinearProgress variant="determinate" value={Math.min(ratio, 100)} sx={{ mt: 1 }} />
                    </Box>
                  );
                })}
                {monthlySummary.length === 0 && (
                  <Typography variant="body2" color="text.secondary">
                    月次データがありません
                  </Typography>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {(profile?.role === "AUDITOR" || profile?.role === "BUDGET_ADMIN") && (
        <Box>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600}>
                最近の操作ログ
              </Typography>
              <Stack spacing={1} mt={2}>
                {logs.map((log) => (
                  <Box key={log.id} sx={{ display: "flex", gap: 2, alignItems: "center" }}>
                    <Chip size="small" label={log.action} color="primary" />
                    <Typography variant="body2" color="text.secondary">
                      {log.actor} / {log.target_type} #{log.target_id ?? "-"}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {log.created_at}
                    </Typography>
                  </Box>
                ))}
                {logs.length === 0 && (
                  <Typography variant="body2" color="text.secondary">
                    監査ログがありません
                  </Typography>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Box>
      )}
    </Stack>
  );
};

export default DashboardPage;
