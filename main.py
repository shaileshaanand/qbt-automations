import qbittorrentapi
from qbittorrentapi import Client, TorrentDictionary
import os
from datetime import datetime, timedelta
import time
import schedule
import logging

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def ensure_required_tags_exist(qbt_client: Client):
    tags = qbt_client.torrent_tags.tags
    required_tags = ["private", "public", "paused"]
    for tag in required_tags:
        if tag not in tags:
            qbt_client.torrent_tags.create_tags(tags=tag)
            logging.info(f"Created '{tag}' tag")


def is_private_torrent(torrent: TorrentDictionary) -> bool:
    dht_tracker = list(filter(lambda x: x.url == "** [DHT] **", torrent.trackers))[0]
    is_private = dht_tracker.msg == "This torrent is private"
    return is_private


def set_private_public_tags(qbt_client: Client) -> list[str]:
    changes = []
    try:
        qbt_client.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        logging.error(f"Login failed: {e}")
        return []
    torrents = qbt_client.torrents_info()
    for torrent in torrents:
        logging.debug(
            f"Name: {torrent.name}, Size: {torrent.size}, Progress: {torrent.progress * 100:.2f}%"
        )
        tags = get_tags_list(torrent)
        is_private = is_private_torrent(torrent)
        if is_private:
            if "private" not in tags:
                torrent.add_tags(tags="private")
                msg = f"Added 'private' tag to torrent: {torrent.name}"
                logging.info(msg)
                changes.append(msg)
            if "public" in tags:
                torrent.remove_tags(tags="public")
                msg = f"Removed 'public' tag from torrent: {torrent.name}"
                logging.info(msg)
                changes.append(msg)
        else:
            if "public" not in tags:
                torrent.add_tags(tags="public")
                msg = f"Added 'public' tag to torrent: {torrent.name}"
                logging.info(msg)
                changes.append(msg)
            if "private" in tags:
                torrent.remove_tags(tags="private")
                msg = f"Removed 'private' tag from torrent: {torrent.name}"
                logging.info(msg)
                changes.append(msg)
    return changes


def get_tags_list(torrent: TorrentDictionary) -> list:
    tags = torrent.tags
    if tags:
        return tags.split(", ")
    return []


def set_public_tagged_torrent_upload_limit(qbt_client: Client) -> list[str]:
    changes = []
    torrents = qbt_client.torrents_info()
    for torrent in torrents:
        tags = get_tags_list(torrent)
        public_upload_limit_30d = 200 * 1000
        public_upload_limit_1y = 50 * 1000
        public_upload_limit_new = 500 * 1000
        added_date = datetime.fromtimestamp(torrent.info.added_on)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        one_year_ago = datetime.now() - timedelta(days=365)
        logging.debug(
            f"Torrent: {torrent.name}, Added on: {added_date}, Tags: {tags}, Upload limit: {torrent.up_limit} KB/s"
        )
        if "public" in tags:
            if added_date < one_year_ago:
                if torrent.up_limit != public_upload_limit_1y:
                    torrent.set_upload_limit(limit=public_upload_limit_1y)
                    msg = f"Updated upload limit for torrent: {torrent.name} to {public_upload_limit_1y}"
                    logging.info(msg)
                    changes.append(msg)
            elif added_date < thirty_days_ago:
                if torrent.up_limit != public_upload_limit_30d:
                    torrent.set_upload_limit(limit=public_upload_limit_30d)
                    msg = f"Updated upload limit for torrent: {torrent.name} to {public_upload_limit_30d}"
                    logging.info(msg)
                    changes.append(msg)
            else:
                if torrent.up_limit != public_upload_limit_new:
                    torrent.set_upload_limit(limit=public_upload_limit_new)
                    msg = f"Updated upload limit for torrent: {torrent.name} to {public_upload_limit_new}"
                    logging.info(msg)
                    changes.append(msg)
    return changes


def stop_old_public_torrents(qbt_client: Client) -> list[str]:
    changes = []
    stop_days = int(os.getenv("PUBLIC_TORRENT_STOP_DAYS", 10))
    torrents = qbt_client.torrents_info()
    cutoff_date = datetime.now() - timedelta(days=stop_days)
    for torrent in torrents:
        tags = get_tags_list(torrent)
        if "public" in tags:
            added_date = datetime.fromtimestamp(torrent.info.added_on)
            if added_date < cutoff_date:
                if not (
                    torrent.state.startswith("paused")
                    or torrent.state.startswith("stopped")
                ):
                    torrent.pause()
                    msg = f"Stopped old public torrent (> {stop_days} days): {torrent.name}"
                    logging.info(msg)
                    changes.append(msg)
    return changes


def enforce_torrent_states(qbt_client: Client) -> list[str]:
    changes = []
    torrents = qbt_client.torrents_info()
    for torrent in torrents:
        tags = get_tags_list(torrent)
        if "paused" in tags:
            # If tagged paused, ensure it is paused
            # qBittorrent active states usually do not start with "paused"
            if not (
                torrent.state.startswith("paused")
                or torrent.state.startswith("stopped")
            ):
                torrent.pause()
                msg = f"Paused torrent (tagged 'paused'): {torrent.name}"
                logging.info(msg)
                changes.append(msg)
        else:
            # If not tagged paused, ensure it is force resumed
            if torrent.state not in ["forcedUP", "forcedDL"]:
                # force_start=True will force resume the torrent
                torrent.set_force_start(value=True)
                msg = f"Force resumed torrent: {torrent.name}"
                logging.info(msg)
                changes.append(msg)
    return changes


def main(qbt_client: Client):
    ensure_required_tags_exist(qbt_client)
    tag_changes = set_private_public_tags(qbt_client)
    limit_changes = set_public_tagged_torrent_upload_limit(qbt_client)
    stop_changes = stop_old_public_torrents(qbt_client)
    resume_changes = enforce_torrent_states(qbt_client)

    all_changes = tag_changes + limit_changes + stop_changes + resume_changes

    if all_changes:
        logging.info("--- Run Summary ---")
        logging.info(f"Total changes: {len(all_changes)}")
        for change in all_changes:
            logging.info(f"- {change}")
        logging.info("-------------------")


if __name__ == "__main__":
    logging.info("Starting qBittorrent automation script...")
    conn_info = dict(
        host=os.getenv("QBITTORRENT_HOST", "localhost"),
        port=int(os.getenv("QBITTORRENT_PORT", 8080)),
        username=os.getenv("QBITTORRENT_USERNAME", "admin"),
        password=os.getenv("QBITTORRENT_PASSWORD", "adminadmin"),
    )
    with qbittorrentapi.Client(**conn_info) as qbt_client:
        try:
            qbt_client.auth_log_in()
            logging.info("Successfully logged in to qBittorrent")
            main(qbt_client)
            schedule.every(int(os.getenv("QBT_INTERVAL", 5))).minutes.do(
                main, qbt_client=qbt_client
            )
            while True:
                schedule.run_pending()
                logging.getLogger().handlers[0].flush()
                time.sleep(1)  # wait one minute
        except qbittorrentapi.LoginFailed as e:
            logging.error(f"Login failed: {e}")
