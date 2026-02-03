import { useCallback, useEffect, useMemo, useState } from "react";
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

interface Category {
  id: number;
  name: string;
}

interface Subcategory {
  id: number;
  category_id: number;
  name: string;
}

const MasterPage = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [subcategories, setSubcategories] = useState<Subcategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("");

  const [categoryName, setCategoryName] = useState("");
  const [subName, setSubName] = useState("");
  const [subCategoryId, setSubCategoryId] = useState("");

  const [editCategory, setEditCategory] = useState<Category | null>(null);
  const [editSub, setEditSub] = useState<Subcategory | null>(null);

  const loadAll = useCallback(() => {
    api.get<Category[]>("/api/categories").then((res) => setCategories(res.data));
    api
      .get<Subcategory[]>("/api/subcategories", {
        params: selectedCategory ? { category_id: selectedCategory } : undefined
      })
      .then((res) => setSubcategories(res.data));
  }, [selectedCategory]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const categoryColumns: GridColDef[] = useMemo(
    () => [
      { field: "id", headerName: "ID", width: 80 },
      { field: "name", headerName: "大分類名", width: 200 },
      {
        field: "actions",
        headerName: "操作",
        width: 200,
        sortable: false,
        renderCell: (params) => (
          <Stack direction="row" spacing={1}>
            <Button size="small" variant="outlined" onClick={() => setEditCategory(params.row as Category)}>
              編集
            </Button>
            <Button
              size="small"
              color="error"
              variant="outlined"
              onClick={async () => {
                await api.delete(`/api/categories/${params.row.id}`);
                loadAll();
              }}
            >
              削除
            </Button>
          </Stack>
        )
      }
    ],
    [loadAll]
  );

  const subColumns: GridColDef[] = useMemo(
    () => [
      { field: "id", headerName: "ID", width: 80 },
      {
        field: "category_id",
        headerName: "大分類",
        width: 160,
        valueGetter: (params) => {
          const category = categories.find((c) => c.id === params.row.category_id);
          return category ? category.name : params.row.category_id;
        }
      },
      { field: "name", headerName: "小分類名", width: 200 },
      {
        field: "actions",
        headerName: "操作",
        width: 200,
        sortable: false,
        renderCell: (params) => (
          <Stack direction="row" spacing={1}>
            <Button size="small" variant="outlined" onClick={() => setEditSub(params.row as Subcategory)}>
              編集
            </Button>
            <Button
              size="small"
              color="error"
              variant="outlined"
              onClick={async () => {
                await api.delete(`/api/subcategories/${params.row.id}`);
                loadAll();
              }}
            >
              削除
            </Button>
          </Stack>
        )
      }
    ],
    [categories, loadAll]
  );

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        マスタ管理
      </Typography>

      <Card>
        <CardContent>
          <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="center">
            <TextField
              label="大分類名"
              value={categoryName}
              onChange={(e) => setCategoryName(e.target.value)}
            />
            <Button
              variant="contained"
              onClick={async () => {
                await api.post("/api/categories", { name: categoryName });
                setCategoryName("");
                loadAll();
              }}
              disabled={!categoryName}
            >
              大分類追加
            </Button>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="center">
            <TextField
              select
              label="大分類"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              sx={{ minWidth: 180 }}
            >
              <MenuItem value="">すべて</MenuItem>
              {categories.map((c) => (
                <MenuItem value={c.id} key={c.id}>
                  {c.name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="大分類（追加）"
              value={subCategoryId}
              onChange={(e) => setSubCategoryId(e.target.value)}
              sx={{ minWidth: 180 }}
            >
              {categories.map((c) => (
                <MenuItem value={c.id} key={c.id}>
                  {c.name}
                </MenuItem>
              ))}
            </TextField>
            <TextField label="小分類名" value={subName} onChange={(e) => setSubName(e.target.value)} />
            <Button
              variant="contained"
              onClick={async () => {
                await api.post("/api/subcategories", {
                  category_id: Number(subCategoryId),
                  name: subName
                });
                setSubName("");
                loadAll();
              }}
              disabled={!subName || !subCategoryId}
            >
              小分類追加
            </Button>
          </Stack>
        </CardContent>
      </Card>

      <Box>
        <Typography variant="subtitle1" fontWeight={600}>
          大分類一覧
        </Typography>
        <Card sx={{ mt: 1 }}>
          <CardContent sx={{ height: 300 }}>
            <DataGrid rows={categories} columns={categoryColumns} pageSizeOptions={[5, 10]} slots={{ toolbar: GridToolbar }} />
          </CardContent>
        </Card>
      </Box>

      <Box>
        <Typography variant="subtitle1" fontWeight={600}>
          小分類一覧
        </Typography>
        <Card sx={{ mt: 1 }}>
          <CardContent sx={{ height: 300 }}>
            <DataGrid
              rows={subcategories}
              columns={subColumns}
              pageSizeOptions={[5, 10]}
              slots={{ toolbar: GridToolbar }}
            />
          </CardContent>
        </Card>
      </Box>

      <Dialog open={Boolean(editCategory)} onClose={() => setEditCategory(null)}>
        <DialogTitle>大分類編集</DialogTitle>
        <DialogContent>
          <TextField
            label="大分類名"
            value={editCategory?.name ?? ""}
            onChange={(e) => setEditCategory((prev) => (prev ? { ...prev, name: e.target.value } : prev))}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditCategory(null)}>キャンセル</Button>
          <Button
            variant="contained"
            onClick={async () => {
              if (!editCategory) return;
              await api.put(`/api/categories/${editCategory.id}`, { name: editCategory.name });
              setEditCategory(null);
              loadAll();
            }}
          >
            保存
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(editSub)} onClose={() => setEditSub(null)}>
        <DialogTitle>小分類編集</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField
              select
              label="大分類"
              value={editSub?.category_id ?? ""}
              onChange={(e) => setEditSub((prev) => (prev ? { ...prev, category_id: Number(e.target.value) } : prev))}
            >
              {categories.map((c) => (
                <MenuItem value={c.id} key={c.id}>
                  {c.name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="小分類名"
              value={editSub?.name ?? ""}
              onChange={(e) => setEditSub((prev) => (prev ? { ...prev, name: e.target.value } : prev))}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditSub(null)}>キャンセル</Button>
          <Button
            variant="contained"
            onClick={async () => {
              if (!editSub) return;
              await api.put(`/api/subcategories/${editSub.id}`, {
                category_id: editSub.category_id,
                name: editSub.name
              });
              setEditSub(null);
              loadAll();
            }}
          >
            保存
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
};

export default MasterPage;
