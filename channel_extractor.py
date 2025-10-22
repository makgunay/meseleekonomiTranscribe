import os
import csv
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# OAuth 2.0 scope for YouTube Data API
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

class ChannelExtractor:
    """Extract all videos from a YouTube channel using YouTube Data API v3."""

    def __init__(self):
        self.youtube = None
        self.base_output_path = './video/'

    def authenticate(self) -> Optional[object]:
        """
        Authenticate with YouTube Data API using OAuth 2.0.

        Returns:
            YouTube API client object or None if authentication fails
        """
        creds = None

        # Check for existing token
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}. Re-authenticating...")
                    os.remove('token.json')
                    creds = None

            if not creds:
                if not os.path.exists('client_secret.json'):
                    print("ERROR: client_secret.json not found!")
                    print("Please download OAuth 2.0 credentials from Google Cloud Console")
                    print("(APIs & Services → Credentials → Create OAuth 2.0 Client ID)")
                    return None

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Authentication failed: {e}")
                    return None

            # Save credentials for future use
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            self.youtube = build('youtube', 'v3', credentials=creds)
            return self.youtube
        except Exception as e:
            print(f"Failed to build YouTube client: {e}")
            return None

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """
        Get channel information including uploads playlist ID.

        Args:
            channel_id: YouTube channel ID (starts with UC)

        Returns:
            Dictionary with channel_name and uploads_playlist_id
        """
        try:
            request = self.youtube.channels().list(
                part='contentDetails,snippet',
                id=channel_id
            )
            response = request.execute()

            if not response.get('items'):
                print(f"No channel found with ID: {channel_id}")
                return None

            channel = response['items'][0]
            return {
                'channel_name': channel['snippet']['title'],
                'uploads_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads']
            }
        except HttpError as e:
            print(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            print(f"Error getting channel info: {e}")
            return None

    def get_all_videos(self, uploads_playlist_id: str) -> List[Dict]:
        """
        Get all videos from a channel's uploads playlist.

        Uses two-stage fetching:
        1. Get video IDs from playlist (paginated)
        2. Batch fetch full video details

        Args:
            uploads_playlist_id: Playlist ID for channel uploads

        Returns:
            List of video dictionaries with full metadata
        """
        all_videos = []
        video_ids = []
        next_page_token = None

        print("Fetching video list...")

        while True:
            try:
                # Stage 1: Get video IDs from playlist
                request = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = request.execute()

                # Collect video IDs
                for item in response.get('items', []):
                    video_id = item['snippet']['resourceId']['videoId']
                    video_ids.append(video_id)

                # When we have 50 IDs or no more pages, fetch details
                if len(video_ids) >= 50 or 'nextPageToken' not in response:
                    videos = self._fetch_video_details(video_ids)
                    all_videos.extend(videos)
                    print(f"Processed {len(all_videos)} videos...")
                    video_ids = []  # Clear for next batch

                # Check for more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

            except HttpError as e:
                print(f"HTTP error occurred: {e}")
                break
            except Exception as e:
                print(f"Error fetching videos: {e}")
                break

        print(f"Total videos fetched: {len(all_videos)}")
        return all_videos

    def _fetch_video_details(self, video_ids: List[str]) -> List[Dict]:
        """
        Batch fetch full video details including statistics.

        Args:
            video_ids: List of video IDs to fetch

        Returns:
            List of video dictionaries with full metadata
        """
        if not video_ids:
            return []

        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            )
            response = request.execute()

            videos = []
            for item in response.get('items', []):
                video = self._parse_video_data(item)
                videos.append(video)

            return videos

        except Exception as e:
            print(f"Error fetching video details: {e}")
            return []

    def _parse_video_data(self, item: Dict) -> Dict:
        """
        Parse video data from API response into standard format.

        Args:
            item: Video item from API response

        Returns:
            Dictionary with standardized video metadata
        """
        snippet = item.get('snippet', {})
        statistics = item.get('statistics', {})
        content_details = item.get('contentDetails', {})

        return {
            'video_id': item.get('id', ''),
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'link': f"https://www.youtube.com/watch?v={item.get('id', '')}",
            'publish_date': snippet.get('publishedAt', ''),
            'view_count': statistics.get('viewCount', 'N/A'),
            'like_count': statistics.get('likeCount', 'N/A'),
            'comment_count': statistics.get('commentCount', 'N/A'),
            'duration': content_details.get('duration', ''),
            'tags': snippet.get('tags', []),
            'category_id': snippet.get('categoryId', ''),
            'downloaded': 'No'  # Flag for tracking downloads
        }

    def sanitize_filename(self, name: str) -> str:
        """
        Sanitize channel name for use in filenames.

        Args:
            name: Channel name to sanitize

        Returns:
            Sanitized filename-safe string
        """
        # Keep only alphanumeric, spaces, hyphens, and underscores
        sanitized = re.sub(r'[^\w\s\-]', '', name)
        return sanitized.strip()

    def sync_csv_with_existing_files(self, csv_path: str, folder_path: str):
        """
        Update CSV to mark videos that already have downloaded MP3 files.

        Args:
            csv_path: Path to the CSV file
            folder_path: Folder where MP3 files are stored
        """
        # Get all existing MP3 files (using os.listdir to avoid glob issues)
        existing_video_ids = set()

        try:
            for filename in os.listdir(folder_path):
                if filename.endswith('.mp3'):
                    # Extract video ID from [video_id] pattern
                    if filename.startswith('[') and ']' in filename:
                        video_id = filename.split(']')[0][1:]
                        existing_video_ids.add(video_id)
        except OSError as e:
            print(f"Error reading folder: {e}")
            return

        print(f"Found {len(existing_video_ids)} existing MP3 files")

        # Read CSV
        import csv
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Update rows
        updated = 0
        for row in rows:
            video_id = row.get('video_id', '')
            if video_id in existing_video_ids:
                row['downloaded'] = 'Yes'
                updated += 1

        # Write back to CSV
        if rows:
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                fieldnames = list(rows[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

        print(f"Updated {updated} videos as already downloaded in CSV")

    def save_channel_data(self, videos: List[Dict], channel_name: str) -> tuple[str, str]:
        """
        Save channel video data to CSV and JSON files.

        Creates folder structure: video/{channel_name}/
        Files include timestamp and video count.

        Args:
            videos: List of video dictionaries
            channel_name: Name of the channel

        Returns:
            Tuple of (csv_path, json_path)
        """
        # Create channel-specific folder
        sanitized_name = self.sanitize_filename(channel_name)
        channel_folder = os.path.join(self.base_output_path, sanitized_name)
        os.makedirs(channel_folder, exist_ok=True)

        # Generate filenames with timestamp and count
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        video_count = len(videos)
        base_filename = f"{sanitized_name}_{timestamp}_{video_count}"

        csv_path = os.path.join(channel_folder, f"{base_filename}.csv")
        json_path = os.path.join(channel_folder, f"{base_filename}.json")

        # Save CSV
        self._save_csv(videos, csv_path)

        # Save JSON
        self._save_json(videos, channel_name, json_path)

        # Sync CSV with existing downloaded files
        print(f"\nChecking for existing downloaded files...")
        self.sync_csv_with_existing_files(csv_path, channel_folder)

        print(f"\nData saved to:")
        print(f"  CSV:  {csv_path}")
        print(f"  JSON: {json_path}")

        return csv_path, json_path

    def _save_csv(self, videos: List[Dict], filepath: str):
        """Save videos to CSV file with downloaded flag."""
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            # Field order matching SPECIFICATION.md + downloaded flag
            fieldnames = [
                'video_id', 'title', 'description', 'link', 'publish_date',
                'view_count', 'like_count', 'comment_count', 'duration',
                'tags', 'category_id', 'downloaded'
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for video in videos:
                # Convert tags array to comma-separated string for CSV
                row = video.copy()
                row['tags'] = ', '.join(video.get('tags', []))
                writer.writerow(row)

    def _save_json(self, videos: List[Dict], channel_name: str, filepath: str):
        """Save videos to JSON file with metadata wrapper."""
        data = {
            'channel_name': channel_name,
            'export_date': datetime.now().strftime('%Y%m%d'),
            'video_count': len(videos),
            'videos': videos
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def extract_channel(self, channel_id: str) -> Optional[str]:
        """
        Main method to extract all videos from a channel.

        Args:
            channel_id: YouTube channel ID

        Returns:
            Path to the channel folder or None if failed
        """
        print(f"Starting extraction for channel: {channel_id}")

        # Authenticate
        if not self.youtube:
            print("Authenticating with YouTube API...")
            if not self.authenticate():
                return None

        # Get channel info
        channel_info = self.get_channel_info(channel_id)
        if not channel_info:
            return None

        print(f"Channel: {channel_info['channel_name']}")

        # Get all videos
        videos = self.get_all_videos(channel_info['uploads_playlist_id'])
        if not videos:
            print("No videos found or error occurred")
            return None

        # Save data
        csv_path, json_path = self.save_channel_data(videos, channel_info['channel_name'])

        # Return channel folder path
        sanitized_name = self.sanitize_filename(channel_info['channel_name'])
        return os.path.join(self.base_output_path, sanitized_name)


def main():
    """CLI interface for channel extraction."""
    extractor = ChannelExtractor()

    print("YouTube Channel Video Extractor")
    print("=" * 50)

    channel_id = input("Enter YouTube Channel ID: ").strip()

    if not channel_id:
        print("Error: Channel ID is required")
        return

    try:
        folder_path = extractor.extract_channel(channel_id)
        if folder_path:
            print(f"\nSuccess! Channel data saved to: {folder_path}")
        else:
            print("\nExtraction failed. Please check the error messages above.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
