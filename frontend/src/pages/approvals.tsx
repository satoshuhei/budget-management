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

const ApprovalsPage = () => {
  const { profile } = useAuth();
  const canApprove = profile?.role === "APPROVER" || profile?.role === "BUDGET_ADMIN";
  const [rows, setRows] = useState<RequestResponse[]>([]);
  const [reason, setReason] = useState("");
  const [selected, setSelected] = useState<RequestResponse | null>(null);
  const [open, setOpen] = useState(false);

  const loadInbox = () => {
    api
      .get<RequestResponse[]>("/api/approvals/inbox")
      .then((res) => setRows(res.data))
      .catch(() => setRows([]));
  };

  useEffect(() => {
    loadInbox();
  }, []);

  const handleApprove = async () => {
    if (!selected?.id || !profile) return;
    await api.post(`/api/approvals/${selected.id}/approve`, null, {
      params: { reason, approved_by: profile.username }
    });
    setOpen(false);
    setReason("");
    setSelected(null);
    loadInbox();
  };

  const handleReturn = async (id: number) => {
    await api.post(`/api/approvals/${id}/return`);
    loadInbox();
  };

  const handleReject = async (id: number) => {
    await api.post(`/api/approvals/${id}/reject`);
    loadInbox();
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
        width: 260,
        sortable: false,
        renderCell: (params) => (
          <Stack direction="row" spacing={1}>
            <Button
              size="small"
              variant="contained"
              onClick={() => {
                setSelected(params.row as RequestResponse);
                setOpen(true);
              }}
              disabled={!canApprove}
            >
              承認
            </Button>
            <Button size="small" variant="outlined" onClick={() => handleReturn(params.row.id)} disabled={!canApprove}>
              差戻し
            </Button>
            <Button
              size="small"
              color="error"
              variant="outlined"
              onClick={() => handleReject(params.row.id)}
              disabled={!canApprove}
            >
              却下
            </Button>
          </Stack>
        )
      }
    ],
    []
  );

  return (
    <Stack spacing={3}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h5" fontWeight={700}>
          承認インボックス
        </Typography>
        <Button variant="outlined" onClick={loadInbox}>
          更新
        </Button>
      </Stack>

      <Card>
        <CardContent sx={{ height: 520 }}>
          <DataGrid rows={rows} columns={columns} pageSizeOptions={[10, 20, 50]} slots={{ toolbar: GridToolbar }} />
        </CardContent>
      </Card>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>承認理由</DialogTitle>
        <DialogContent>
          <Box mt={1}>
            {selected && (
              <Stack spacing={1} mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Request ID: {selected.id}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Plan ID: {selected.plan_id ?? "計画外"}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  申請額: {formatJPY(selected.requested_amount)}
                </Typography>
              </Stack>
            )}
            <TextField
              label="理由"
              fullWidth
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>キャンセル</Button>
          <Button variant="contained" onClick={handleApprove} disabled={!reason}>
            承認する
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
};

export default ApprovalsPage;
