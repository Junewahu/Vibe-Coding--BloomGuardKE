import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { PatientList } from '../components/patients/PatientList';
import { PatientDetailsRoute } from './PatientDetailsRoute';
import { CHWFieldTrackerRoute } from './CHWFieldTrackerRoute';

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      <Route path="/patients" element={<PatientList />} />
      <Route path="/patients/:id" element={<PatientDetailsRoute />} />
      <Route path="/chw/:chwId/field-tracker" element={<CHWFieldTrackerRoute />} />
    </Routes>
  );
}; 