import { Outlet, useNavigate } from "react-router-dom";
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  InputBase,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Toolbar,
  Typography
} from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import TableChartIcon from "@mui/icons-material/TableChart";
import LogoutIcon from "@mui/icons-material/Logout";
import SearchIcon from "@mui/icons-material/Search";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import FactCheckIcon from "@mui/icons-material/FactCheck";
import AssessmentIcon from "@mui/icons-material/Assessment";
import HistoryIcon from "@mui/icons-material/History";
import AssignmentIcon from "@mui/icons-material/Assignment";
import SettingsIcon from "@mui/icons-material/Settings";
import { useAuth } from "../hooks/useAuth";

const drawerWidth = 240;

const Layout = () => {
  const navigate = useNavigate();
  const { logout, profile } = useAuth();
  const role = profile?.role;
  const canApprove = role === "APPROVER" || role === "BUDGET_ADMIN";
  const canAudit = role === "AUDITOR" || role === "BUDGET_ADMIN";
  const canMaster = role === "BUDGET_ADMIN";

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar sx={{ gap: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            Budget Management
          </Typography>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              bgcolor: "rgba(255,255,255,0.08)",
              px: 2,
              py: 0.5,
              borderRadius: 2,
              flex: 1,
              maxWidth: 520
            }}
          >
            <SearchIcon sx={{ mr: 1, color: "text.secondary" }} />
            <InputBase placeholder="検索…" fullWidth sx={{ color: "text.primary" }} />
          </Box>
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="body2" color="text.secondary">
              {profile?.username} ({profile?.role})
            </Typography>
            <IconButton color="inherit" onClick={() => logout()}>
              <LogoutIcon />
            </IconButton>
          </Stack>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            boxSizing: "border-box",
            bgcolor: "#0f1726"
          }
        }}
      >
        <Toolbar />
        <List>
          <ListItemButton onClick={() => navigate("/")}
            sx={{
              borderLeft: "3px solid transparent",
              "&.Mui-selected": { borderLeftColor: "primary.main" }
            }}
          >
            <ListItemIcon>
              <DashboardIcon />
            </ListItemIcon>
            <ListItemText primary="ダッシュボード" />
          </ListItemButton>
          <ListItemButton onClick={() => navigate("/plans")}
            sx={{
              borderLeft: "3px solid transparent",
              "&.Mui-selected": { borderLeftColor: "primary.main" }
            }}
          >
            <ListItemIcon>
              <TableChartIcon />
            </ListItemIcon>
            <ListItemText primary="年度計画" />
          </ListItemButton>
          <ListItemButton onClick={() => navigate("/requests")}
            sx={{
              borderLeft: "3px solid transparent",
              "&.Mui-selected": { borderLeftColor: "primary.main" }
            }}
          >
            <ListItemIcon>
              <AssignmentIcon />
            </ListItemIcon>
            <ListItemText primary="申請" />
          </ListItemButton>
          {canApprove && (
            <ListItemButton onClick={() => navigate("/approvals")}
              sx={{
                borderLeft: "3px solid transparent",
                "&.Mui-selected": { borderLeftColor: "primary.main" }
              }}
            >
              <ListItemIcon>
                <CheckCircleIcon />
              </ListItemIcon>
              <ListItemText primary="承認" />
            </ListItemButton>
          )}
          <ListItemButton onClick={() => navigate("/executions")}
            sx={{
              borderLeft: "3px solid transparent",
              "&.Mui-selected": { borderLeftColor: "primary.main" }
            }}
          >
            <ListItemIcon>
              <FactCheckIcon />
            </ListItemIcon>
            <ListItemText primary="執行" />
          </ListItemButton>
          <ListItemButton onClick={() => navigate("/reports")}
            sx={{
              borderLeft: "3px solid transparent",
              "&.Mui-selected": { borderLeftColor: "primary.main" }
            }}
          >
            <ListItemIcon>
              <AssessmentIcon />
            </ListItemIcon>
            <ListItemText primary="レポート" />
          </ListItemButton>
          {canAudit && (
            <ListItemButton onClick={() => navigate("/audit")}
              sx={{
                borderLeft: "3px solid transparent",
                "&.Mui-selected": { borderLeftColor: "primary.main" }
              }}
            >
              <ListItemIcon>
                <HistoryIcon />
              </ListItemIcon>
              <ListItemText primary="監査" />
            </ListItemButton>
          )}
          {canMaster && (
            <ListItemButton onClick={() => navigate("/master")}
              sx={{
                borderLeft: "3px solid transparent",
                "&.Mui-selected": { borderLeftColor: "primary.main" }
              }}
            >
              <ListItemIcon>
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText primary="マスタ" />
            </ListItemButton>
          )}
        </List>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3, bgcolor: "background.default" }}>
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;
