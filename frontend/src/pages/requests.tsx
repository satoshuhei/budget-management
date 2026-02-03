import { useEffect, useMemo, useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Stack,
  TextField,
  Typography
} from "@mui/material";
import { DataGrid, GridColDef, GridToolbar } from "@mui/x-data-grid";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { formatJPY } from "../utils/currency";

interface RequestResponse {
  id: number;
  plan_id: number | null;
  requested_amount: string;
  status: string;
}

interface PlanResponse {
  id: number;
  product_name: string;
  vendor: string;
  planned_month: string;
  contract_type: string;
  amount: string;
  plan_type: string;
  note: string;
}

interface AuditLog {
  id: number;
  actor: string;
  action: string;
  reason: string | null;
  created_at: string;
}

const RequestsPage = () => {
  const { profile } = useAuth();
  const canRequest = profile?.role === "USER" || profile?.role === "BUDGET_ADMIN";
  const statusColor = (status: string) => {
    if (status === "APPROVED") return "success";
    if (status === "SUBMITTED") return "info";
    if (status === "RETURNED") return "warning";
    if (status === "REJECTED") return "error";
    return "default";
  };
  const [rows, setRows] = useState<RequestResponse[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [open, setOpen] = useState(false);
  const [planId, setPlanId] = useState("");
  const [amount, setAmount] = useState("");
  const [reason, setReason] = useState("");
  const [detailOpen, setDetailOpen] = useState(false);
  const [selected, setSelected] = useState<RequestResponse | null>(null);
  const [planDetail, setPlanDetail] = useState<PlanResponse | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);

  const loadRequests = () => {
    api
      .get<RequestResponse[]>("/api/requests", {
        params: statusFilter ? { status: statusFilter } : undefined
      })
      .then((res) => setRows(res.data))
      .catch(() => setRows([]));
  };

  useEffect(() => {
    loadRequests();
  }, [statusFilter]);

  const handleCreate = async () => {
    if (!profile) return;
    await api.post("/api/requests", {
      plan_id: planId ? Number(planId) : null,
      requested_amount: Number(amount),
      created_by: profile.username,
      reason
    });
    setOpen(false);
    setPlanId("");
    setAmount("");
    setReason("");
    loadRequests();
  };

  const handleSubmit = async (id: number) => {
    await api.post(`/api/requests/${id}/submit`);
    loadRequests();
  };

  const loadDetail = async (row: RequestResponse) => {
    setSelected(row);
    setDetailOpen(true);
    setPlanDetail(null);
    setAuditLogs([]);

    if (row.plan_id) {
      api.get<PlanResponse>(`/api/plans/${row.plan_id}`).then((res) => setPlanDetail(res.data));
    }

    if (profile?.role === "AUDITOR" || profile?.role === "BUDGET_ADMIN") {
      api
        .get<AuditLog[]>("/api/audit-logs", {
          params: { target_type: "Request", target_id: row.id }
        })
        .then((res) => setAuditLogs(res.data));
    }
  };

  const columns: GridColDef[] = useMemo(
    () => [
      { field: "id", headerName: "ID", width: 90 },
      { field: "plan_id", headerName: "Plan", width: 120 },
      { field: "requested_amount", headerName: "申請額", width: 140, valueFormatter: (value) => formatJPY(value) },
      { field: "status", headerName: "状態", width: 120 },
      {
        field: "actions",
        headerName: "アクション",
        width: 180,
        sortable: false,
        renderCell: (params) => (
          <Button
            size="small"
            variant="contained"
            disabled={params.row.status !== "DRAFT" || !canRequest}
            onClick={() => handleSubmit(params.row.id)}
          >
            提出
          </Button>
        )
      }
    ],
    []
  );

  return (
    <Stack spacing={3}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h5" fontWeight={700}>
          申請
        </Typography>
        <Stack direction="row" spacing={2}>
          <TextField
            select
            label="ステータス"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            sx={{ minWidth: 160 }}
          >
            <MenuItem value="">すべて</MenuItem>
            {["DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "RETURNED"].map((status) => (
              <MenuItem value={status} key={status}>
                {status}
              </MenuItem>
            ))}
          </TextField>
          <Button variant="contained" onClick={() => setOpen(true)} disabled={!canRequest}>
            新規申請
          </Button>
        </Stack>
      </Stack>

      <Card>
        <CardContent sx={{ height: 520 }}>
          <DataGrid
            rows={rows}
            columns={columns}
            pageSizeOptions={[10, 20, 50]}
            slots={{ toolbar: GridToolbar }}
            onRowClick={(params) => loadDetail(params.row as RequestResponse)}
          />
        </CardContent>
      </Card>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>新規申請</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField
              label="Plan ID (任意)"
              value={planId}
              onChange={(e) => setPlanId(e.target.value)}
            />
            <TextField label="申請額" value={amount} onChange={(e) => setAmount(e.target.value)} />
            <TextField label="理由" value={reason} onChange={(e) => setReason(e.target.value)} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>キャンセル</Button>
          <Button variant="contained" onClick={handleCreate} disabled={!amount || !reason || !canRequest}>
            作成
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>申請詳細</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <Typography>申請ID: {selected?.id}</Typography>
            <Typography>Plan ID: {selected?.plan_id ?? "計画外"}</Typography>
            <Typography>申請額: {formatJPY(selected?.requested_amount)}</Typography>
            <Typography>状態: {selected?.status}</Typography>
            <Box>
              <Typography variant="caption" color="text.secondary">
                ステータス
              </Typography>
              <Box mt={0.5}>
                <Button variant="outlined" size="small" color={statusColor(selected?.status ?? "")}>
                  {selected?.status ?? "-"}
                </Button>
              </Box>
            </Box>
            {planDetail && (
              <Box>
                <Typography variant="subtitle2" mt={2}>
                  計画情報
                </Typography>
                <Typography>製品/サービス: {planDetail.product_name}</Typography>
                <Typography>取引先: {planDetail.vendor}</Typography>
                <Typography>予定月: {planDetail.planned_month}</Typography>
                <Typography>契約区分: {planDetail.contract_type}</Typography>
                <Typography>想定金額: {formatJPY(planDetail.amount)}</Typography>
                <Typography>種別: {planDetail.plan_type}</Typography>
                <Typography>備考: {planDetail.note}</Typography>
              </Box>
            )}
            {(profile?.role === "AUDITOR" || profile?.role === "BUDGET_ADMIN") && (
              <Box>
                <Typography variant="subtitle2" mt={2}>
                  監査ログ
                </Typography>
                <Stack spacing={1} mt={1}>
                  {auditLogs.map((log) => (
                    <Box key={log.id} sx={{ borderLeft: "2px solid #1e2a44", pl: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        {log.created_at}
                      </Typography>
                      <Typography variant="body2">
                        {log.action} / {log.actor}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        理由: {log.reason ?? "-"}
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </Box>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailOpen(false)}>閉じる</Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
};

export default RequestsPage;
