import numpy as np
from sklearn.model_selection import train_test_split

from travelscanner.models.price import Price, JOIN
from travelscanner.models.travel import Travel
from travelscanner.models.tripadvisor_rating import TripAdvisorRating


def load_unscraped_hotels():
    ret_hotels = []

    # Select distinct hotel names and areas without rating
    travels = Travel.select(Travel.hotel, Travel.country, Travel.area).distinct(). \
        join(TripAdvisorRating, join_type=JOIN.LEFT_OUTER, on=((Travel.hotel == TripAdvisorRating.hotel) &
                                                               (Travel.area == TripAdvisorRating.area) &
                                                               (Travel.country == TripAdvisorRating.country))) \
        .where(TripAdvisorRating.rating.is_null(True))

    for travel in travels:
        ret_hotels.append((travel.hotel, travel.area, travel.country))

    return ret_hotels


def load_prices(include_objects=False):
    # Get data from database with join query
    global price_objects
    joined_prices = Travel.select(Travel, Price, TripAdvisorRating).join(TripAdvisorRating, on=(
                (Travel.country == TripAdvisorRating.country) & (Travel.hotel == TripAdvisorRating.hotel) &
                (Travel.area == TripAdvisorRating.area))).switch(Travel).join(Price)

    # Initialize arrays
    if include_objects:
        price_objects = list()
    n_samples = joined_prices.count()
    features = ["All Inclusive", "Meal type", "Duration (days)", "Country", "Guests", "Hotel stars",
                "Days until departure", "Month", "Week", "Departure airport", "Has pool", "Has childpool",
                "Room type", "Weekday", "Day", "Vendor", "TripAdvisor rating", "Review count", "Excellent dist.",
                "Good dist.", "Average dist.", "Poor dist.", "Terrible dist."]

    data = np.empty((n_samples, len(features)))
    target = np.empty((n_samples,))

    # Fill arrays with data
    for i, d in enumerate(joined_prices):
        if include_objects and price_objects is not None:
            price_objects.append(d.price)

        # Set features
        data[i] = [d.price.all_inclusive, d.price.meal, d.duration_days, d.country, d.guests, d.hotel_stars,
                   (d.departure_date - d.price.created_at.date()).days, d.departure_date.month,
                   d.departure_date.isocalendar()[1], d.departure_airport, d.has_pool, d.has_childpool, d.price.room,
                   d.departure_date.weekday(), d.departure_date.day, d.vendor, d.tripadvisorrating.rating,
                   d.tripadvisorrating.review_count, d.tripadvisorrating.excellent, d.tripadvisorrating.good,
                   d.tripadvisorrating.average, d.tripadvisorrating.poor, d.tripadvisorrating.terrible]

        # Set target value
        target[i] = d.price.price

    if include_objects:
        return data, target, features, price_objects
    else:
        return data, target, features


def split_set(x, y, test_ratio=0.8):
    return train_test_split(x, y, train_size=int(len(x) * test_ratio), random_state=4)
