import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";

import Index from "./pages/Index.tsx";
import Auth from "./pages/Auth.tsx";
import Dashboard from "./pages/Dashboard.tsx";
import Sessions from "./pages/Sessions.tsx";
import NewSession from "./pages/NewSession.tsx";
import DomainSelect from "./pages/DomainSelect.tsx";
import SessionConsole from "./pages/SessionConsole.tsx";
import PostOp from "./pages/PostOp.tsx";
import PreOpView from "./pages/PreOpView.tsx";
import SurgeonProfile from "./pages/SurgeonProfile.tsx";
import AdminAudit from "./pages/admin/AdminAudit.tsx";
import AdminUsers from "./pages/admin/AdminUsers.tsx";
import AdminGpu from "./pages/admin/AdminGpu.tsx";
import NotFound from "./pages/NotFound.tsx";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/auth" element={<Auth />} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/sessions" element={<ProtectedRoute><Sessions /></ProtectedRoute>} />
            <Route path="/sessions/domain" element={<ProtectedRoute><DomainSelect /></ProtectedRoute>} />
            <Route path="/sessions/new" element={<ProtectedRoute><NewSession /></ProtectedRoute>} />
            <Route path="/sessions/:id/preop" element={<ProtectedRoute><PreOpView /></ProtectedRoute>} />
            <Route path="/sessions/:id/console" element={<ProtectedRoute><SessionConsole /></ProtectedRoute>} />
            <Route path="/sessions/:id/post-op" element={<ProtectedRoute><PostOp /></ProtectedRoute>} />
            <Route path="/settings/profile" element={<ProtectedRoute><SurgeonProfile /></ProtectedRoute>} />
            <Route path="/admin/audit" element={<ProtectedRoute requireRole="admin"><AdminAudit /></ProtectedRoute>} />
            <Route path="/admin/users" element={<ProtectedRoute requireRole="admin"><AdminUsers /></ProtectedRoute>} />
            <Route path="/admin/gpu" element={<ProtectedRoute requireRole="admin"><AdminGpu /></ProtectedRoute>} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
