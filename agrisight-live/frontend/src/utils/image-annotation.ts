/**
 * Image Annotation Utility
 * Helper functions for drawing annotations on images.
 * Expected env vars: None
 * Testing tips: Unit test coordinate transformations.
 */

export function calculateBoundingBoxCss(x: number, y: number, w: number, h: number) {
  // Converts normalized coordinates (0-1) to percentages for CSS
  return {
    left: `${x * 100}%`,
    top: `${y * 100}%`,
    width: `${w * 100}%`,
    height: `${h * 100}%`,
  };
}
