import qbittorrentapi
from qbittorrentapi import Client, TorrentDictionary
import os
from datetime import datetime, timedelta
import time
import schedule
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_private_and_public_tag_if_not_exists(qbt_client: Client):
    tags = qbt_client.torrent_tags.tags
    if "private" not in tags:
        qbt_client.torrent_tags.create_tags(tags="private")
        logging.info("Created 'private' tag")
    if "public" not in tags:
        qbt_client.torrent_tags.create_tags(tags="public")
        logging.info("Created 'public' tag")


def is_private_torrent(torrent: TorrentDictionary) -> bool:
    dht_tracker = list(filter(lambda x: x.url == "** [DHT] **", torrent.trackers))[0]
    is_private = dht_tracker.msg == "This torrent is private"
    return is_private


def set_private_public_tags(qbt_client: Client):
    create_private_and_public_tag_if_not_exists(qbt_client)
    try:
        qbt_client.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        logging.error(f"Login failed: {e}")
        return
    torrents = qbt_client.torrents_info()
    for torrent in torrents:
        logging.info(
            f"Name: {torrent.name}, Size: {torrent.size}, Progress: {torrent.progress * 100:.2f}%"
        )
        tags = get_tags_list(torrent)
        is_private = is_private_torrent(torrent)
        if is_private:
            if "private" not in tags:
                torrent.add_tags(tags="private")
                logging.info(f"Added 'private' tag to torrent: {torrent.name}")
            if "public" in tags:
                torrent.remove_tags(tags="public")
                logging.info(f"Removed 'public' tag from torrent: {torrent.name}")
        else:
            if "public" not in tags:
                torrent.add_tags(tags="public")
                logging.info(f"Added 'public' tag to torrent: {torrent.name}")
            if "private" in tags:
                torrent.remove_tags(tags="private")
                logging.info(f"Removed 'private' tag from torrent: {torrent.name}")


def get_tags_list(torrent: TorrentDictionary) -> list:
    tags = torrent.tags
    if tags:
        return tags.split(", ")
    return []


def set_public_tagged_torrent_upload_limit(qbt_client: Client):
    torrents = qbt_client.torrents_info()
    for torrent in torrents:
        tags = get_tags_list(torrent)
        public_upload_limit_30d = 200 * 1000
        public_upload_limit_1y = 50 * 1000
        public_upload_limit_new = 500 * 1000
        added_date = datetime.fromtimestamp(torrent.info.added_on)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        one_year_ago = datetime.now() - timedelta(days=365)
        logging.info(
            f"Torrent: {torrent.name}, Added on: {added_date}, Tags: {tags}, Upload limit: {torrent.up_limit} KB/s"
        )
        if "public" in tags:
            if added_date < one_year_ago:
                if torrent.up_limit != public_upload_limit_1y:
                    torrent.set_upload_limit(limit=public_upload_limit_1y)
                    logging.info(
                        f"Updated upload limit for torrent: {torrent.name} to {public_upload_limit_1y}"
                    )
            elif added_date < thirty_days_ago:
                if torrent.up_limit != public_upload_limit_30d:
                    torrent.set_upload_limit(limit=public_upload_limit_30d)
                    logging.info(
                        f"Updated upload limit for torrent: {torrent.name} to {public_upload_limit_30d}"
                    )
            else:
                if torrent.up_limit != public_upload_limit_new:
                    torrent.set_upload_limit(limit=public_upload_limit_new)
                    logging.info(
                        f"Updated upload limit for torrent: {torrent.name} to {public_upload_limit_new}"
                    )


def main(qbt_client: Client):
    set_private_public_tags(qbt_client)
    set_public_tagged_torrent_upload_limit(qbt_client)


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
            schedule.every(int(os.getenv("QBT_INTERVAL",5))).minutes.do(main, qbt_client=qbt_client)
            while True:
                schedule.run_pending()
                logging.getLogger().handlers[0].flush()
                time.sleep(1)  # wait one minute
        except qbittorrentapi.LoginFailed as e:
            logging.error(f"Login failed: {e}")
