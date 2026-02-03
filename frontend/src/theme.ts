import { createTheme } from "@mui/material";

export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#ff9900"
    },
    secondary: {
      main: "#00a6ff"
    },
    background: {
      default: "#0b1220",
      paper: "#111b2b"
    },
    text: {
      primary: "#f5f7fb",
      secondary: "#a0b3d6"
    }
  },
  typography: {
    fontFamily: "'Segoe UI', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif"
  },
  shape: {
    borderRadius: 10
  }
});
