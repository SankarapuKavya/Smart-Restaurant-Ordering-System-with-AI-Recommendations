from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from .models import Dish, Rating


# -------------------------------
# CONTENT BASED FILTERING
# -------------------------------
def content_based_recommend(user_preferences):

    dishes = Dish.objects.all()

    if not dishes:
        return []

    descriptions = [dish.description for dish in dishes]

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(descriptions)

    user_vector = tfidf.transform([user_preferences])

    similarity_scores = cosine_similarity(user_vector, tfidf_matrix)

    ranked_dishes = sorted(
        list(zip(dishes, similarity_scores[0])),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked_dishes


# -------------------------------
# COLLABORATIVE FILTERING
# -------------------------------
def collaborative_score(user):

    ratings = Rating.objects.all().values()

    df = pd.DataFrame(ratings)

    if df.empty:
        return {}

    user_item_matrix = df.pivot_table(
        index='user_id',
        columns='restaurant_id',
        values='rating'
    ).fillna(0)

    similarity = cosine_similarity(user_item_matrix)

    similar_users = similarity[user.id - 1]

    return similar_users


# -------------------------------
# HYBRID RECOMMENDATION
# -------------------------------
def hybrid_recommendation(user_preferences):

    content_results = content_based_recommend(user_preferences)

    final_results = []

    for dish, score in content_results:

        final_results.append((dish, final_score))

    final_results.sort(key=lambda x: x[1], reverse=True)

    return final_results[:5]