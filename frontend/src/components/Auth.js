const USERS_KEY = "book_users";
const CURRENT_KEY = "book_current";

async function hashPassword(password) {
  if (!crypto.subtle) return password; // Fallback nếu không support
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hash = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, "0")).join("");
}

function readUsers() {
  try { return JSON.parse(localStorage.getItem(USERS_KEY)) || []; } catch { return []; }
}
function writeUsers(users) { localStorage.setItem(USERS_KEY, JSON.stringify(users)); }

export function getCurrentUser() {
  try { return JSON.parse(localStorage.getItem(CURRENT_KEY)); } catch { return null; }
}
function setCurrentUser(u) { localStorage.setItem(CURRENT_KEY, JSON.stringify(u)); }

export async function register({ name, email, password }) {
  const users = readUsers();
  if (users.some(u => u.email.toLowerCase() === email.toLowerCase())) {
    throw new Error("Email đã tồn tại");
  }
  const hashed = await hashPassword(password);
  const user = { id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()), name, email, password: hashed };
  users.push(user);
  writeUsers(users);
  setCurrentUser({ id: user.id, name: user.name, email: user.email });
  return { id: user.id, name: user.name, email: user.email };
}

export async function login({ email, password }) {
  const users = readUsers();
  const found = users.find(u => u.email.toLowerCase() === email.toLowerCase());
  if (!found) throw new Error("Email hoặc mật khẩu không đúng");
  
  const hashed = await hashPassword(password);
  if (found.password !== hashed) {
      throw new Error("Email hoặc mật khẩu không đúng");
  }

  setCurrentUser({ id: found.id, name: found.name, email: found.email });
  return { id: found.id, name: found.name, email: found.email };
}

export function logout() {
  localStorage.removeItem(CURRENT_KEY);
}