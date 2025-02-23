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

        pre_releases = sorted(
            (release for release in releases if release.prerelease),
            key=lambda r: r.published_at,
            reverse=True
        )

        if not pre_releases:
            print("No pre-releases found.")
            return None

        latest_pre_release = pre_releases[0]
        assets = latest_pre_release.get_assets()

        asset_info = [
            {
                "name": asset.name,
                "size": asset.size,
                "download_count": asset.download_count,
                "browser_download_url": asset.browser_download_url,
                "created_at": asset.created_at
            }
            for asset in assets
        ]

        return asset_info
    except Exception as e:
        print(f"An error occurred: {e}")
        return None