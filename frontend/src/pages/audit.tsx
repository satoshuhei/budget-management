import { useEffect, useState } from "react";
import {
  Button,
  Card,
  CardContent,
  Stack,
  TextField,
  Typography
} from "@mui/material";
import { DataGrid, GridColDef, GridToolbar } from "@mui/x-data-grid";
import { api } from "../services/api";

interface AuditLog {
  id: number;
  actor: string;
  action: string;
  target_type: string;
  target_id: number | null;
  reason: string | null;
  detail_json: Record<string, unknown>;
  created_at: string;
}

const AuditPage = () => {
  const [rows, setRows] = useState<AuditLog[]>([]);
  const [actor, setActor] = useState("");
  const [action, setAction] = useState("");
  const [targetType, setTargetType] = useState("");

  const loadLogs = () => {
    api
      .get<AuditLog[]>("/api/audit-logs", {
        params: {
          actor: actor || undefined,
          action: action || undefined,
          target_type: targetType || undefined
        }
      })
      .then((res) => setRows(res.data))
      .catch(() => setRows([]));
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const columns: GridColDef[] = [
    { field: "created_at", headerName: "日時", width: 200 },
    { field: "actor", headerName: "ユーザー", width: 120 },
    { field: "action", headerName: "操作", width: 160 },
    { field: "target_type", headerName: "対象", width: 120 },
    { field: "target_id", headerName: "ID", width: 100 },
    { field: "reason", headerName: "理由", width: 200 }
  ];

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        監査ログ
      </Typography>

      <Card>
        <CardContent>
          <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="center">
            <TextField label="ユーザー" value={actor} onChange={(e) => setActor(e.target.value)} />
            <TextField label="操作" value={action} onChange={(e) => setAction(e.target.value)} />
            <TextField label="対象" value={targetType} onChange={(e) => setTargetType(e.target.value)} />
            <Button variant="contained" onClick={loadLogs}>
              検索
            </Button>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent sx={{ height: 520 }}>
          <DataGrid rows={rows} columns={columns} pageSizeOptions={[10, 20, 50]} slots={{ toolbar: GridToolbar }} />
        </CardContent>
      </Card>
    </Stack>
  );
};

export default AuditPage;
