import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import SearchBar from './components/SearchBar';
import BusinessList from './components/BusinessList';
import ReviewList from './components/ReviewList';
import SemanticResults from './components/SemanticResults';
import Login from './components/Login';
import './App.css';

function AppContent() {
    const { user, login, logout, isAuthenticated, loading: authLoading } = useAuth();
    const [businesses, setBusinesses] = useState([]);
    const [semanticResults, setSemanticResults] = useState([]);
    const [isSemanticMode, setIsSemanticMode] = useState(false);
    const [selectedBusinessId, setSelectedBusinessId] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSearch = async ({ lat, long, radius, semanticQuery, isSemantic }) => {
        setLoading(true);
        setIsSemanticMode(isSemantic);
        setSelectedBusinessId(null);

        try {
            let url;
            if (isSemantic && semanticQuery) {
                url = `http://108.61.214.225:8000/search/semantic?query=${encodeURIComponent(semanticQuery)}&lat=${lat}&long=${long}&radius_meters=${radius}`;
            } else {
                url = `http://108.61.214.225:8000/search/location?lat=${lat}&long=${long}&radius_meters=${radius}`;
            }

            const response = await fetch(url);

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "Search failed");
            }

            const data = await response.json();

            if (isSemantic) {
                setSemanticResults(Array.isArray(data) ? data : []);
                setBusinesses([]);
            } else {
                setBusinesses(Array.isArray(data) ? data : []);
                setSemanticResults([]);
            }
        } catch (error) {
            console.error("Error searching:", error);
            alert(`Error searching: ${error.message}`);
            setSemanticResults([]);
            setBusinesses([]);
        } finally {
            setLoading(false);
        }
    };

    if (authLoading) {
        return <div className="App"><p>Loading...</p></div>;
    }

    if (!isAuthenticated()) {
        return <Login onLogin={login} />;
    }

    const handleLogout = () => {
        logout();
        window.location.reload();
    };

    return (
        <div className="App">
            <div className="app-header">
                <h1>Yelp Distributed Discovery</h1>
                <div className="user-info">
                    <span>Welcome, {user?.name || user?.user_id}</span>
                    <button onClick={handleLogout} className="logout-button">Logout</button>
                </div>
            </div>

            {!selectedBusinessId ? (
                <>
                    <SearchBar onSearch={handleSearch} />
                    {loading ? (
                        <p>Loading...</p>
                    ) : isSemanticMode ? (
                        <SemanticResults results={semanticResults} onSelect={setSelectedBusinessId} />
                    ) : (
                        <BusinessList businesses={businesses} onSelect={setSelectedBusinessId} />
                    )}
                </>
            ) : (
                <ReviewList businessId={selectedBusinessId} onBack={() => setSelectedBusinessId(null)} />
            )}
        </div>
    );
}

function App() {
    return (
        <AuthProvider>
            <AppContent />
        </AuthProvider>
    );
}

export default App;
