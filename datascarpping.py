import os
import argparse
import pandas as pd
from googleapiclient.discovery import build
from datetime import timedelta

# YouTube API Key (Replace with your API key)
API_KEY = "AIzaSyC9qHxl4OYXXkEFJaSlEFSBluaUSZvtl_E"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def fetch_videos(youtube, genre, max_results=500):
    """Fetch top videos for a specific genre."""
    videos = []
    next_page_token = None

    while len(videos) < max_results:
        request = youtube.search().list(
            q=genre,
            part="snippet",
            type="video",
            maxResults=min(50, max_results - len(videos)),
            pageToken=next_page_token
        )
        response = request.execute()
        videos.extend(response["items"])
        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break

    return videos

def get_video_details(youtube, video_id):
    """Fetch detailed information for a video."""
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics,recordingDetails",
        id=video_id
    )
    response = request.execute()
    return response["items"][0] if response["items"] else None

def parse_duration(duration):
    """Convert ISO 8601 duration to a readable format."""
    try:
        time = timedelta()
        if duration.startswith("P") and "T" in duration:
            time_str = duration.split("T")[1]
            hours, minutes, seconds = 0, 0, 0
            if "H" in time_str:
                hours = int(time_str.split("H")[0])
                time_str = time_str.split("H")[1]
            if "M" in time_str:
                minutes = int(time_str.split("M")[0])
                time_str = time_str.split("M")[1]
            if "S" in time_str:
                seconds = int(time_str.split("S")[0])
            time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        return str(time)
    except:
        return "N/A"

def main():
    parser = argparse.ArgumentParser(description="YouTube Data Scraper")
    parser.add_argument("genre", help="The genre to search for.")
    args = parser.parse_args()

    # Build YouTube API client
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

    print(f"Fetching videos for genre: {args.genre}")
    videos = fetch_videos(youtube, args.genre)

    print("Fetching video details...")
    video_data = []
    for video in videos:
        video_id = video["id"]["videoId"]
        details = get_video_details(youtube, video_id)
        if details:
            snippet = details["snippet"]
            stats = details["statistics"]
            content_details = details["contentDetails"]
            recording_details = details.get("recordingDetails", {})

            video_data.append({
                "Video URL": f"https://www.youtube.com/watch?v={video_id}",
                "Title": snippet["title"],
                "Description": snippet.get("description", ""),
                "Channel Title": snippet["channelTitle"],
                "Keyword Tags": ", ".join(snippet.get("tags", [])),
                "YouTube Video Category": snippet.get("categoryId", ""),
                "Topic Details": snippet.get("categoryId", ""),  # Placeholder
                "Video Published At": snippet["publishedAt"],
                "Video Duration": parse_duration(content_details["duration"]),
                "View Count": stats.get("viewCount", 0),
                "Comment Count": stats.get("commentCount", 0),
                "Captions Available": False,  # To be updated
                "Caption Text": "",          # To be updated
                "Location of Recording": recording_details.get("location", "N/A")
            })

    # Save to CSV
    print("Saving data to CSV...")
    df = pd.DataFrame(video_data)
    output_file = f"{args.genre}_videos.csv"
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
