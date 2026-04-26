import { Navigate, createBrowserRouter } from "react-router-dom";
import { App } from "@/App";
import { RequireAuth } from "@/components/auth/RequireAuth";
import { LayoutEditorPage } from "@/pages/layout-editor";
import { ModelViewerPage } from "@/pages/model-viewer";
import { LoginPage } from "@/pages/auth/login";
import { RegisterPage } from "@/pages/auth/register";
import { ProfilePage } from "@/pages/profile";
import { ErrorPage } from "@/pages/error";
import WelcomePage from "../pages/welcome";

export const router = createBrowserRouter(
  [
  {
    path: "/",
    element: <App />,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        element: <WelcomePage />,
      },
      {
        path: "/welcome",
        element: <WelcomePage />,
      },
      {
        path: "/layout",
        element: (
          <RequireAuth>
            <LayoutEditorPage />
          </RequireAuth>
        ),
      },
      {
        path: "/layout/:tab",
        element: (
          <RequireAuth>
            <LayoutEditorPage />
          </RequireAuth>
        ),
      },
      {
        path: "/artifacts",
        element: (
          <RequireAuth>
            <Navigate to="/layout/artifacts" replace />
          </RequireAuth>
        ),
      },
      {
        path: "/models",
        element: (
          <RequireAuth>
            <ModelViewerPage />
          </RequireAuth>
        ),
      },
      {
        path: "/profile",
        element: (
          <RequireAuth>
            <ProfilePage />
          </RequireAuth>
        ),
      },
      {
        path: "/auth/login",
        element: <LoginPage />,
      },
      {
        path: "/auth/register",
        element: <RegisterPage />,
      },
      {
        path: "*",
        element: <ErrorPage />,
      },
    ],
  },
  ],
  {
    // future: {
    //   // 启用 React Router v7 的 startTransition 特性
    //   v7_startTransition: true,实验属性
  }
);
