import React from 'react';

const BusinessList = ({ businesses, onSelect }) => {
    if (!businesses || businesses.length === 0) {
        return <p>No businesses found.</p>;
    }

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
            {businesses.map((business) => (
                <div
                    key={business._id?.$oid || business.business_id}
                    className="card"
                    style={{ border: '1px solid #444', borderRadius: '8px', padding: '15px', textAlign: 'left', cursor: 'pointer' }}
                    onClick={() => onSelect(business.business_id)}
                >
                    <h3>{business.name}</h3>
                    <p>{business.address}, {business.city}</p>
                    <p>Stars: {business.stars} ({business.review_count} reviews)</p>
                </div>
            ))}
        </div>
    );
};

export default BusinessList;
