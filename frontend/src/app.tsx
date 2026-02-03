import { Route, Routes, Navigate } from "react-router-dom";
import Layout from "./layout/layout";
import DashboardPage from "./pages/dashboard";
import LoginPage from "./pages/login";
import PlansPage from "./pages/plans";
import { useAuth } from "./hooks/useAuth";
import ApprovalsPage from "./pages/approvals";
import ExecutionsPage from "./pages/executions";
import ReportsPage from "./pages/reports";
import AuditPage from "./pages/audit";
import RequestsPage from "./pages/requests";
import MasterPage from "./pages/master";
import ErrorBoundary from "./components/ErrorBoundary";

const App = () => {
  const { isAuthenticated, isChecking } = useAuth();

  if (isChecking) {
    return <div />;
  }

  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={isAuthenticated ? <Layout /> : <Navigate to="/login" replace />}
        >
          <Route index element={<DashboardPage />} />
          <Route path="plans" element={<PlansPage />} />
          <Route path="requests" element={<RequestsPage />} />
          <Route path="approvals" element={<ApprovalsPage />} />
          <Route path="executions" element={<ExecutionsPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="audit" element={<AuditPage />} />
          <Route path="master" element={<MasterPage />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  );
};

export default App;
