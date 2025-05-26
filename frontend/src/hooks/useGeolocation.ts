import { useState, useEffect } from 'react';

interface Location {
  latitude: number;
  longitude: number;
  accuracy?: number;
}

interface GeolocationError {
  code: number;
  message: string;
}

export const useGeolocation = () => {
  const [location, setLocation] = useState<Location | null>(null);
  const [error, setError] = useState<GeolocationError | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!navigator.geolocation) {
      setError({
        code: 0,
        message: 'Geolocation is not supported by your browser',
      });
      setLoading(false);
      return;
    }

    const successHandler = (position: GeolocationPosition) => {
      setLocation({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
      });
      setLoading(false);
    };

    const errorHandler = (error: GeolocationPositionError) => {
      setError({
        code: error.code,
        message: error.message,
      });
      setLoading(false);
    };

    const watchId = navigator.geolocation.watchPosition(
      successHandler,
      errorHandler,
      {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0,
      }
    );

    return () => {
      navigator.geolocation.clearWatch(watchId);
    };
  }, []);

  return { location, error, loading };
}; 