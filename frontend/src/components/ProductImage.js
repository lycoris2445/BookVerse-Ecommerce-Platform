import React, { useState } from 'react';
import { resolveImageUrl } from '../utils/imageUtils';

const ProductImage = ({ 
  src, 
  alt = "Sản phẩm", 
  className = "", 
  width = 200, 
  height = 250,
  style = {}
}) => {
  const [imgSrc, setImgSrc] = useState(() => resolveImageUrl(src));
  const [hasError, setHasError] = useState(false);

  const handleError = () => {
    if (!hasError) {
      setHasError(true);
      setImgSrc('/placeholder.png');
    }
  };

  const imgStyle = {
    width: width,
    height: height,
    objectFit: 'cover',
    display: 'block',
    ...style
  };

  return (
    <img
      src={imgSrc}
      alt={alt}
      className={className}
      style={imgStyle}
      onError={handleError}
      loading="lazy"
    />
  );
};

export default ProductImage;
