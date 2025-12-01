import React, { useState } from 'react';
import SearchBar from './components/SearchBar';
import BusinessList from './components/BusinessList';
import ReviewList from './components/ReviewList';
import SemanticResults from './components/SemanticResults';
import './App.css';

function App() {
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
                url = `http://localhost:8000/search/semantic?query=${encodeURIComponent(semanticQuery)}&lat=${lat}&long=${long}&radius_meters=${radius}`;
            } else {
                url = `http://localhost:8000/search/location?lat=${lat}&long=${long}&radius_meters=${radius}`;
            }

            const response = await fetch(url);

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "Search failed");
            }

            const data = await response.json();

            if (isSemantic) {
                setSemanticResults(Array.isArray(data) ? data : []);
                setBusinesses([]); // Clear businesses
            } else {
                setBusinesses(Array.isArray(data) ? data : []);
                setSemanticResults([]); // Clear semantic results
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

    return (
        <div className="App">
            <h1>Yelp Distributed Discovery</h1>

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

export default App;
