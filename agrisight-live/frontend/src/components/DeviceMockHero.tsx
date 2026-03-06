/**
 * DeviceMockHero Component
 * Renders a floating device mockup for the landing page hero section.
 * Expected env vars: None
 * Testing tips: Visual component, verify rendering without errors.
 */
import React from 'react';

export default function DeviceMockHero() {
  return (
    <div className="relative w-64 h-[500px] bg-neutral-dark rounded-[3rem] border-8 border-gray-800 shadow-2xl overflow-hidden transform rotate-[-5deg] hover:rotate-0 transition-transform duration-500">
      {/* Notch */}
      <div className="absolute top-0 inset-x-0 h-6 bg-gray-800 rounded-b-3xl w-1/2 mx-auto z-20" />
      
      {/* Screen Content */}
      <div className="absolute inset-0 bg-surface-white">
        <div className="h-1/2 bg-primary-green/20 relative">
          {/* Mock Leaf */}
          <svg className="absolute inset-0 w-full h-full text-primary-green/40 p-8" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17,8C8,10 5.9,16.17 3.82,21.34L5.71,22L6.66,19.7C7.14,19.87 7.64,20 8,20C19,20 22,3 22,3C21,5 14,5.25 9,6.25C4,7.25 2,11.5 2,13.5C2,15.5 3.75,17.25 3.75,17.25C7,8 17,8 17,8Z" />
          </svg>
          {/* Mock Bounding Box */}
          <div className="absolute top-1/4 left-1/4 w-1/2 h-1/2 border-2 border-primary-green rounded-lg animate-pulse" />
        </div>
        <div className="p-4">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4" />
          <div className="h-3 bg-gray-100 rounded w-full mb-2" />
          <div className="h-3 bg-gray-100 rounded w-5/6 mb-2" />
          <div className="h-3 bg-gray-100 rounded w-4/6" />
        </div>
      </div>
    </div>
  );
}
