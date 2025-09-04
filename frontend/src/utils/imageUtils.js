/**
 * Resolve image URL to absolute URL with fallback
 * @param {string} imageUrl - Image URL from API or relative path
 * @returns {string} - Absolute URL or placeholder
 */
export const resolveImageUrl = (imageUrl) => {
  // If empty or null, return placeholder
  if (!imageUrl) {
    return '/placeholder.png';
  }

  // If already absolute URL (starts with http(s)), return as is
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }

  // Get backend host - use React env variables with production fallback
  const apiBase = process.env.REACT_APP_API_URL || 
    (process.env.NODE_ENV === 'production' 
      ? 'https://ecomtech.onrender.com' 
      : 'http://127.0.0.1:8000');
  const backendHost = apiBase.replace('/api', '');

  // If starts with '/' (absolute path), combine with backend host
  if (imageUrl.startsWith('/')) {
    return `${backendHost}${imageUrl}`;
  }

  // If relative path (no leading '/'), add '/media/book_images/' prefix
  return `${backendHost}/media/book_images/${imageUrl}`;
};

/**
 * Handle image error by setting placeholder
 * @param {Event} event - Image error event
 */
export const handleImageError = (event) => {
  event.target.src = '/placeholder.png';
  event.target.onerror = null; // Prevent infinite loop
};
