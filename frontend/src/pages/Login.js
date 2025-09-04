// Login.js (cải thiện giao diện)
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../components/Auth";
import { FaEnvelope, FaLock } from "react-icons/fa";
import PropTypes from "prop-types";
import toast from "react-hot-toast";

export default function Login({ onLoggedIn }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const user = await login({ email, password });
      onLoggedIn(user);
      toast.success("Đăng nhập thành công!");
      navigate("/");
    } catch (ex) {
      toast.error(ex.message || "Đăng nhập thất bại");
    }
  }

  return (
    <section className="auth-section">
      <div className="container">
        <h1 className="auth-title">Đăng nhập</h1>
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">
              <FaEnvelope /> Email
            </label>
            <input className="input" value={email} onChange={e => setEmail(e.target.value)} type="email" required placeholder="Nhập email" />
          </div>
          <div className="form-group">
            <label className="form-label">
              <FaLock /> Mật khẩu
            </label>
            <input className="input" value={password} onChange={e => setPassword(e.target.value)} type="password" required placeholder="Nhập mật khẩu" />
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" type="submit">Đăng nhập</button>
            <Link to="/register" className="btn btn-link">Chưa có tài khoản? Đăng ký</Link>
          </div>
        </form>
      </div>
    </section>
  );
}

Login.propTypes = {
  onLoggedIn: PropTypes.func.isRequired
};