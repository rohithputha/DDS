import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const ReviewList = ({ businessId, onBack }) => {
    const { user, token } = useAuth();
    const [reviews, setReviews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [newReview, setNewReview] = useState({ stars: 5, text: '' });
    const [business, setBusiness] = useState(null);

    React.useEffect(() => {
        const fetchData = async () => {
            if (!businessId) return;
            try {
                const [reviewsRes, businessRes] = await Promise.all([
                    fetch(`http://108.61.214.225:8000/business/${businessId}/reviews`),
                    fetch(`http://108.61.214.225:8000/business/${businessId}`)
                ]);

                if (!reviewsRes.ok || !businessRes.ok) {
                    throw new Error("Failed to fetch data");
                }

                const reviewsData = await reviewsRes.json();
                const businessData = await businessRes.json();

                setReviews(Array.isArray(reviewsData) ? reviewsData : []);
                setBusiness(businessData);
            } catch (error) {
                console.error("Error fetching data", error);
                setReviews([]);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [businessId]);

    const handleSubmitReview = async (e) => {
        e.preventDefault();

        if (!user || !user.user_id) {
            alert('You must be logged in to write a review');
            return;
        }

        setSubmitting(true);
        try {
            const headers = {
                'Content-Type': 'application/json',
            };

            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch('http://108.61.214.225:8000/reviews', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    business_id: businessId,
                    user_id: user.user_id,
                    stars: parseFloat(newReview.stars),
                    text: newReview.text.trim(),
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to add review");
            }

            const [reviewsRes, businessRes] = await Promise.all([
                fetch(`http://108.61.214.225:8000/business/${businessId}/reviews`),
                fetch(`http://108.61.214.225:8000/business/${businessId}`)
            ]);

            if (reviewsRes.ok) {
                const reviewsData = await reviewsRes.json();
                setReviews(Array.isArray(reviewsData) ? reviewsData : []);
            }

            if (businessRes.ok) {
                const businessData = await businessRes.json();
                setBusiness(businessData);
            }

            // Reset form
            setNewReview({ stars: 5, text: '' });
            alert('Review added successfully!');
        } catch (error) {
            alert('Error adding review: ' + error.message);
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return <p>Loading...</p>;

    return (
        <div className="review-view">
            <button onClick={onBack} className="back-button">← Back to Search</button>

            {business && (
                <div className="business-details-header">
                    <h1>{business.name}</h1>
                    <div className="business-meta-large">
                        <span className="stars-large">★ {business.stars}</span>
                        <span>({business.review_count} reviews)</span>
                        <span> • {business.categories}</span>
                    </div>
                    <p className="address">{business.address}, {business.city}, {business.state}</p>
                </div>
            )}

            <div className="review-section">
                <div className="review-list">
                    <h3>Reviews</h3>
                    {reviews.map((review, idx) => {
                        if (!review) return null;
                        return (
                            <div key={idx} className="review-item">
                                <div className="review-header">
                                    <strong>{review.user_details?.name || 'Unknown User'}</strong>
                                    <span className="stars">★ {review.stars}</span>
                                </div>
                                <p>{review.text}</p>
                            </div>
                        );
                    })}
                </div>

                <div className="add-review-form">
                    <h3>Write a Review</h3>
                    {user && (
                        <p className="review-as-user">Writing as: {user.name || user.user_id}</p>
                    )}
                    <form onSubmit={handleSubmitReview}>
                        <div className="form-group">
                            <label>Rating:</label>
                            <input
                                type="number"
                                min="1"
                                max="5"
                                value={newReview.stars}
                                onChange={(e) => setNewReview({ ...newReview, stars: e.target.value })}
                                disabled={submitting}
                            />
                        </div>
                        <textarea
                            placeholder="Share your experience..."
                            value={newReview.text}
                            onChange={(e) => setNewReview({ ...newReview, text: e.target.value })}
                            required
                            disabled={submitting}
                        />
                        <button type="submit" disabled={submitting || !user}>
                            {submitting ? 'Submitting...' : 'Submit Review'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ReviewList;
