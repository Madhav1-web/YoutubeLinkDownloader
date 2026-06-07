import yt_dlp
import sys
import os
import imageio_ffmpeg

YOUTUBE_LINKS = [
    # Add individual YouTube URLs here, e.g.:
    # "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
]

PLAYLIST_LINKS = [
    # Add YouTube playlist URLs here, e.g.:
    # "https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxxxxxxxx",
    "https://www.youtube.com/playlist?list=PLW-zja9ufsdjEntkQNd0Y9ZqU503M9Xm_"
]

OUTPUT_DIR = "downloads"

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

FORMAT = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]"


def is_playlist_url(url: str) -> bool:
    return "list=" in url and ("playlist" in url or "list=" in url)


def extract_playlist_video_urls(playlist_url: str) -> list[str]:
    """Extract individual video URLs from a playlist using yt-dlp."""
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,  # don't download, just list entries
        "skip_download": True,
        "noplaylist": False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    if not info:
        return []

    entries = info.get("entries") or []
    urls = []
    for entry in entries:
        if not entry:
            continue
        video_id = entry.get("id") or entry.get("url", "")
        if video_id and not video_id.startswith("http"):
            urls.append(f"https://www.youtube.com/watch?v={video_id}")
        elif video_id.startswith("http"):
            urls.append(video_id)

    return urls


def download_videos(links: list[str]):
    """Download a list of individual video URLs."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    ydl_opts = {
        "format": FORMAT,
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(OUTPUT_DIR, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
        "ffmpeg_location": FFMPEG,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        failed = []
        for url in links:
            url = url.strip()
            if not url:
                continue
            print(f"\nDownloading: {url}")
            try:
                ydl.download([url])
            except yt_dlp.utils.DownloadError as e:
                print(f"  ERROR: {e}")
                failed.append(url)

    if failed:
        print(f"\nFailed downloads ({len(failed)}):")
        for u in failed:
            print(f"  {u}")
    else:
        print("\nAll downloads completed successfully.")


def download_playlist(playlist_url: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    ydl_opts = {
        "format": FORMAT,
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(OUTPUT_DIR, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(ext)s"),
        "noplaylist": False,
        "quiet": False,
        "no_warnings": False,
        "ffmpeg_location": FFMPEG,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
        print(f"\nPlaylist download completed: {playlist_url}")
    except yt_dlp.utils.DownloadError as e:
        print(f"Direct playlist download failed: {e}")
        print("Falling back to extracting individual video URLs...")
        video_urls = extract_playlist_video_urls(playlist_url)
        if not video_urls:
            print(f"ERROR: Could not extract any videos from playlist: {playlist_url}")
            return
        print(f" Found {len(video_urls)} videos. Downloading individually")
        download_videos(video_urls)


if __name__ == "__main__":
    # Collect raw inputs: CLI args or the hardcoded lists
    raw_inputs = sys.argv[1:] if len(sys.argv) > 1 else (YOUTUBE_LINKS + PLAYLIST_LINKS)

    if not raw_inputs:
        print("Usage:  python downloader.py <url1> <url2> ...")
        print("   or:  add URLs to YOUTUBE_LINKS or PLAYLIST_LINKS in this file.")
        sys.exit(1)

    individual = []
    playlists = []
    for url in raw_inputs:
        url = url.strip()
        if not url:
            continue
        if is_playlist_url(url):
            playlists.append(url)
        else:
            individual.append(url)

    for pl in playlists:
        download_playlist(pl)

    if individual:
        download_videos(individual)
