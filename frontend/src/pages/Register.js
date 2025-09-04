// Register.js (cải thiện giao diện)
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register } from "../components/Auth";
import { FaUser, FaEnvelope, FaLock } from "react-icons/fa";
import PropTypes from "prop-types";
import toast from "react-hot-toast";

export default function Register({ onRegistered }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const user = await register({ name, email, password });
      onRegistered(user);
      toast.success("Đăng ký thành công!");
      navigate("/");
    } catch (ex) {
      toast.error(ex.message || "Đăng ký thất bại");
    }
  }

  return (
    <section className="auth-section">
      <div className="container">
        <h1 className="auth-title">Đăng ký</h1>
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">
              <FaUser /> Họ và tên
            </label>
            <input className="input" value={name} onChange={e => setName(e.target.value)} required placeholder="Nhập tên của bạn" />
          </div>
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
            <input className="input" value={password} onChange={e => setPassword(e.target.value)} type="password" minLength={6} required placeholder="Tối thiểu 6 ký tự" />
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" type="submit">Tạo tài khoản</button>
            <Link to="/login" className="btn btn-link">Đã có tài khoản? Đăng nhập</Link>
          </div>
        </form>
      </div>
    </section>
  );
}

Register.propTypes = {
  onRegistered: PropTypes.func.isRequired
};