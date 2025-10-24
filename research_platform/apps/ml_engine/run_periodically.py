from apps.ml_engine.recommendation_engine import ImprovedRecommendationEngine

if __name__=="__main__":
    engine = ImprovedRecommendationEngine()
    engine.build_embeddings()
    # generate recommendations
    for user in User.objects.all():
        engine.generate_for_user(user)
        print(f"Generated recommendations for user: {user.username}")


    