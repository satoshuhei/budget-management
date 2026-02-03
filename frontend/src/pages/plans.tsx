import { useEffect, useMemo, useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogContent,
  DialogTitle,
  DialogActions,
  MenuItem,
  Stack,
  TextField,
  Typography
} from "@mui/material";
import { DataGrid, GridColDef, GridToolbar, GridColumnVisibilityModel } from "@mui/x-data-grid";
import { api } from "../services/api";
import { formatJPY } from "../utils/currency";
import { safeJsonParse } from "../utils/parse";
import { resolveCategoryName, resolveSubcategoryName } from "../utils/planLabels";

export interface PlanResponse {
  id: number;
  fiscal_year: number;
  department_id: number;
  category_id: number;
  subcategory_id: number;
  product_name: string;
  vendor: string;
  planned_month: string;
  contract_type: string;
  amount: string;
  plan_type: string;
  note: string;
  status: string;
}

export interface Category {
  id: number;
  name: string;
}

export interface Subcategory {
  id: number;
  category_id: number;
  name: string;
}

export const normalizePlannedMonth = (value: string) => {
  const trimmed = value.trim();
  const match = trimmed.match(/^(\d{4})[-/](\d{1,2})(?:[-/](\d{1,2}))?$/);
  if (!match) return trimmed;
  const month = match[2].padStart(2, "0");
  return `${match[1]}-${month}`;
};

export const isValidPlannedMonth = (value: string) => /^\d{4}[-/]\d{1,2}(?:[-/]\d{1,2})?$/.test(value.trim());

export const normalizeAmountInput = (value: string) => value.replace(/[,，￥¥\s円]/g, "").trim();

export const isValidAmountInput = (value: string) => {
  const normalized = normalizeAmountInput(value);
  if (!normalized) return false;
  return !Number.isNaN(Number(normalized));
};

export const buildPlanColumns = (
  categories: Category[],
  subcategories: Subcategory[]
): GridColDef<PlanResponse>[] => [
  { field: "id", headerName: "計画ID", width: 100 },
  { field: "planned_month", headerName: "予定月", width: 110 },
  {
    field: "category_id",
    headerName: "大分類",
    width: 140,
    valueGetter: (_value, row) => resolveCategoryName(row, categories)
  },
  {
    field: "subcategory_id",
    headerName: "小分類",
    width: 140,
    valueGetter: (_value, row) => resolveSubcategoryName(row, subcategories)
  },
  { field: "product_name", headerName: "製品/サービス", width: 180 },
  { field: "vendor", headerName: "取引先", width: 140 },
  { field: "contract_type", headerName: "契約区分", width: 120 },
  { field: "amount", headerName: "想定金額", width: 130, valueFormatter: (value) => formatJPY(value) },
  { field: "plan_type", headerName: "種別", width: 120 },
  { field: "status", headerName: "状態", width: 110 },
  { field: "note", headerName: "備考", width: 220 }
];

