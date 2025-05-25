import React, { createContext, useContext, ReactNode } from 'react';
import { useCHW } from '../hooks/useCHW';

interface CHWContextType {
  fieldVisits: any[];
  activities: any[];
  stats: {
    totalVisits: number;
    completedVisits: number;
    scheduledActivities: number;
    visitTrend: number;
  };
  isLoading: boolean;
  loadFieldData: () => Promise<void>;
  createFieldVisit: (visit: any) => Promise<any>;
  updateFieldVisit: (visitId: string, updates: any) => Promise<any>;
  createCHWActivity: (activity: any) => Promise<any>;
  updateCHWActivity: (activityId: string, updates: any) => Promise<any>;
}

const CHWContext = createContext<CHWContextType | undefined>(undefined);

interface CHWProviderProps {
  children: ReactNode;
  chwId: string;
}

export const CHWProvider: React.FC<CHWProviderProps> = ({ children, chwId }) => {
  const chwState = useCHW(chwId);

  return (
    <CHWContext.Provider value={chwState}>
      {children}
    </CHWContext.Provider>
  );
};

export const useCHWContext = () => {
  const context = useContext(CHWContext);
  if (context === undefined) {
    throw new Error('useCHWContext must be used within a CHWProvider');
  }
  return context;
}; 