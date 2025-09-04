import React, { useEffect, useMemo, useState } from "react";
import { Link, Routes, Route, useNavigate } from "react-router-dom";
import { FaSearch, FaShoppingCart } from "react-icons/fa";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Cart from "./components/Cart";
import ProductDetail from "./components/ProductDetail";
import { getCurrentUser, logout } from "./components/Auth";
import Checkout from "./components/Checkout";
import Footer from "./components/Footer";
import { Toaster } from "react-hot-toast";
import toast from "react-hot-toast";
import trackingService from "./services/tracking";

export default function App() {
  const navigate = useNavigate();
  const [user, setUser] = useState(() => getCurrentUser());
  const [cart, setCart] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("book_cart") || "[]");
    } catch {
      return [];
    }
  });
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [category, setCategory] = useState("all");

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    localStorage.setItem("book_cart", JSON.stringify(cart));
  }, [cart]);

  // Set user ID for tracking when user changes
  useEffect(() => {
    if (user && user.id) {
      trackingService.setUser(user.id);
    }
  }, [user]);

  const cartCount = useMemo(() => cart.reduce((s, i) => s + i.quantity, 0), [cart]);
  const cartTotal = useMemo(() => cart.reduce((s, i) => s + i.price * i.quantity, 0), [cart]);

  function addToCart(book, quantity) {
    // Track add to cart activity
    trackingService.trackAddToCart(book.BookID || book.id);
    
    setCart(currentCart => {
      const itemIndex = currentCart.findIndex(item => item.id === book.id);
      if (itemIndex > -1) {
        const newCart = [...currentCart];
        newCart[itemIndex].quantity += quantity;
        return newCart;
      }
      return [...currentCart, { ...book, quantity }];
    });
  }

  function removeFromCart(id) {
    setCart(currentCart => currentCart.filter(item => item.id !== id));
  }

  function updateQuantity(id, quantity) {
    if (quantity <= 0) {
      removeFromCart(id);
    } else {
      setCart(currentCart => currentCart.map(item =>
        item.id === id ? { ...item, quantity: Math.max(1, quantity) } : item
      ));
    }
  }

  function clearCart() {
    setCart([]);
  }

  function handleLogout() {
    logout();
    setUser(null);
    navigate("/");
  }

  // Hàm kiểm tra giỏ hàng trước khi điều hướng đến checkout
  function handleCheckoutClick(e) {
    if (cart.length === 0) {
      e.preventDefault();
      toast.error("Giỏ hàng trống. Vui lòng thêm sách trước khi thanh toán.");
    }
  }

  return (
    <div className="app-container">
      <header className="header">
        <div className="nav container">
          <Link to="/" className="brand-left">
            <img src="https://img.pikbest.com/png-images/20240821/simple-modern-book-logo-vector_10745589.png!bw700" alt="BookVerse Logo" className="brand-logo" />
            <div className="brand-name">BookVerse</div>
            <div className="slogan">Đọc sách là sống</div>
          </Link>

          <div className="search-center">
            <div className="search">
              <input
                className="input"
                type="search"
                placeholder="Tìm sách..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button className="search-btn"><FaSearch /></button>
            </div>
          </div>

          <div className="user-right">
            {user ? (
              <>
                <span className="user-name">Chào, {user.name.split(" ")[0]}</span>
                <button className="btn" onClick={handleLogout}>Đăng xuất</button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn-nav">Đăng nhập</Link>
                <Link to="/register" className="btn btn-nav btn-accent-nav">Đăng ký</Link>
              </>
            )}
            <Link to="/cart" className="btn cart-btn" aria-label="Giỏ hàng">
              <FaShoppingCart />
              {cartCount > 0 && <span className="badge">{cartCount}</span>}
            </Link>
          </div>
        </div>
      </header>

      <main className="main-content container">
        <Routes>
          <Route path="/" element={<Home query={debouncedQuery} category={category} onCategoryChange={setCategory} onAddToCart={addToCart} />} />
          <Route path="/product/:id" element={<ProductDetail onAddToCart={addToCart} />} />
          <Route path="/cart" element={<Cart items={cart} total={cartTotal} onInc={(id) => updateQuantity(id, (cart.find(i => i.id === id)?.quantity || 1) + 1)} onDec={(id) => updateQuantity(id, (cart.find(i => i.id === id)?.quantity || 1) - 1)} onRemove={removeFromCart} onClear={clearCart} />} />
          <Route path="/login" element={<Login onLoggedIn={setUser} />} />
          <Route path="/register" element={<Register onRegistered={setUser} />} />
          <Route 
            path="/checkout" 
            element={
              cart.length > 0 ? (
                <Checkout total={cartTotal} onClear={clearCart} />
              ) : (
                <div className="container" style={{ padding: 'var(--spacing-lg)' }}>
                  <div className="muted">Giỏ hàng trống. Vui lòng thêm sách để thanh toán.</div>
                  <Link to="/" className="btn btn-primary" style={{ marginTop: 'var(--spacing-md)' }}>
                    Quay về trang chủ
                  </Link>
                </div>
              )
            } 
          />
          <Route path="*" element={<div style={{ padding: 40 }}>Không tìm thấy trang</div>} />
        </Routes>
      </main>

      <Footer />
      <Toaster position="top-center" reverseOrder={false} />
    </div>
  );
}