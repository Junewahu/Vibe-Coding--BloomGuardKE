import React from 'react';
import { useParams } from 'react-router-dom';
import { CHWFieldTrackerWrapper } from '../components/tracking/CHWFieldTrackerWrapper';

export const CHWFieldTrackerRoute: React.FC = () => {
  const { chwId } = useParams<{ chwId: string }>();

  if (!chwId) {
    return <div>CHW ID is required</div>;
  }

  return <CHWFieldTrackerWrapper chwId={chwId} />;
}; 