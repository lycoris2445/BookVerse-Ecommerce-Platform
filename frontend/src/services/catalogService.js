import ApiService from './api';

// Lấy danh sách sách với filter và pagination
export async function getBooks(params = {}) {
  try {
    const queryParams = new URLSearchParams();
    
    // Thêm các params vào query
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        queryParams.append(key, params[key]);
      }
    });
    
    const queryString = queryParams.toString();
    const endpoint = `/api/v1/catalog/books/${queryString ? `?${queryString}` : ''}`;
    
    const response = await ApiService.request(endpoint, { auth: false });
    
    // Transform DRF pagination response to expected format
    return {
      success: true,
      data: response.results || [],
      total: response.count || 0,
      next: response.next,
      previous: response.previous
    };
  } catch (error) {
    console.error('Get books failed:', error);
    return {
      success: false,
      data: [],
      total: 0,
      error: error.message
    };
  }
}

// Lấy chi tiết một cuốn sách
export async function getBook(bookId) {
  try {
    return await ApiService.request(`/api/v1/catalog/books/${bookId}/`, { auth: false });
  } catch (error) {
    console.error('Get book failed:', error);
    throw error;
  }
}

// Tìm kiếm sách
export async function searchBooks(query, params = {}) {
  try {
    const searchParams = {
      search: query,
      ...params
    };
    
    return await getBooks(searchParams);
  } catch (error) {
    console.error('Search books failed:', error);
    throw error;
  }
}

// Lấy sách theo category
export async function getBooksByCategory(categoryId, params = {}) {
  try {
    const categoryParams = {
      category: categoryId,
      ...params
    };
    
    return await getBooks(categoryParams);
  } catch (error) {
    console.error('Get books by category failed:', error);
    throw error;
  }
}

// Lấy danh sách categories
export async function getCategories() {
  try {
    const response = await ApiService.request('/api/v1/catalog/categories/', { auth: false });
    
    // Transform DRF pagination response to expected format
    return {
      success: true,
      data: response.results || [],
      total: response.count || 0
    };
  } catch (error) {
    console.error('Get categories failed:', error);
    return {
      success: false,
      data: [],
      total: 0,
      error: error.message
    };
  }
}

// Lấy danh sách authors
export async function getAuthors(params = {}) {
  try {
    const queryParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
      if (params[key]) {
        queryParams.append(key, params[key]);
      }
    });
    
    const queryString = queryParams.toString();
    const endpoint = `/api/v1/catalog/authors/${queryString ? `?${queryString}` : ''}`;
    
    return await ApiService.request(endpoint, { auth: false });
  } catch (error) {
    console.error('Get authors failed:', error);
    throw error;
  }
}

// Lấy chi tiết author
export async function getAuthor(authorId) {
  try {
    return await ApiService.request(`/api/v1/catalog/authors/${authorId}/`, { auth: false });
  } catch (error) {
    console.error('Get author failed:', error);
    throw error;
  }
}

// Lấy danh sách publishers
export async function getPublishers() {
  try {
    return await ApiService.request('/api/v1/catalog/publishers/', { auth: false });
  } catch (error) {
    console.error('Get publishers failed:', error);
    throw error;
  }
}

// Lấy chi tiết publisher
export async function getPublisher(publisherId) {
  try {
    return await ApiService.request(`/api/v1/catalog/publishers/${publisherId}/`, { auth: false });
  } catch (error) {
    console.error('Get publisher failed:', error);
    throw error;
  }
}

// Lấy sách featured/nổi bật
export async function getFeaturedBooks(limit = 8) {
  try {
    return await getBooks({ 
      featured: true, 
      page_size: limit 
    });
  } catch (error) {
    console.error('Get featured books failed:', error);
    throw error;
  }
}

// Lấy sách mới nhất
export async function getLatestBooks(limit = 8) {
  try {
    return await getBooks({ 
      ordering: '-created_at', 
      page_size: limit 
    });
  } catch (error) {
    console.error('Get latest books failed:', error);
    throw error;
  }
}

// Lấy sách bán chạy
export async function getBestSellerBooks(limit = 8) {
  try {
    return await getBooks({ 
      ordering: '-sales_count', 
      page_size: limit 
    });
  } catch (error) {
    console.error('Get best seller books failed:', error);
    throw error;
  }
}

// Default export với tất cả functions để backward compatibility
export default {
  getBooks,
  getBook,
  searchBooks,
  getBooksByCategory,
  getCategories,
  getAuthors,
  getAuthor,
  getPublishers,
  getPublisher,
  getFeaturedBooks,
  getLatestBooks,
  getBestSellerBooks
};
