import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

// Create the auth context
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is logged in on initial load
  useEffect(() => {
    const fetchUser = async () => {
      if (token) {
        try {
          const response = await axios.get('/api/users/me', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          setUser(response.data);
        } catch (err) {
          // If token is invalid or expired, log out
          logout();
          setError('Session expired. Please log in again.');
        } finally {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    };

    fetchUser();
  }, [token]);

  // Handle login
  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      // Using URLSearchParams to send form data format that FastAPI expects
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axios.post('/api/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      const { access_token } = response.data;
      
      // Save token to local storage
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Fetch user info
      const userResponse = await axios.get('/api/users/me', {
        headers: {
          'Authorization': `Bearer ${access_token}`
        }
      });
      
      setUser(userResponse.data);
      return true;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Login failed. Please try again.';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Handle register
  const register = async (email, username, password) => {
    setLoading(true);
    setError(null);
    
    try {
      await axios.post('/api/register', {
        email,
        username,
        password
      });
      
      // Auto login after registration
      return await login(email, password);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Registration failed. Please try again.';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Handle logout
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  // Check if user is authenticated
  const isAuthenticated = !!token && !!user;

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      error,
      isAuthenticated,
      login,
      register,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  );
}; 