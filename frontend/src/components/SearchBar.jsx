import React, { useState } from 'react';

function SearchBar({ onSearch }) {
    const [lat, setLat] = useState('');
    const [long, setLong] = useState('');
    const [radius, setRadius] = useState(5000);
    const [semanticQuery, setSemanticQuery] = useState('');
    const [isSemantic, setIsSemantic] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        onSearch({ lat, long, radius, semanticQuery, isSemantic });
    };

    return (
        <form onSubmit={handleSubmit} className="search-bar">
            <div className="search-inputs">
                <input
                    type="number"
                    placeholder="Latitude"
                    value={lat}
                    onChange={(e) => setLat(e.target.value)}
                    required
                    step="any"
                />
                <input
                    type="number"
                    placeholder="Longitude"
                    value={long}
                    onChange={(e) => setLong(e.target.value)}
                    required
                    step="any"
                />
                <input
                    type="number"
                    placeholder="Radius (meters)"
                    value={radius}
                    onChange={(e) => setRadius(e.target.value)}
                    required
                />
            </div>

            <div className="semantic-toggle">
                <label>
                    <input
                        type="checkbox"
                        checked={isSemantic}
                        onChange={(e) => setIsSemantic(e.target.checked)}
                    />
                    Enable Semantic Search
                </label>
            </div>

            {isSemantic && (
                <div className="semantic-input">
                    <input
                        type="text"
                        placeholder="Describe what you're looking for (e.g., 'spicy tacos with good salsa')"
                        value={semanticQuery}
                        onChange={(e) => setSemanticQuery(e.target.value)}
                        required={isSemantic}
                        className="semantic-text-input"
                    />
                </div>
            )}

            <button type="submit">Search</button>
        </form>
    );
}

export default SearchBar;
