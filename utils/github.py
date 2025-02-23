from github import Github

def get_latest_release(owner, repo):
    try:
        g = Github()

        repository = g.get_repo(f"{owner}/{repo}")
        latest_release = repository.get_latest_release()

        release_info = {
            "tag_name": latest_release.tag_name,
            "name": latest_release.title,
            "published_at": latest_release.published_at,
            "html_url": latest_release.html_url,
            "assets": []
        }

        for asset in latest_release.get_assets():
            release_info["assets"].append({
                "name": asset.name,
                "size": asset.size,
                "download_count": asset.download_count,
                "browser_download_url": asset.browser_download_url
            })

        return release_info
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_latest_pre_release_assets(owner, repo):
    try:
        g = Github()
        repository = g.get_repo(f"{owner}/{repo}")
        releases = repository.get_releases()

        # Filter for pre-releases and sort them by their publication date, newest first
        pre_releases = sorted(
            (release for release in releases if release.prerelease),
            key=lambda r: r.published_at,
            reverse=True
        )

        if not pre_releases:
            print("No pre-releases found.")
            return None

        # Get the most up-to-date pre-release
        latest_pre_release = pre_releases[0]

        # Collect asset information in a list
        assets = [
            {
                "name": asset.name,
                "size": asset.size,
                "download_count": asset.download_count,
                "browser_download_url": asset.browser_download_url,
                "created_at": asset.created_at
            }
            for asset in latest_pre_release.get_assets()
        ]

        # Return a dictionary similar to get_latest_release
        release_info = {
            "tag_name": latest_pre_release.tag_name,
            "name": latest_pre_release.title,
            "published_at": latest_pre_release.published_at,
            "html_url": latest_pre_release.html_url,
            "assets": assets
        }

        return release_info
    except Exception as e:
        print(f"An error occurred: {e}")
        return None