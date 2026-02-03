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

interface ExecutionResponse {
  id: number;
  request_id: number;
  status: string;
  actual_amount: string | null;
}

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

const ExecutionsPage = () => {
  const { profile } = useAuth();
  const [rows, setRows] = useState<ExecutionResponse[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [requestId, setRequestId] = useState("");
  const [executionId, setExecutionId] = useState("");
  const [actualAmount, setActualAmount] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [selected, setSelected] = useState<ExecutionResponse | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [requestDetail, setRequestDetail] = useState<RequestResponse | null>(null);
  const [planDetail, setPlanDetail] = useState<PlanResponse | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const canOperate = profile?.role === "USER" || profile?.role === "BUDGET_ADMIN";

  const statusColor = (status: string) => {
    if (status === "PAID") return "success";
    if (status === "INVOICED") return "info";
    if (status === "DELIVERED") return "secondary";
    if (status === "ORDERED") return "warning";
    return "default";
  };

  const loadExecutions = () => {
    api
      .get<ExecutionResponse[]>("/api/executions", {
        params: statusFilter ? { status: statusFilter } : undefined
      })
      .then((res) => setRows(res.data))
      .catch(() => setRows([]));
  };

  useEffect(() => {
    loadExecutions();
  }, [statusFilter]);

  const handleCreate = async () => {
    setMessage(null);
    const res = await api.post("/api/executions", { request_id: Number(requestId) });
    setExecutionId(String(res.data.id));
    setMessage(`執行を作成しました (ID: ${res.data.id})`);
    loadExecutions();
  };

  const handleStatus = async (action: string) => {
    setMessage(null);
    await api.post(`/api/executions/${executionId}/${action}`);
    setMessage(`ステータスを更新しました (${action})`);
    loadExecutions();
  };

  const handlePaid = async () => {
    setMessage(null);
    await api.post(`/api/executions/${executionId}/set-paid`, {
      actual_amount: Number(actualAmount),
      allow_over: false,
      reason: "paid",
      paid_by: profile?.username ?? "system"
    });
    setMessage("支払完了を登録しました");
    loadExecutions();
  };

  const columns: GridColDef[] = useMemo(
    () => [
      { field: "id", headerName: "ID", width: 90 },
      { field: "request_id", headerName: "Request", width: 120 },
      { field: "status", headerName: "状態", width: 130 },
      { field: "actual_amount", headerName: "実績", width: 120, valueFormatter: (value) => formatJPY(value) }
    ],
    []
  );

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        執行
      </Typography>

      <Card>
        <CardContent>
          <Stack spacing={2}>
            <Typography variant="subtitle1" fontWeight={600}>
              執行の作成
            </Typography>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <TextField
                label="Request ID"
                value={requestId}
                onChange={(e) => setRequestId(e.target.value)}
              />
              <Button variant="contained" onClick={handleCreate} disabled={!requestId}>
                作成
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Stack spacing={2}>
            <Typography variant="subtitle1" fontWeight={600}>
              ステータス更新
            </Typography>
            <TextField
              label="Execution ID"
              value={executionId}
              onChange={(e) => setExecutionId(e.target.value)}
            />
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <Button variant="outlined" onClick={() => handleStatus("set-ordered")} disabled={!executionId}>
                発注
              </Button>
              <Button variant="outlined" onClick={() => handleStatus("set-delivered")} disabled={!executionId}>
                納品
              </Button>
              <Button variant="outlined" onClick={() => handleStatus("set-invoiced")} disabled={!executionId}>
                請求
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Stack spacing={2}>
            <Typography variant="subtitle1" fontWeight={600}>
              支払完了
            </Typography>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <TextField
                label="Execution ID"
                value={executionId}
                onChange={(e) => setExecutionId(e.target.value)}
              />
              <TextField
                label="実績金額"
                value={actualAmount}
                onChange={(e) => setActualAmount(e.target.value)}
              />
              <Button variant="contained" onClick={handlePaid} disabled={!executionId || !actualAmount}>
                支払完了
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      {message && (
        <Box>
          <Typography color="text.secondary">{message}</Typography>
        </Box>
      )}

      <Card>
        <CardContent>
          <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="center">
            <TextField
              select
              label="ステータス"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              sx={{ minWidth: 160 }}
            >
              <MenuItem value="">すべて</MenuItem>
              {["NOT_STARTED", "ORDERED", "DELIVERED", "INVOICED", "PAID", "CANCELED"].map((status) => (
                <MenuItem value={status} key={status}>
                  {status}
                </MenuItem>
              ))}
            </TextField>
            <Button variant="outlined" onClick={loadExecutions}>
              更新
            </Button>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent sx={{ height: 520 }}>
          <DataGrid
            rows={rows}
            columns={columns}
            pageSizeOptions={[10, 20, 50]}
            slots={{ toolbar: GridToolbar }}
            onRowClick={(params) => {
              setSelected(params.row as ExecutionResponse);
              setExecutionId(String(params.row.id));
              setRequestDetail(null);
              setPlanDetail(null);
              setAuditLogs([]);
              setModalOpen(true);
              api.get<RequestResponse>(`/api/requests/${params.row.request_id}`).then((res) => {
                setRequestDetail(res.data);
                if (res.data.plan_id) {
                  api.get<PlanResponse>(`/api/plans/${res.data.plan_id}`).then((planRes) => {
                    setPlanDetail(planRes.data);
                  });
                }
              });
              if (profile?.role === "AUDITOR" || profile?.role === "BUDGET_ADMIN") {
                api
                  .get<AuditLog[]>("/api/audit-logs", {
                    params: { target_type: "Execution", target_id: params.row.id }
                  })
                  .then((res) => setAuditLogs(res.data));
              }
            }}
          />
        </CardContent>
      </Card>

      <Dialog open={modalOpen} onClose={() => setModalOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>執行詳細</DialogTitle>
        <DialogContent>
          {selected && (
            <Stack spacing={2} mt={1}>
              <Typography variant="body2" color="text.secondary">
                Execution ID: {selected.id}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Request ID: {selected.request_id}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                状態: {selected.status}
              </Typography>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  ステータス
                </Typography>
                <Box mt={0.5}>
                  <Button variant="outlined" size="small" color={statusColor(selected.status)}>
                    {selected.status}
                  </Button>
                </Box>
              </Box>
              {requestDetail && (
                <Box>
                  <Typography variant="subtitle2" mt={1}>
                    申請情報
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    申請額: {formatJPY(requestDetail.requested_amount)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    申請状態: {requestDetail.status}
                  </Typography>
                </Box>
              )}
              {planDetail && (
                <Box>
                  <Typography variant="subtitle2" mt={1}>
                    計画情報
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    製品/サービス: {planDetail.product_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    取引先: {planDetail.vendor}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    予定月: {planDetail.planned_month}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    契約区分: {planDetail.contract_type}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    種別: {planDetail.plan_type}
                  </Typography>
                </Box>
              )}
              <TextField
                label="実績金額"
                value={actualAmount}
                onChange={(e) => setActualAmount(e.target.value)}
              />
              <Stack direction={{ xs: "column", md: "row" }} spacing={1}>
                <Button variant="outlined" onClick={() => handleStatus("set-ordered")} disabled={!canOperate}>
                  発注
                </Button>
                <Button variant="outlined" onClick={() => handleStatus("set-delivered")} disabled={!canOperate}>
                  納品
                </Button>
                <Button variant="outlined" onClick={() => handleStatus("set-invoiced")} disabled={!canOperate}>
                  請求
                </Button>
                <Button variant="contained" onClick={handlePaid} disabled={!actualAmount || !canOperate}>
                  支払完了
                </Button>
              </Stack>
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
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setModalOpen(false)}>閉じる</Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
};

export default ExecutionsPage;
