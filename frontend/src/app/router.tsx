import { lazy, Suspense, type ReactNode } from "react";
import { Navigate, createBrowserRouter } from "react-router-dom";
import { AppShell } from "./AppShell";
import { LoadingDots } from "../components/ui/LoadingDots";
import { AuthLayout } from "../components/auth/AuthLayout";
import { AdminRoute, GuestRoute, ProtectedRoute } from "./RouteGuards";

const ChatPage = lazy(() =>
  import("../pages/ChatPage").then((module) => ({ default: module.ChatPage })),
);
const SearchPage = lazy(() =>
  import("../pages/SearchPage").then((module) => ({ default: module.SearchPage })),
);
const TopicsPage = lazy(() =>
  import("../pages/TopicsPage").then((module) => ({ default: module.TopicsPage })),
);
const TopicDetailPage = lazy(() =>
  import("../pages/TopicDetailPage").then((module) => ({
    default: module.TopicDetailPage,
  })),
);
const PracticePage = lazy(() =>
  import("../pages/PracticePage").then((module) => ({ default: module.PracticePage })),
);
const DocumentPage = lazy(() =>
  import("../pages/DocumentPage").then((module) => ({ default: module.DocumentPage })),
);
const LoginPage = lazy(() =>
  import("../pages/LoginPage").then((module) => ({ default: module.LoginPage })),
);
const RegisterPage = lazy(() =>
  import("../pages/RegisterPage").then((module) => ({ default: module.RegisterPage })),
);
const AdminDocumentsPage = lazy(() =>
  import("../pages/AdminDocumentsPage").then((module) => ({
    default: module.AdminDocumentsPage,
  })),
);

function load(element: ReactNode) {
  return (
    <Suspense
      fallback={
        <div className="grid min-h-80 place-items-center">
          <LoadingDots label="Đang tải trang" />
        </div>
      }
    >
      {element}
    </Suspense>
  );
}

export const router = createBrowserRouter([
  {
    element: <GuestRoute />,
    children: [
      {
        element: <AuthLayout />,
        children: [
          { path: "login", element: load(<LoginPage />) },
          { path: "register", element: load(<RegisterPage />) },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          { index: true, element: <Navigate to="/chat" replace /> },
          { path: "chat", element: load(<ChatPage />) },
          { path: "search", element: load(<SearchPage />) },
          { path: "topics", element: load(<TopicsPage />) },
          { path: "topics/:slug", element: load(<TopicDetailPage />) },
          { path: "practice", element: load(<PracticePage />) },
          { path: "documents/:id", element: load(<DocumentPage />) },
          {
            element: <AdminRoute />,
            children: [
              {
                path: "admin/documents",
                element: load(<AdminDocumentsPage />),
              },
            ],
          },
        ],
      },
    ],
  },
]);
