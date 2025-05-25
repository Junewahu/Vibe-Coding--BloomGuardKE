from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models.patient import Patient
from ..models.appointment import Appointment
from ..models.follow_up import FollowUp
from ..models.notification import Notification
from ..models.response import Response

def calculate_risk_score(patient: Patient) -> float:
    """
    Calculate a risk score for a patient based on various factors.
    Returns a score between 0 and 10, where higher scores indicate higher risk.
    """
    score = 0.0
    
    # Factor 1: Appointment Attendance (0-2 points)
    attendance_score = _calculate_attendance_score(patient)
    score += attendance_score
    
    # Factor 2: Follow-up Compliance (0-2 points)
    follow_up_score = _calculate_follow_up_score(patient)
    score += follow_up_score
    
    # Factor 3: Response Rate (0-2 points)
    response_score = _calculate_response_score(patient)
    score += response_score
    
    # Factor 4: Medical History (0-2 points)
    medical_score = _calculate_medical_score(patient)
    score += medical_score
    
    # Factor 5: Demographics (0-2 points)
    demographic_score = _calculate_demographic_score(patient)
    score += demographic_score
    
    return min(score, 10.0)  # Cap at 10

def _calculate_attendance_score(patient: Patient) -> float:
    """Calculate score based on appointment attendance history."""
    score = 0.0
    
    # Get appointments in the last 3 months
    three_months_ago = datetime.now() - timedelta(days=90)
    appointments = patient.appointments.filter(
        Appointment.scheduled_date >= three_months_ago
    ).all()
    
    if not appointments:
        return 0.0
    
    # Calculate no-show rate
    no_shows = sum(1 for apt in appointments if apt.status == "no_show")
    no_show_rate = no_shows / len(appointments)
    
    if no_show_rate >= 0.5:  # 50% or more no-shows
        score = 2.0
    elif no_show_rate >= 0.25:  # 25-50% no-shows
        score = 1.5
    elif no_show_rate >= 0.1:  # 10-25% no-shows
        score = 1.0
    elif no_show_rate > 0:  # Some no-shows
        score = 0.5
    
    return score

def _calculate_follow_up_score(patient: Patient) -> float:
    """Calculate score based on follow-up compliance."""
    score = 0.0
    
    # Get follow-ups in the last 3 months
    three_months_ago = datetime.now() - timedelta(days=90)
    follow_ups = patient.follow_ups.filter(
        FollowUp.created_at >= three_months_ago
    ).all()
    
    if not follow_ups:
        return 0.0
    
    # Calculate completion rate
    completed = sum(1 for fu in follow_ups if fu.status == "completed")
    completion_rate = completed / len(follow_ups)
    
    if completion_rate < 0.3:  # Less than 30% completed
        score = 2.0
    elif completion_rate < 0.5:  # 30-50% completed
        score = 1.5
    elif completion_rate < 0.7:  # 50-70% completed
        score = 1.0
    elif completion_rate < 0.9:  # 70-90% completed
        score = 0.5
    
    return score

def _calculate_response_score(patient: Patient) -> float:
    """Calculate score based on response rate to notifications."""
    score = 0.0
    
    # Get notifications in the last 3 months
    three_months_ago = datetime.now() - timedelta(days=90)
    notifications = patient.notifications.filter(
        Notification.created_at >= three_months_ago
    ).all()
    
    if not notifications:
        return 0.0
    
    # Calculate response rate
    responses = sum(1 for n in notifications if n.responses)
    response_rate = responses / len(notifications)
    
    if response_rate < 0.2:  # Less than 20% response rate
        score = 2.0
    elif response_rate < 0.4:  # 20-40% response rate
        score = 1.5
    elif response_rate < 0.6:  # 40-60% response rate
        score = 1.0
    elif response_rate < 0.8:  # 60-80% response rate
        score = 0.5
    
    return score

def _calculate_medical_score(patient: Patient) -> float:
    """Calculate score based on medical history and conditions."""
    score = 0.0
    
    # Check for chronic conditions
    if patient.medical_history and "chronic_conditions" in patient.medical_history:
        chronic_conditions = patient.medical_history["chronic_conditions"]
        if len(chronic_conditions) >= 3:
            score += 1.0
        elif len(chronic_conditions) >= 1:
            score += 0.5
    
    # Check for recent hospitalizations
    if patient.medical_history and "hospitalizations" in patient.medical_history:
        recent_hospitalizations = [
            h for h in patient.medical_history["hospitalizations"]
            if (datetime.now() - h["date"]).days <= 90
        ]
        if len(recent_hospitalizations) >= 2:
            score += 1.0
        elif len(recent_hospitalizations) == 1:
            score += 0.5
    
    return min(score, 2.0)

def _calculate_demographic_score(patient: Patient) -> float:
    """Calculate score based on demographic factors."""
    score = 0.0
    
    # Age factor
    if patient.date_of_birth:
        age = (datetime.now() - patient.date_of_birth).days / 365.25
        if age >= 65:  # Elderly patients
            score += 0.5
        elif age <= 5:  # Very young patients
            score += 0.5
    
    # Location factor (if available)
    if patient.address and "distance_to_clinic" in patient.address:
        distance = patient.address["distance_to_clinic"]
        if distance > 50:  # More than 50km from clinic
            score += 0.5
    
    # Socioeconomic factors
    if patient.socioeconomic_status == "low":
        score += 0.5
    
    # Transportation access
    if patient.transportation_access == "limited":
        score += 0.5
    
    return min(score, 2.0)

def get_risk_factors(patient: Patient) -> List[Dict[str, Any]]:
    """Get detailed risk factors for a patient."""
    risk_factors = []
    
    # Appointment attendance factors
    attendance_score = _calculate_attendance_score(patient)
    if attendance_score > 0:
        risk_factors.append({
            "category": "appointment_attendance",
            "score": attendance_score,
            "description": "High rate of missed appointments"
        })
    
    # Follow-up compliance factors
    follow_up_score = _calculate_follow_up_score(patient)
    if follow_up_score > 0:
        risk_factors.append({
            "category": "follow_up_compliance",
            "score": follow_up_score,
            "description": "Low follow-up completion rate"
        })
    
    # Response rate factors
    response_score = _calculate_response_score(patient)
    if response_score > 0:
        risk_factors.append({
            "category": "communication",
            "score": response_score,
            "description": "Low response rate to notifications"
        })
    
    # Medical history factors
    medical_score = _calculate_medical_score(patient)
    if medical_score > 0:
        risk_factors.append({
            "category": "medical_history",
            "score": medical_score,
            "description": "Complex medical history"
        })
    
    # Demographic factors
    demographic_score = _calculate_demographic_score(patient)
    if demographic_score > 0:
        risk_factors.append({
            "category": "demographics",
            "score": demographic_score,
            "description": "High-risk demographic factors"
        })
    
    return sorted(risk_factors, key=lambda x: x["score"], reverse=True) 