const PlansPage = () => {
  const [rows, setRows] = useState<PlanResponse[]>([]);
  const [filterMonth, setFilterMonth] = useState("");
  const [filterType, setFilterType] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedPlan, setSelectedPlan] = useState<PlanResponse | null>(null);
  const [importOpen, setImportOpen] = useState(false);
  const [csvText, setCsvText] = useState("");
  const [importMessage, setImportMessage] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [subcategories, setSubcategories] = useState<Subcategory[]>([]);
  const [viewName, setViewName] = useState("");
  const [savedViews, setSavedViews] = useState<Record<string, { month: string; type: string; search: string }>>(() => {
    const raw = localStorage.getItem("plans-saved-views");
    return safeJsonParse(raw, {});
  });
  const [createOpen, setCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    fiscal_year: 2026,
    department_id: 1,
    category_id: "",
    subcategory_id: "",
    product_name: "",
    vendor: "",
    planned_month: "",
    contract_type: "",
    amount: "",
    plan_type: "",
    note: ""
  });
  const [editOpen, setEditOpen] = useState(false);
  const [editForm, setEditForm] = useState({
    id: 0,
    category_id: "",
    subcategory_id: "",
    product_name: "",
    vendor: "",
    planned_month: "",
    contract_type: "",
    amount: "",
    plan_type: "",
    note: "",
    status: "ACTIVE",
    changed_by: "",
    reason: ""
  });
  const [changesOpen, setChangesOpen] = useState(false);
  const [changeLogs, setChangeLogs] = useState<Array<{ id: number; changed_by: string; reason: string; diff: Record<string, unknown>; changed_at: string }>>([]);
  const diffLabelMap: Record<string, string> = {
    product_name: "製品/サービス",
    vendor: "取引先",
    planned_month: "予定月",
    contract_type: "契約区分",
    amount: "想定金額",
    plan_type: "種別",
    note: "備考",
    status: "状態",
    category_id: "大分類",
    subcategory_id: "小分類"
  };

  const resolveDiffValue = (key: string, value: unknown) => {
    if (key === "amount") {
      return formatJPY(value as string | number | null | undefined);
    }
    if (key === "category_id") {
      const category = categories.find((c) => String(c.id) === String(value));
      return category ? category.name : String(value ?? "-");
    }
    if (key === "subcategory_id") {
      const sub = subcategories.find((s) => String(s.id) === String(value));
      return sub ? sub.name : String(value ?? "-");
    }
    return String(value ?? "-");
  };
  const [columnVisibility, setColumnVisibility] = useState<GridColumnVisibilityModel>(() => {
    const saved = localStorage.getItem("plans-column-visibility");
    return safeJsonParse(saved, {}) as GridColumnVisibilityModel;
  });

  useEffect(() => {
    api
      .get<PlanResponse[]>("/api/plans")
      .then((res) => setRows(res.data))
      .catch(() => setRows([]));

    api.get<Category[]>("/api/categories").then((res) => setCategories(res.data)).catch(() => setCategories([]));
    api.get<Subcategory[]>("/api/subcategories").then((res) => setSubcategories(res.data)).catch(() => setSubcategories([]));
  }, []);

  const filtered = useMemo(() => {
    return rows.filter((row) => {
      if (filterMonth && row.planned_month !== filterMonth) return false;
      if (filterType && row.plan_type !== filterType) return false;
      if (searchTerm) {
        const term = searchTerm.toLowerCase();
        const hay = [
          row.product_name,
          row.vendor,
          row.note,
          row.plan_type,
          row.contract_type
        ]
          .join(" ")
          .toLowerCase();
        if (!hay.includes(term)) return false;
      }
      return true;
    });
  }, [rows, filterMonth, filterType, searchTerm]);

  const columns = useMemo(
    () => buildPlanColumns(categories, subcategories),
    [categories, subcategories]
  );

  return (
    <Stack spacing={3}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h5" fontWeight={700}>
          年度計画
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button variant="outlined" onClick={() => setImportOpen(true)}>
            CSVインポート
          </Button>
          <Button variant="contained" onClick={() => setCreateOpen(true)}>
            新規計画
          </Button>
        </Stack>
      </Stack>

      <Card>
        <CardContent>
          <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="center">
            <TextField
              label="検索"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              sx={{ minWidth: 200 }}
            />
            <TextField
              label="保存ビュー名"
              value={viewName}
              onChange={(e) => setViewName(e.target.value)}
              sx={{ minWidth: 200 }}
            />
            <Button
              variant="outlined"
              onClick={() => {
                if (!viewName) return;
                const next = {
                  ...savedViews,
                  [viewName]: { month: filterMonth, type: filterType, search: searchTerm }
                };
                setSavedViews(next);
                localStorage.setItem("plans-saved-views", JSON.stringify(next));
              }}
            >
              ビュー保存
            </Button>
            <TextField
              select
              label="保存ビュー"
              value=""
              onChange={(e) => {
                const view = savedViews[e.target.value];
                if (!view) return;
                setFilterMonth(view.month);
                setFilterType(view.type);
                setSearchTerm(view.search);
              }}
              sx={{ minWidth: 180 }}
            >
              <MenuItem value="">選択</MenuItem>
              {Object.keys(savedViews).map((key) => (
                <MenuItem value={key} key={key}>
                  {key}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="予定月"
              value={filterMonth}
              onChange={(e) => setFilterMonth(e.target.value)}
              sx={{ minWidth: 160 }}
            >
              <MenuItem value="">すべて</MenuItem>
              {Array.from(new Set(rows.map((r) => r.planned_month))).map((month) => (
                <MenuItem value={month} key={month}>
                  {month}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="種別"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              sx={{ minWidth: 160 }}
            >
              <MenuItem value="">すべて</MenuItem>
              {Array.from(new Set(rows.map((r) => r.plan_type))).map((type) => (
                <MenuItem value={type} key={type}>
                  {type}
                </MenuItem>
              ))}
            </TextField>
            <Box flex={1} />
            <Chip label={`件数 ${filtered.length}`} color="primary" />
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent sx={{ height: 520 }}>
          <DataGrid
            rows={filtered}
            columns={columns}
            pageSizeOptions={[10, 20, 50]}
            slots={{ toolbar: GridToolbar }}
            columnVisibilityModel={columnVisibility}
            onColumnVisibilityModelChange={(model) => {
              setColumnVisibility(model);
              localStorage.setItem("plans-column-visibility", JSON.stringify(model));
            }}
            onRowClick={(params) => setSelectedPlan(params.row as PlanResponse)}
            onRowDoubleClick={(params) => {
              const plan = params.row as PlanResponse;
              setEditForm({
                id: plan.id,
                category_id: String(plan.category_id),
                subcategory_id: String(plan.subcategory_id),
                product_name: plan.product_name,
                vendor: plan.vendor,
                planned_month: plan.planned_month,
                contract_type: plan.contract_type,
                amount: plan.amount,
                plan_type: plan.plan_type,
                note: plan.note,
                status: plan.status,
                changed_by: "",
                reason: ""
              });
              setEditOpen(true);
            }}
          />
        </CardContent>
      </Card>

      <Dialog open={Boolean(selectedPlan)} onClose={() => setSelectedPlan(null)} maxWidth="md" fullWidth>
        <DialogTitle>計画詳細</DialogTitle>
        <DialogContent>
          {selectedPlan && (
            <Stack spacing={2} mt={1}>
              <Typography>
                大分類: {categories.find((c) => c.id === selectedPlan.category_id)?.name ?? selectedPlan.category_id}
              </Typography>
              <Typography>
                小分類: {subcategories.find((s) => s.id === selectedPlan.subcategory_id)?.name ?? selectedPlan.subcategory_id}
              </Typography>
              <Typography>製品/サービス: {selectedPlan.product_name}</Typography>
              <Typography>取引先: {selectedPlan.vendor}</Typography>
              <Typography>予定月: {selectedPlan.planned_month}</Typography>
              <Typography>契約区分: {selectedPlan.contract_type}</Typography>
              <Typography>想定金額: {formatJPY(selectedPlan.amount)}</Typography>
              <Typography>種別: {selectedPlan.plan_type}</Typography>
              <Typography>状態: {selectedPlan.status}</Typography>
              <Typography>備考: {selectedPlan.note}</Typography>
              <Stack direction="row" spacing={2}>
                <Button
                  variant="outlined"
                  onClick={async () => {
                    const res = await api.get(`/api/plans/${selectedPlan.id}/changes`);
                    setChangeLogs(res.data);
                    setChangesOpen(true);
                  }}
                >
                  変更履歴
                </Button>
                <Button
                  variant="contained"
                  onClick={() => {
                    setEditForm({
                      id: selectedPlan.id,
                      category_id: String(selectedPlan.category_id),
                      subcategory_id: String(selectedPlan.subcategory_id),
                      product_name: selectedPlan.product_name,
                      vendor: selectedPlan.vendor,
                      planned_month: selectedPlan.planned_month,
                      contract_type: selectedPlan.contract_type,
                      amount: selectedPlan.amount,
                      plan_type: selectedPlan.plan_type,
                      note: selectedPlan.note,
                      status: selectedPlan.status,
                      changed_by: "",
                      reason: ""
                    });
                    setEditOpen(true);
                  }}
                >
                  編集
                </Button>
              </Stack>
            </Stack>
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>計画編集</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <TextField
                select
                label="大分類"
                value={editForm.category_id}
                onChange={(e) =>
                  setEditForm((prev) => ({
                    ...prev,
                    category_id: e.target.value,
                    subcategory_id: ""
                  }))
                }
                sx={{ minWidth: 180 }}
                error={!editForm.category_id}
                helperText={!editForm.category_id ? "必須" : ""}
              >
                {categories.map((c) => (
                  <MenuItem value={c.id} key={c.id}>
                    {c.name}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="小分類"
                value={editForm.subcategory_id}
                onChange={(e) => setEditForm((prev) => ({ ...prev, subcategory_id: e.target.value }))}
                sx={{ minWidth: 180 }}
                disabled={!editForm.category_id}
                error={!editForm.subcategory_id}
                helperText={!editForm.subcategory_id ? "必須" : ""}
              >
                {subcategories
                  .filter((s) => String(s.category_id) === String(editForm.category_id))
                  .map((s) => (
                    <MenuItem value={s.id} key={s.id}>
                      {s.name}
                    </MenuItem>
                  ))}
              </TextField>
            </Stack>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <TextField
                label="製品/サービス"
                value={editForm.product_name}
                onChange={(e) => setEditForm((prev) => ({ ...prev, product_name: e.target.value }))}
              />
              <TextField
                label="取引先"
                value={editForm.vendor}
                onChange={(e) => setEditForm((prev) => ({ ...prev, vendor: e.target.value }))}
              />
            </Stack>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <TextField
                label="予定月(YYYY-MM)"
                value={editForm.planned_month}
                onChange={(e) => setEditForm((prev) => ({ ...prev, planned_month: e.target.value }))}
              />
              <TextField
                label="契約区分"
                value={editForm.contract_type}
                onChange={(e) => setEditForm((prev) => ({ ...prev, contract_type: e.target.value }))}
              />
              <TextField
                label="種別"
                value={editForm.plan_type}
                onChange={(e) => setEditForm((prev) => ({ ...prev, plan_type: e.target.value }))}
              />
            </Stack>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <TextField
                label="想定金額"
                value={editForm.amount}
                onChange={(e) => setEditForm((prev) => ({ ...prev, amount: e.target.value }))}
                error={Boolean(editForm.amount) && Number.isNaN(Number(editForm.amount))}
                helperText={
                  Boolean(editForm.amount) && Number.isNaN(Number(editForm.amount))
                    ? "数値を入力してください"
                    : ""
                }
              />
              <TextField
                select
                label="状態"
                value={editForm.status}
                onChange={(e) => setEditForm((prev) => ({ ...prev, status: e.target.value }))}
                sx={{ minWidth: 160 }}
              >
                {"ACTIVE,ARCHIVED".split(",").map((status) => (
                  <MenuItem key={status} value={status}>
                    {status}
                  </MenuItem>
                ))}
              </TextField>
            </Stack>
            <TextField
              label="備考"
              value={editForm.note}
              onChange={(e) => setEditForm((prev) => ({ ...prev, note: e.target.value }))}
            />
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <TextField
                label="変更者"
                value={editForm.changed_by}
                onChange={(e) => setEditForm((prev) => ({ ...prev, changed_by: e.target.value }))}
                error={!editForm.changed_by}
                helperText={!editForm.changed_by ? "必須" : ""}
              />
              <TextField
                label="理由"
                value={editForm.reason}
                onChange={(e) => setEditForm((prev) => ({ ...prev, reason: e.target.value }))}
                error={!editForm.reason}
                helperText={!editForm.reason ? "必須" : ""}
              />
            </Stack>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOpen(false)}>キャンセル</Button>
          <Button
            variant="contained"
            onClick={async () => {
              await api.put(`/api/plans/${editForm.id}`, {
                category_id: Number(editForm.category_id),
                subcategory_id: Number(editForm.subcategory_id),
                product_name: editForm.product_name,
                vendor: editForm.vendor,
                planned_month: editForm.planned_month,
                contract_type: editForm.contract_type,
                amount: Number(editForm.amount),
                plan_type: editForm.plan_type,
                note: editForm.note,
                status: editForm.status,
                changed_by: editForm.changed_by,
                reason: editForm.reason
              });
              setEditOpen(false);
              api.get<PlanResponse[]>("/api/plans").then((res) => setRows(res.data));
            }}
            disabled={
              !editForm.category_id ||
              !editForm.subcategory_id ||
              !editForm.changed_by ||
              !editForm.reason ||
              !editForm.amount ||
              Number.isNaN(Number(editForm.amount))
            }
          >
            更新
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={changesOpen} onClose={() => setChangesOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>変更履歴</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            {changeLogs.map((log) => (
              <Box key={log.id} sx={{ borderLeft: "2px solid #1e2a44", pl: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  {log.changed_at}
                </Typography>
                <Typography variant="body2">{log.changed_by}</Typography>
                <Typography variant="caption" color="text.secondary">
                  理由: {log.reason}
                </Typography>
                <Stack spacing={1} mt={1}>
                  {Object.entries((log.diff as { before?: Record<string, unknown>; after?: Record<string, unknown> }).after ?? {}).map(
                    ([key, value]) => (
                      <Box key={key}>
                        <Typography variant="caption" color="text.secondary">
                          {diffLabelMap[key] ?? key}
                        </Typography>
                        <Typography variant="body2">
                          {resolveDiffValue(key, (log.diff as { before?: Record<string, unknown> }).before?.[key])} → {resolveDiffValue(key, value)}
                        </Typography>
                      </Box>
                    )
                  )}
                </Stack>
              </Box>
            ))}
            {changeLogs.length === 0 && (
              <Typography variant="body2" color="text.secondary">
                履歴がありません
              </Typography>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setChangesOpen(false)}>閉じる</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={importOpen} onClose={() => setImportOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>CSVインポート</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <Typography variant="body2" color="text.secondary">
              ヘッダー:
              fiscal_year,department_id,category_id,subcategory_id,product_name,vendor,planned_month,contract_type,amount,plan_type,note
            </Typography>
            <TextField
              label="CSVデータ"
              multiline
              minRows={6}
              value={csvText}
              onChange={(e) => setCsvText(e.target.value)}
            />
            {importMessage && (
              <Typography variant="body2" color="primary">
                {importMessage}
              </Typography>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImportOpen(false)}>閉じる</Button>
          <Button
            variant="contained"
            onClick={async () => {
              const lines = csvText
                .split("\n")
                .map((line) => line.trim())
                .filter((line) => line.length > 0);
              if (lines.length < 2) {
                setImportMessage("CSVが空です");
                return;
              }
              const header = lines[0].split(",").map((h) => h.trim());
              const rows = lines.slice(1).map((line) => {
                const cols = line.split(",");
                const record: Record<string, string> = {};
                header.forEach((h, i) => {
                  record[h] = (cols[i] ?? "").trim();
                });
                return {
                  fiscal_year: Number(record.fiscal_year),
                  department_id: Number(record.department_id),
                  category_id: Number(record.category_id),
                  subcategory_id: Number(record.subcategory_id),
                  product_name: record.product_name,
                  vendor: record.vendor,
                  planned_month: record.planned_month,
                  contract_type: record.contract_type,
                  amount: Number(record.amount),
                  plan_type: record.plan_type,
                  note: record.note
                };
              });
              await api.post("/api/plans/bulk", { plans: rows });
              setImportMessage(`インポート完了: ${rows.length}件`);
              api.get<PlanResponse[]>("/api/plans").then((res) => setRows(res.data));
            }}
            disabled={!csvText}
          >
            取り込み
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>新規計画</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <TextField
                label="年度"
                type="number"
                value={createForm.fiscal_year}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, fiscal_year: Number(e.target.value) }))}
              />
              <TextField
                label="部門"
                type="number"
                value={createForm.department_id}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, department_id: Number(e.target.value) }))}
              />
            </Stack>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <TextField
                select
                label="大分類"
                value={createForm.category_id}
                onChange={(e) => {
                  setCreateForm((prev) => ({
                    ...prev,
                    category_id: e.target.value,
                    subcategory_id: ""
                  }));
                }}
                sx={{ minWidth: 180 }}
              >
                {categories.map((c) => (
                  <MenuItem value={c.id} key={c.id}>
                    {c.name}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="小分類"
                value={createForm.subcategory_id}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, subcategory_id: e.target.value }))}
                sx={{ minWidth: 180 }}
                disabled={!createForm.category_id}
              >
                {subcategories
                  .filter((s) => String(s.category_id) === String(createForm.category_id))
                  .map((s) => (
                    <MenuItem value={s.id} key={s.id}>
                      {s.name}
                    </MenuItem>
                  ))}
              </TextField>
            </Stack>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <TextField
                label="製品/サービス"
                value={createForm.product_name}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, product_name: e.target.value }))}
                error={!createForm.product_name}
                helperText={!createForm.product_name ? "必須" : ""}
              />
              <TextField
                label="取引先"
                value={createForm.vendor}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, vendor: e.target.value }))}
                error={!createForm.vendor}
                helperText={!createForm.vendor ? "必須" : ""}
              />
            </Stack>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <TextField
                label="予定月(YYYY-MM)"
                value={createForm.planned_month}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, planned_month: e.target.value }))}
                error={!isValidPlannedMonth(createForm.planned_month)}
                helperText={!isValidPlannedMonth(createForm.planned_month) ? "YYYY-MM 形式(YYYY/M, YYYY/MM, YYYY-MM-DDも可)" : ""}
              />
              <TextField
                label="契約区分"
                value={createForm.contract_type}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, contract_type: e.target.value }))}
                error={!createForm.contract_type}
                helperText={!createForm.contract_type ? "必須" : ""}
              />
              <TextField
                label="種別"
                value={createForm.plan_type}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, plan_type: e.target.value }))}
                error={!createForm.plan_type}
                helperText={!createForm.plan_type ? "必須" : ""}
              />
            </Stack>
            <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
              <TextField
                label="想定金額"
                value={createForm.amount}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, amount: e.target.value }))}
                error={Boolean(createForm.amount) && !isValidAmountInput(createForm.amount)}
                helperText={
                  Boolean(createForm.amount) && !isValidAmountInput(createForm.amount)
                    ? "数値を入力してください (カンマ/円/￥可)"
                    : ""
                }
              />
              <TextField
                label="備考"
                value={createForm.note}
                onChange={(e) => setCreateForm((prev) => ({ ...prev, note: e.target.value }))}
              />
            </Stack>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)}>キャンセル</Button>
          <Button
            variant="contained"
            onClick={async () => {
              const plannedMonth = normalizePlannedMonth(createForm.planned_month);
              const amount = Number(normalizeAmountInput(createForm.amount));
              await api.post("/api/plans", {
                fiscal_year: createForm.fiscal_year,
                department_id: createForm.department_id,
                category_id: Number(createForm.category_id),
                subcategory_id: Number(createForm.subcategory_id),
                product_name: createForm.product_name,
                vendor: createForm.vendor,
                planned_month: plannedMonth,
                contract_type: createForm.contract_type,
                amount,
                plan_type: createForm.plan_type,
                note: createForm.note
              });
              setCreateOpen(false);
              setCreateForm({
                fiscal_year: 2026,
                department_id: 1,
                category_id: "",
                subcategory_id: "",
                product_name: "",
                vendor: "",
                planned_month: "",
                contract_type: "",
                amount: "",
                plan_type: "",
                note: ""
              });
              api.get<PlanResponse[]>("/api/plans").then((res) => setRows(res.data));
            }}
            disabled={(() => {
              const amountValue = createForm.amount.trim();
              return (
                !createForm.category_id ||
                !createForm.subcategory_id ||
                !createForm.product_name.trim() ||
                !createForm.vendor.trim() ||
                !isValidPlannedMonth(createForm.planned_month) ||
                !createForm.contract_type.trim() ||
                !amountValue ||
                !isValidAmountInput(createForm.amount) ||
                !createForm.plan_type.trim()
              );
            })()}
          >
            作成
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
};

export default PlansPage;
