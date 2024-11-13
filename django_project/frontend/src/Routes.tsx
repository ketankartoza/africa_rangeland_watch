import React, { Suspense } from "react";
import { useRoutes } from "react-router-dom";
import PrivateRoute from "./PrivateRoute";

const Center = React.lazy(() => import("@chakra-ui/react").then(module => ({ default: module.Center })));
const Spinner = React.lazy(() => import("@chakra-ui/react").then(module => ({ default: module.Spinner })));

const HomePage = React.lazy(() => import("./pages/Home/index"));
const NotFound = React.lazy(() => import("./pages/NotFound"));
const ProfileInformationPage = React.lazy(() => import("./pages/Profile"));
const OrganisationInformation = React.lazy(() => import("./pages/OrganisationInformation"));

const ProjectRoutes = () => {
  const routes = useRoutes([
    { path: "/", element: <HomePage /> },
    { path: "*", element: <NotFound /> },

    // Use PrivateRoute for protected routes
    {
      path: "/profile",
      element: <PrivateRoute Component={ProfileInformationPage} />,
    },
    {
      path: "/organisation",
      element: <PrivateRoute Component={OrganisationInformation} />,
    },
  ]);

  return (
    <Suspense
      fallback={
        <Suspense fallback={<div></div>}>
          <Center h="100vh">
            <Spinner size="xl" />
          </Center>
        </Suspense>
      }
    >
      {routes}
    </Suspense>
  );
};

export default ProjectRoutes;
