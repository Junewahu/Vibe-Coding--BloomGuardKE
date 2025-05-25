export interface FieldVisit {
  id: string;
  chw_id: string;
  patient_id: string;
  visit_type: 'home_visit' | 'follow_up' | 'emergency' | 'routine';
  scheduled_date: string;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  notes?: string;
  location?: {
    latitude: number;
    longitude: number;
    address: string;
  };
  created_at: string;
  updated_at: string;
}

export interface CHWActivity {
  id: string;
  chw_id: string;
  activity_type: 'training' | 'meeting' | 'community_event' | 'other';
  title: string;
  description: string;
  scheduled_date: string;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  location?: {
    latitude: number;
    longitude: number;
    address: string;
  };
  participants?: string[];
  created_at: string;
  updated_at: string;
} 