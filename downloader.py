import yt_dlp
import sys
import os
import imageio_ffmpeg

YOUTUBE_LINKS = [
    # Add your YouTube URLs here, e.g.:
    # "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
]

OUTPUT_DIR = "downloads"

def download_videos(links: list[str]):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    ydl_opts = {
        # Prefer 720p mp4 video + best audio, merge into mp4
        "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(OUTPUT_DIR, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
        "ffmpeg_location": imageio_ffmpeg.get_ffmpeg_exe(),
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


if __name__ == "__main__":
    # Accept URLs as arguments frmo the terminal itself, or you can just edit in the code, provision for both is there
    links = sys.argv[1:] if len(sys.argv) > 1 else YOUTUBE_LINKS

    if not links:
        print("Usage:  python downloader.py <url1> <url2> ...")
        print("   or:  add URLs to the YOUTUBE_LINKS list in this file.")
        sys.exit(1)

    download_videos(links)
