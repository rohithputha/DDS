import React from 'react';

function SemanticResults({ results, onSelect }) {
    if (!results || results.length === 0) {
        return <div className="no-results">No relevant businesses found.</div>;
    }

    const businessMap = new Map();

    results.forEach(result => {
        if (!businessMap.has(result.business_id)) {
            businessMap.set(result.business_id, {
                ...result,
                matching_reviews: []
            });
        }
        if (businessMap.get(result.business_id).matching_reviews.length < 3) {
            businessMap.get(result.business_id).matching_reviews.push(result.review_text);
        }
    });

    const uniqueBusinesses = Array.from(businessMap.values());

    return (
        <div className="semantic-results">
            <h2>Found {uniqueBusinesses.length} Relevant Businesses</h2>
            <div className="results-grid">
                {uniqueBusinesses.map((business, index) => (
                    <div
                        key={index}
                        className="semantic-card clickable"
                        onClick={() => onSelect(business.business_id)}
                    >
                        <div className="business-header">
                            <h3>{business.business_name}</h3>
                            <span className="stars">★ {business.business_stars}</span>
                        </div>

                        <p className="business-meta">
                            {business.business_city} • {business.business_categories}
                        </p>

                        <div className="match-snippet">
                            <strong>Top Match:</strong>
                            <p>"{business.matching_reviews[0]}"</p>
                        </div>

                        <small className="relevance">Relevance: {business.score?.toFixed(4)}</small>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default SemanticResults;
