import pylast


class LastFMRecommender:
    def __init__(self, api_key, api_secret):
        self.network = pylast.LastFMNetwork(
            api_key=api_key,
            api_secret=api_secret
        )

    def get_similar_tracks(self, artist, track, limit=5):
        """Получить похожие треки"""
        try:
            track_obj = self.network.get_track(artist, track)
            similar = track_obj.get_similar(limit=limit)

            recommendations = []
            for sim_track, similarity in similar:
                recommendations.append({
                    'name': sim_track.title,
                    'artist': sim_track.artist.name,
                    'similarity': similarity,
                    'url': sim_track.get_url()
                })

            return recommendations
        except Exception as e:
            print(f"Ошибка Last.fm: {e}")
            return []

    def get_top_tracks_for_artist(self, artist, limit=5):
        """Получить популярные треки исполнителя"""
        try:
            artist_obj = self.network.get_artist(artist)
            top_tracks = artist_obj.get_top_tracks(limit=limit)

            return [{
                'name': track.title,
                'artist': artist,
                'playcount': track.playcount
            } for track, _ in top_tracks]
        except:
            return []

print(LastFMRecommender("c41a2ca43463fd4bb4f38f4b2cfcd47c", "d9397283f11bafe9c9ccab94f1aff0f1").get_similar_tracks("Mindless Self Indulgence", "Get it up"))