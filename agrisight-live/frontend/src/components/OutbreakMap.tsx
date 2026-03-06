/**
 * OutbreakMap
 * Renders a regional disease heatmap using Mapbox GL.
 * Expected env vars: VITE_MAPBOX_TOKEN, VITE_API_URL
 * Testing tips: Mock mapbox-gl and fetch in tests.
 */
import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';

mapboxgl.accessToken =
  (import.meta.env.VITE_MAPBOX_TOKEN as string | undefined) ?? '';

interface HeatCell {
  lat: number;
  lon: number;
  density: number;
}

export function OutbreakMap() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: 'mapbox://styles/mapbox/light-v11',
      center: [81.0, 23.0],
      zoom: 5,
    });
    mapRef.current = map;

    const baseUrl =
      (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000';
    fetch(`${baseUrl}/api/outbreak-heatmap`)
      .then((res) => res.json())
      .then((data) => {
        const cells: HeatCell[] = data.grid ?? [];
        if (!cells.length) return;
        const features = cells.map((c) => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [c.lon, c.lat] },
          properties: { density: c.density },
        }));
        const sourceData = {
          type: 'FeatureCollection',
          features,
        } as any;
        map.on('load', () => {
          map.addSource('outbreak-heat', {
            type: 'geojson',
            data: sourceData,
          });
          map.addLayer({
            id: 'outbreak-heat-layer',
            type: 'heatmap',
            source: 'outbreak-heat',
            paint: {
              'heatmap-weight': ['interpolate', ['linear'], ['get', 'density'], 0, 0, 1, 1],
              'heatmap-intensity': 1,
              'heatmap-radius': 20,
              'heatmap-color': [
                'interpolate',
                ['linear'],
                ['heatmap-density'],
                0,
                'rgba(0, 255, 0, 0)',
                0.3,
                'rgba(173, 255, 47, 0.6)',
                0.6,
                'rgba(255, 215, 0, 0.8)',
                1,
                'rgba(255, 0, 0, 0.9)',
              ],
            },
          });
        });
      })
      .catch(() => {});

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  return <div ref={containerRef} className="w-full h-64 rounded-2xl overflow-hidden" />;
}

