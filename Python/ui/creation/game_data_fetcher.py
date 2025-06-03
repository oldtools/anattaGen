import os
import json
import threading
import requests
from bs4 import BeautifulSoup
import configparser
import time
import queue
import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QCoreApplication

class GameDataFetcher(QObject):
    """Class to fetch and parse game data from Steam and PCGamingWiki"""
    
    # Define signals for thread communication
    status_update = pyqtSignal(str)
    progress_update = pyqtSignal(int, int)  # current, total
    fetch_complete = pyqtSignal(dict)
    fetch_error = pyqtSignal(str)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.base_urls = {}
        self.load_base_urls()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Queue for processing game data
        self.fetch_queue = queue.Queue()
        self.is_processing = False
        self.worker_thread = None
        
        # Debug log file
        self.debug_log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
        os.makedirs(self.debug_log_path, exist_ok=True)
        self.debug_log_file = os.path.join(self.debug_log_path, "fetch_queue_debug.log")
        
        # Connect signals
        self.status_update.connect(self._update_status_bar)
        
        # Log initialization
        self._log_debug("GameDataFetcher initialized")
        self.status_update.emit("GameDataFetcher initialized")
    
    def _update_status_bar(self, message):
        """Update the status bar with the given message"""
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(message)
            # Force UI update
            QCoreApplication.processEvents()
    
    def _log_debug(self, message):
        """Log debug information to file"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        with open(self.debug_log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def load_base_urls(self):
        """Load base URLs from repos.set file"""
        try:
            # Get the app's root directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            app_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
            
            # Try multiple possible locations for repos.set
            repos_set_paths = [
                os.path.join(app_root_dir, "repos.set"),
                os.path.join(app_root_dir, "Python", "repos.set")
            ]
            
            repos_set_path = None
            for path in repos_set_paths:
                if os.path.exists(path):
                    repos_set_path = path
                    break
            
            if not repos_set_path:
                self.status_update.emit(f"repos.set file not found in any of the expected locations")
                return
            
            self.status_update.emit(f"Using repos.set from {repos_set_path}")
            
            # Read the repos.set file
            config = configparser.ConfigParser()
            # Make the parser case-sensitive
            config.optionxform = str
            
            # Read the file manually to handle the format without section headers
            with open(repos_set_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the GLOBAL section
            global_section = ""
            in_global_section = False
            
            for line in content.splitlines():
                if line.strip() == "[GLOBAL]":
                    in_global_section = True
                    continue
                elif line.strip().startswith("[") and line.strip().endswith("]"):
                    in_global_section = False
                    continue
                
                if in_global_section and "=" in line:
                    global_section += line + "\n"
                    # Also directly parse the URL values
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        self.base_urls[key] = value
            
            self.status_update.emit(f"Loaded {len(self.base_urls)} base URLs from repos.set")
            
        except Exception as e:
            self.status_update.emit(f"Error loading base URLs: {str(e)}")
    
    def fetch_game_data(self, game_data, profile_folder_path):
        """
        Queue game data for fetching from Steam and PCGamingWiki
        
        Args:
            game_data: Dictionary containing game information
            profile_folder_path: Path to the profile folder
        """
        # Add to queue
        self.fetch_queue.put((game_data, profile_folder_path))
        queue_size = self.fetch_queue.qsize()
        
        self._log_debug(f"Added to queue: {game_data.get('name_override', '')} - Queue size: {queue_size}")
        self.status_update.emit(f"Added {game_data.get('name_override', '')} to fetch queue. Queue size: {queue_size}")
        
        # Start processing if not already running
        if not self.is_processing:
            self.is_processing = True
            self.worker_thread = threading.Thread(target=self._process_queue)
            self.worker_thread.daemon = True
            self.worker_thread.start()
            self._log_debug("Started worker thread")
        
        return self.worker_thread
    
    def _process_queue(self):
        """Process the queue of games to fetch data for"""
        try:
            total_items = self.fetch_queue.qsize()
            processed_items = 0
            
            self._log_debug(f"Processing queue with {total_items} items")
            
            while not self.fetch_queue.empty():
                # Get the next item from the queue
                game_data, profile_folder_path = self.fetch_queue.get()
                processed_items += 1
                
                game_name = game_data.get('name_override', '') or game_data.get('steam_title', '') or os.path.basename(game_data.get('directory', ''))
                self._log_debug(f"Processing item {processed_items}/{total_items}: {game_name}")
                self.status_update.emit(f"Processing {game_name} ({processed_items}/{total_items})")
                self.progress_update.emit(processed_items, total_items)
                
                # Process the item
                self._fetch_game_data_thread(game_data, profile_folder_path)
                
                # Mark the task as done
                self.fetch_queue.task_done()
                
                # Small delay between items to prevent overwhelming servers
                time.sleep(0.5)
            
            # Reset processing flag when queue is empty
            self.is_processing = False
            self._log_debug("Queue processing completed")
            self.status_update.emit("All metadata fetching completed")
            
        except Exception as e:
            error_msg = f"Error processing queue: {str(e)}"
            self._log_debug(error_msg)
            self.status_update.emit(error_msg)
            self.is_processing = False
    
    def _fetch_game_data_thread(self, game_data, profile_folder_path):
        """Thread function to fetch game data"""
        try:
            # Extract game information
            steam_id = game_data.get('steam_id', '')
            game_name = game_data.get('name_override', '') or game_data.get('steam_title', '') or os.path.basename(game_data.get('directory', ''))
            
            self._log_debug(f"Fetching data for {game_name} (Steam ID: {steam_id})")
            self.status_update.emit(f"Fetching data for {game_name}")
            
            results = {}
            
            # Create the game.ini file path
            game_ini_path = os.path.join(profile_folder_path, "Game.ini")
            
            # Fetch Steam JSON if we have a Steam ID
            if steam_id and steam_id.isdigit():
                self._log_debug(f"Processing Steam ID: {steam_id}")
                self.status_update.emit(f"Processing Steam ID: {steam_id}")
                
                # Force UI update
                QCoreApplication.processEvents()
                
                steam_data = self._fetch_steam_json(steam_id, profile_folder_path)
                if steam_data:
                    results.update(steam_data)
                    # Update game_name if we got a better one from Steam
                    if 'steamName' in steam_data and steam_data['steamName']:
                        game_name = steam_data['steamName']
                        self._log_debug(f"Using Steam name: {game_name}")
                        self.status_update.emit(f"Using Steam name: {game_name}")
            else:
                self._log_debug(f"No valid Steam ID found for {game_name}")
                self.status_update.emit(f"No valid Steam ID found for {game_name}")
            
            # Fetch PCGamingWiki data
            self._log_debug(f"Fetching PCGamingWiki data for {game_name}")
            self.status_update.emit(f"Fetching PCGamingWiki data for {game_name}")
            
            # Force UI update
            QCoreApplication.processEvents()
            
            pcgw_data = self._fetch_pcgw_data(game_name, steam_id, profile_folder_path)
            if pcgw_data:
                results.update(pcgw_data)
            
            # Write results to game.ini
            if results and os.path.exists(game_ini_path):
                self._log_debug(f"Writing results to {game_ini_path}")
                self.status_update.emit(f"Writing results to Game.ini")
                self._write_results_to_ini(results, game_ini_path)
            
            self._log_debug(f"Completed data fetch for {game_name}")
            self.status_update.emit(f"Completed data fetch for {game_name}")
            self.fetch_complete.emit(results)
            
        except Exception as e:
            error_msg = f"Error fetching game data: {str(e)}"
            self._log_debug(error_msg)
            self.status_update.emit(error_msg)
            self.fetch_error.emit(str(e))
    
    def _fetch_steam_json(self, steam_id, profile_folder_path):
        """Fetch Steam JSON data for a game"""
        try:
            # Get the Steam API URL
            steam_api_url = self.base_urls.get('STEAMIDB', 'https://store.steampowered.com/api/appdetails?appids=')
            
            # Construct the full URL
            url = f"{steam_api_url}{steam_id}"
            
            # Create the output file path
            json_file_path = os.path.join(profile_folder_path, f"{steam_id}.json")
            
            # Check if the file already exists
            if os.path.exists(json_file_path):
                self.status_update.emit(f"Steam JSON already exists for app ID {steam_id}")
                # Read the existing file
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return self._parse_steam_json(data, steam_id)
            
            # Download the JSON
            self.status_update.emit(f"Downloading Steam JSON for app ID {steam_id}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Save the JSON to a file
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # Parse the JSON
                data = response.json()
                return self._parse_steam_json(data, steam_id)
            else:
                self.status_update.emit(f"Failed to download Steam JSON: HTTP {response.status_code}")
                return {}
                
        except Exception as e:
            self.status_update.emit(f"Error fetching Steam JSON: {str(e)}")
            return {}
    
    def _parse_steam_json(self, data, steam_id):
        """Parse Steam JSON data"""
        results = {}
        
        try:
            # Check if the data contains the app ID
            if steam_id in data and data[steam_id].get('success', False):
                app_data = data[steam_id]['data']
                
                # Extract relevant information
                results['steamName'] = app_data.get('name', '')
                results['steamReleaseDate'] = app_data.get('release_date', {}).get('date', '')
                results['steamDevelopers'] = ', '.join(app_data.get('developers', []))
                results['steamPublishers'] = ', '.join(app_data.get('publishers', []))
                results['steamGenres'] = ', '.join([genre.get('description', '') for genre in app_data.get('genres', [])])
                results['steamCategories'] = ', '.join([category.get('description', '') for category in app_data.get('categories', [])])
                results['steamDescription'] = app_data.get('short_description', '')
                
                # Get the header image URL
                results['steamHeaderImage'] = app_data.get('header_image', '')
                
                self.status_update.emit(f"Parsed Steam JSON data for {results.get('steamName', 'Unknown')}")
            else:
                self.status_update.emit(f"Steam JSON does not contain valid data for app ID {steam_id}")
        
        except Exception as e:
            self.status_update.emit(f"Error parsing Steam JSON: {str(e)}")
        
        return results
    
    def _fetch_pcgw_data(self, game_name, steam_id, profile_folder_path):
        """Fetch PCGamingWiki data for a game"""
        try:
            results = {}
            html_content = None
            
            # Create the output file path
            html_file_path = os.path.join(profile_folder_path, "pcgw.html")
            
            # Check if the file already exists
            if os.path.exists(html_file_path):
                self._log_debug(f"PCGamingWiki HTML already exists for {game_name}")
                self.status_update.emit(f"PCGamingWiki HTML already exists for {game_name}")
                # Read the existing file
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Parse the existing HTML and return results
                if html_content:
                    self._log_debug(f"Parsing existing HTML for {game_name}")
                    results = self._parse_pcgw_html(html_content)
                    return results
            
            # Try to get the PCGamingWiki URL first via API if we have a Steam ID
            pcgw_url = None
            if steam_id and steam_id.isdigit():
                pcgw_api_url = self.base_urls.get('PCGWAPI', 'https://www.pcgamingwiki.com/api/appid.php?appid=')
                api_url = f"{pcgw_api_url}{steam_id}"
                
                self._log_debug(f"Querying PCGamingWiki API for Steam ID {steam_id}: {api_url}")
                self.status_update.emit(f"Querying PCGamingWiki API for Steam ID {steam_id}")
                
                # Force UI update
                QCoreApplication.processEvents()
                
                try:
                    response = self.session.get(api_url, timeout=15, allow_redirects=True)
                    
                    if response.status_code == 200:
                        # The API redirects to the wiki page
                        pcgw_url = response.url
                        html_content = response.text
                        self._log_debug(f"Found PCGamingWiki page via API: {pcgw_url}")
                        self.status_update.emit(f"Found PCGamingWiki page via API: {pcgw_url}")
                        
                        # Save the HTML to a file
                        with open(html_file_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        
                        self._log_debug(f"Saved PCGamingWiki HTML to {html_file_path}")
                        self.status_update.emit(f"Saved PCGamingWiki HTML to {html_file_path}")
                except Exception as e:
                    error_msg = f"Error querying PCGamingWiki API: {str(e)}"
                    self._log_debug(error_msg)
                    self.status_update.emit(error_msg)
            
            # If we couldn't get the HTML via API, try searching by name
            if not html_content and game_name:
                # Format the game name for the URL - replace spaces with underscores and handle special characters
                formatted_name = game_name.replace(' ', '_')
                formatted_name = formatted_name.replace('&', '%26')
                formatted_name = formatted_name.replace(':', '%3A')
                formatted_name = formatted_name.replace('/', '%2F')
                
                # Try direct URL first
                pcgw_base = self.base_urls.get('PCGWURL', 'https://www.pcgamingwiki.com/wiki/')
                pcgw_url = f"{pcgw_base}{formatted_name}"
                
                self._log_debug(f"Using PCGamingWiki URL based on game name: {pcgw_url}")
                self.status_update.emit(f"Using PCGamingWiki URL based on game name: {pcgw_url}")
                
                # Force UI update
                QCoreApplication.processEvents()
                
                # Download the HTML with retry logic
                self._log_debug(f"Downloading PCGamingWiki HTML for {game_name}")
                self.status_update.emit(f"Downloading PCGamingWiki HTML for {game_name}")
                
                # Try up to 3 times with increasing delays
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        self._log_debug(f"Attempt {retry+1}/{max_retries} to download {pcgw_url}")
                        self.status_update.emit(f"Attempt {retry+1}/{max_retries} to download PCGamingWiki data")
                        
                        # Force UI update
                        QCoreApplication.processEvents()
                        
                        response = self.session.get(pcgw_url, timeout=15, allow_redirects=True)
                        
                        if response.status_code == 200:
                            html_content = response.text
                            
                            # Save the HTML to a file
                            with open(html_file_path, 'w', encoding='utf-8') as f:
                                f.write(html_content)
                            
                            self._log_debug(f"Saved PCGamingWiki HTML to {html_file_path}")
                            self.status_update.emit(f"Saved PCGamingWiki HTML to {html_file_path}")
                            break
                        elif response.status_code == 404:
                            # Try search if direct access fails
                            if retry == 0:  # Only try search on first retry
                                search_url = f"https://www.pcgamingwiki.com/w/index.php?search={formatted_name}&title=Special%3ASearch"
                                self._log_debug(f"Page not found, trying search: {search_url}")
                                self.status_update.emit(f"Page not found, trying search")
                                
                                # Force UI update
                                QCoreApplication.processEvents()
                                
                                search_response = self.session.get(search_url, timeout=15)
                                
                                if search_response.status_code == 200 and "There is a page named" in search_response.text:
                                    # Extract the correct URL from search results
                                    soup = BeautifulSoup(search_response.text, 'html.parser')
                                    result = soup.find('div', class_='searchresults')
                                    if result and result.find('a'):
                                        new_url = "https://www.pcgamingwiki.com" + result.find('a')['href']
                                        self._log_debug(f"Found page via search: {new_url}")
                                        self.status_update.emit(f"Found page via search: {new_url}")
                                        pcgw_url = new_url
                                        continue  # Try again with new URL
                        
                        # If we get here, either all retries failed or we got a non-404 error
                        if retry == max_retries - 1:
                            error_msg = f"Failed to download PCGamingWiki HTML after {max_retries} attempts: HTTP {response.status_code}"
                            self._log_debug(error_msg)
                            self.status_update.emit(error_msg)
                            return {}
                        
                        # Wait before retrying (exponential backoff)
                        wait_time = 2 ** retry
                        self._log_debug(f"Retrying in {wait_time} seconds...")
                        self.status_update.emit(f"Retrying in {wait_time} seconds...")
                        
                        # Force UI update
                        QCoreApplication.processEvents()
                        
                        # Actually wait
                        time.sleep(wait_time)
                        
                    except Exception as e:
                        error_msg = f"Error downloading PCGamingWiki HTML: {str(e)}"
                        self._log_debug(error_msg)
                        self.status_update.emit(error_msg)
                        
                        if retry < max_retries - 1:
                            wait_time = 2 ** retry
                            self._log_debug(f"Retrying in {wait_time} seconds...")
                            self.status_update.emit(f"Retrying in {wait_time} seconds...")
                            
                            # Force UI update
                            QCoreApplication.processEvents()
                            
                            # Actually wait
                            time.sleep(wait_time)
                        else:
                            return {}
            
            # Parse the HTML if we have it
            if html_content:
                self._log_debug(f"Parsing PCGamingWiki HTML for {game_name}")
                results = self._parse_pcgw_html(html_content)
            
            return results
        
        except Exception as e:
            error_msg = f"Error fetching PCGamingWiki data: {str(e)}"
            self._log_debug(error_msg)
            self.status_update.emit(error_msg)
            return {}
    
    def _parse_pcgw_html(self, html_content):
        """Parse PCGamingWiki HTML content"""
        results = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check if the page exists
            if "There is currently no text in this page" in html_content:
                self.status_update.emit("PCGamingWiki page does not exist")
                return results
            
            # Extract game save location
            save_locations = self._extract_save_locations(soup)
            if save_locations:
                results.update(save_locations)
            
            # Extract cloud save information
            cloud_saves = self._extract_cloud_save_info(soup)
            if cloud_saves:
                results.update(cloud_saves)
            
            # Extract configuration file locations
            config_locations = self._extract_config_locations(soup)
            if config_locations:
                results.update(config_locations)
            
            # Extract DRM information
            drm_info = self._extract_drm_info(soup)
            if drm_info:
                results.update(drm_info)
            
            self.status_update.emit(f"Parsed PCGamingWiki HTML data with {len(results)} items")
            
        except Exception as e:
            self.status_update.emit(f"Error parsing PCGamingWiki HTML: {str(e)}")
        
        return results
    
    def _extract_save_locations(self, soup):
        """Extract save game locations from PCGamingWiki HTML"""
        results = {}
        
        try:
            # Look for the save game data table
            save_game_heading = soup.find('span', id='Save_game_data_location')
            
            if save_game_heading:
                # Find the table after this heading
                save_table = save_game_heading.find_parent('h2').find_next_sibling('table')
                
                if save_table:
                    # Extract save locations for different platforms
                    for row in save_table.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            platform = cells[0].get_text(strip=True)
                            location = cells[1].get_text(strip=True)
                            
                            if platform and location:
                                if 'Windows' in platform:
                                    results['saveLocationWindows'] = location
                                elif 'Linux' in platform:
                                    results['saveLocationLinux'] = location
                                elif 'macOS' in platform:
                                    results['saveLocationMac'] = location
            
            # Look for cloud save information
            cloud_heading = soup.find('span', id='Cloud_saves')
            if cloud_heading:
                results['hasCloudSaves'] = 'true'
            else:
                results['hasCloudSaves'] = 'false'
                
        except Exception as e:
            self.status_update.emit(f"Error extracting save locations: {str(e)}")
        
        return results
    
    def _extract_cloud_save_info(self, soup):
        """Extract cloud save information from PCGamingWiki HTML"""
        results = {}
        
        try:
            # Look for the cloud save table
            cloud_heading = soup.find('span', id='Cloud_saves')
            
            if cloud_heading:
                # Find the table after this heading
                cloud_table = cloud_heading.find_parent('h2').find_next_sibling('table')
                
                if cloud_table:
                    # Extract cloud save information for different services
                    for row in cloud_table.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            service = cells[0].get_text(strip=True)
                            support = cells[1].get_text(strip=True)
                            
                            if service and support:
                                if 'Steam' in service:
                                    results['cloudSavesSteam'] = 'Yes' in support
                                elif 'GOG' in service:
                                    results['cloudSavesGOG'] = 'Yes' in support
                                elif 'Epic' in service:
                                    results['cloudSavesEpic'] = 'Yes' in support
                
        except Exception as e:
            self.status_update.emit(f"Error extracting cloud save info: {str(e)}")
        
        return results
    
    def _extract_config_locations(self, soup):
        """Extract configuration file locations from PCGamingWiki HTML"""
        results = {}
        
        try:
            # Look for the configuration file table
            config_heading = soup.find('span', id='Configuration_file.28s.29_location')
            
            if not config_heading:
                config_heading = soup.find('span', id='Configuration_file_location')
            
            if config_heading:
                # Find the table after this heading
                config_table = config_heading.find_parent('h2').find_next_sibling('table')
                
                if config_table:
                    # Extract config locations for different platforms
                    for row in config_table.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            platform = cells[0].get_text(strip=True)
                            location = cells[1].get_text(strip=True)
                            
                            if platform and location:
                                if 'Windows' in platform:
                                    results['configLocationWindows'] = location
                                elif 'Linux' in platform:
                                    results['configLocationLinux'] = location
                                elif 'macOS' in platform:
                                    results['configLocationMac'] = location
                
        except Exception as e:
            self.status_update.emit(f"Error extracting config locations: {str(e)}")
        
        return results
    
    def _extract_drm_info(self, soup):
        """Extract DRM information from PCGamingWiki HTML"""
        results = {}
        
        try:
            # Look for the DRM table
            drm_heading = soup.find('span', id='DRM')
            
            if drm_heading:
                # Find the table after this heading
                drm_table = drm_heading.find_parent('h2').find_next_sibling('table')
                
                if drm_table:
                    drm_list = []
                    
                    # Extract DRM information
                    for row in drm_table.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            drm_type = cells[0].get_text(strip=True)
                            drm_status = cells[1].get_text(strip=True)
                            
                            if drm_type and 'Yes' in drm_status:
                                drm_list.append(drm_type)
                    
                    if drm_list:
                        results['drmTypes'] = ', '.join(drm_list)
                    else:
                        results['drmFree'] = 'true'
                
        except Exception as e:
            self.status_update.emit(f"Error extracting DRM info: {str(e)}")
        
        return results
    
    def _write_results_to_ini(self, results, game_ini_path):
        """Write the results to the game.ini file"""
        try:
            # Read the existing INI file
            config = configparser.ConfigParser()
            config.read(game_ini_path)
            
            # Ensure the CONFIG section exists
            if 'CONFIG' not in config:
                config['CONFIG'] = {}
            
            # Add the results to the CONFIG section
            for key, value in results.items():
                config['CONFIG'][key] = str(value)
            
            # Write the updated INI file
            with open(game_ini_path, 'w', encoding='utf-8') as f:
                config.write(f)
            
            self.status_update.emit(f"Updated game.ini with {len(results)} data items")
            
        except Exception as e:
            self.status_update.emit(f"Error writing results to game.ini: {str(e)}")












