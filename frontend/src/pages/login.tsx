import { useState } from "react";
import { Box, Button, Card, CardContent, Stack, TextField, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const LoginPage = () => {
  const [username, setUsername] = useState("alice");
  const [password, setPassword] = useState("password");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async () => {
    setError(null);
    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError("ログインに失敗しました");
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "background.default",
        px: 2
      }}
    >
      <Card sx={{ width: 420, bgcolor: "background.paper", borderRadius: 3 }}>
        <CardContent>
          <Stack spacing={2}>
            <Typography variant="h5" fontWeight={700}>
              Budget Management
            </Typography>
            <Typography variant="body2" color="text.secondary">
              ダミー認証でログインできます
            </Typography>
            <TextField
              label="ユーザー名"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <TextField
              label="パスワード"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {error && (
              <Typography color="error" variant="body2">
                {error}
              </Typography>
            )}
            <Button variant="contained" size="large" onClick={handleSubmit}>
              ログイン
            </Button>
            <Typography variant="caption" color="text.secondary">
              alice/password, bob/password, admin/admin, auditor/audit
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LoginPage;
