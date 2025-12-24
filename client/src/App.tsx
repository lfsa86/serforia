import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Login } from './pages/Login';
import { Home } from './pages/Home';
import './App.css';

const BASE_PATH = import.meta.env.VITE_BASE_PATH?.replace(/\/$/, '') || '/';

function LoginRedirect() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        fontSize: '1.2rem',
        color: '#666'
      }}>
        Cargando...
      </div>
    );
  }

  return isAuthenticated ? <Navigate to="/" replace /> : <Login />;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter basename={BASE_PATH}>
        <Routes>
          <Route path="/login" element={<LoginRedirect />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
