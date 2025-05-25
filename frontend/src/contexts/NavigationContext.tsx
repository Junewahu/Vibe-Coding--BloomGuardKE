import React, { createContext, useContext, useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface NavigationContextType {
  currentPath: string;
  previousPath: string | null;
  navigateTo: (path: string) => void;
  goBack: () => void;
  canGoBack: boolean;
  breadcrumbs: string[];
}

const NavigationContext = createContext<NavigationContextType>({
  currentPath: '/',
  previousPath: null,
  navigateTo: () => {},
  goBack: () => {},
  canGoBack: false,
  breadcrumbs: [],
});

export const useNavigation = () => useContext(NavigationContext);

export const NavigationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [previousPath, setPreviousPath] = useState<string | null>(null);
  const [pathHistory, setPathHistory] = useState<string[]>([]);

  useEffect(() => {
    if (location.pathname !== previousPath) {
      setPreviousPath(location.pathname);
      setPathHistory((prev) => [...prev, location.pathname]);
    }
  }, [location.pathname, previousPath]);

  const navigateTo = (path: string) => {
    navigate(path);
  };

  const goBack = () => {
    if (pathHistory.length > 1) {
      const newHistory = [...pathHistory];
      newHistory.pop(); // Remove current path
      const previousPath = newHistory[newHistory.length - 1];
      setPathHistory(newHistory);
      navigate(previousPath);
    }
  };

  const getBreadcrumbs = (path: string): string[] => {
    const parts = path.split('/').filter(Boolean);
    return parts.map((part, index) => {
      const path = '/' + parts.slice(0, index + 1).join('/');
      return path;
    });
  };

  return (
    <NavigationContext.Provider
      value={{
        currentPath: location.pathname,
        previousPath,
        navigateTo,
        goBack,
        canGoBack: pathHistory.length > 1,
        breadcrumbs: getBreadcrumbs(location.pathname),
      }}
    >
      {children}
    </NavigationContext.Provider>
  );
}; 