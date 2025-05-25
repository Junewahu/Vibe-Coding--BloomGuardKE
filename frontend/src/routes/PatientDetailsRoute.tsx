import React from 'react';
import { useParams } from 'react-router-dom';
import { PatientDetails } from '../components/patients/PatientDetails';

export const PatientDetailsRoute: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  if (!id) {
    return null;
  }

  return <PatientDetails />;
}; 