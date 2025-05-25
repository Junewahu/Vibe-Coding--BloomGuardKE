import React from 'react';
import { CHWProvider } from '../../contexts/CHWContext';
import { CHWFieldTracker } from './CHWFieldTracker';

interface CHWFieldTrackerWrapperProps {
  chwId: string;
}

export const CHWFieldTrackerWrapper: React.FC<CHWFieldTrackerWrapperProps> = ({ chwId }) => {
  return (
    <CHWProvider chwId={chwId}>
      <CHWFieldTracker />
    </CHWProvider>
  );
}; 