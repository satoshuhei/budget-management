import { Component, ReactNode } from "react";
import { Box, Button, Stack, Typography } from "@mui/material";
import { logClientError } from "../utils/errorLogger";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: { componentStack: string }) {
    logClientError(error, "react.error-boundary", { componentStack: info.componentStack });
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", p: 3 }}>
          <Stack spacing={2} alignItems="center" maxWidth={520}>
            <Typography variant="h5" fontWeight={700}>
              予期しないエラーが発生しました
            </Typography>
            <Typography variant="body2" color="text.secondary" textAlign="center">
              画面の表示に失敗しました。再読み込みしても解決しない場合は、管理者に連絡してください。
            </Typography>
            <Button variant="contained" onClick={this.handleReload}>
              再読み込み
            </Button>
          </Stack>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
