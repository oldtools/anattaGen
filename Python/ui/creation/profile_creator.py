# Import the GameDataFetcher
from Python.ui.creation.game_data_fetcher import GameDataFetcher

class ProfileCreator:
    # ... existing code ...
    
    def create_profile(self, game_data):
        """Create a new game profile"""
        try:
            # ... existing profile creation code ...
            
            # Create the profile directory
            profile_folder_path = os.path.join(self.profiles_dir, safe_name)
            os.makedirs(profile_folder_path, exist_ok=True)
            
            # Create the Game.ini file
            game_ini_path = os.path.join(profile_folder_path, "Game.ini")
            self._create_game_ini(game_ini_path, game_data)
            
            # Fetch additional game data in the background
            self._fetch_additional_game_data(game_data, profile_folder_path)
            
            # ... rest of profile creation code ...
            
            return profile_folder_path
            
        except Exception as e:
            self.status_update.emit(f"Error creating profile: {str(e)}")
            return None
    
    def _fetch_additional_game_data(self, game_data, profile_folder_path):
        """Fetch additional game data from online sources"""
        # Create a GameDataFetcher instance
        data_fetcher = GameDataFetcher(self.main_window)
        
        # Connect signals
        data_fetcher.status_update.connect(self.status_update.emit)
        data_fetcher.fetch_complete.connect(lambda results: self._on_data_fetch_complete(results, profile_folder_path))
        data_fetcher.fetch_error.connect(lambda error: self.status_update.emit(f"Data fetch error: {error}"))
        
        # Start the fetch process
        data_fetcher.fetch_game_data(game_data, profile_folder_path)
    
    def _on_data_fetch_complete(self, results, profile_folder_path):
        """Handle completion of data fetching"""
        if results:
            self.status_update.emit(f"Added {len(results)} data items to profile")
            # You could trigger a refresh of the UI here if needed