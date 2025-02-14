from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from app import settings
from app.db.sqlite.tracks import SQLiteTrackMethods
from app.db.sqlite.settings import SettingsSQLMethods as sdb
from app.db.sqlite.favorite import SQLiteFavoriteMethods as favdb
from app.lib.colorlib import ProcessAlbumColors, ProcessArtistColors

from app.lib.taglib import extract_thumb, get_tags
from app.logger import log
from app.models import Album, Artist, Track
from app.utils.filesystem import run_fast_scandir

from app.store.albums import AlbumStore
from app.store.tracks import TrackStore
from app.store.artists import ArtistStore

get_all_tracks = SQLiteTrackMethods.get_all_tracks
insert_many_tracks = SQLiteTrackMethods.insert_many_tracks

POPULATE_KEY = ""


class PopulateCancelledError(Exception):
    pass


class Populate:
    """
    Populates the database with all songs in the music directory

    checks if the song is in the database, if not, it adds it
    also checks if the album art exists in the image path, if not tries to extract it.
    """

    def __init__(self, key: str) -> None:
        global POPULATE_KEY
        POPULATE_KEY = key

        tracks = get_all_tracks()
        tracks = list(tracks)

        dirs_to_scan = sdb.get_root_dirs()

        if len(dirs_to_scan) == 0:
            log.warning(
                (
                        "The root directory is not configured. "
                        + "Open the app in your webbrowser to configure."
                )
            )
            return

        try:
            if dirs_to_scan[0] == "$home":
                dirs_to_scan = [settings.Paths.USER_HOME_DIR]
        except IndexError:
            pass

        files = []

        for _dir in dirs_to_scan:
            files.extend(run_fast_scandir(_dir, full=True)[1])

        untagged = self.filter_untagged(tracks, files)

        if len(untagged) == 0:
            log.info("All clear, no unread files.")
            return

        self.tag_untagged(untagged, key)

        ProcessTrackThumbnails()
        ProcessAlbumColors()
        ProcessArtistColors()

    @staticmethod
    def filter_untagged(tracks: list[Track], files: list[str]):
        tagged_files = [t.filepath for t in tracks]
        return set(files) - set(tagged_files)

    @staticmethod
    def tag_untagged(untagged: set[str], key: str):
        log.info("Found %s new tracks", len(untagged))
        tagged_tracks: list[dict] = []
        tagged_count = 0

        fav_tracks = favdb.get_fav_tracks()
        fav_tracks = "-".join([t[1] for t in fav_tracks])

        for file in tqdm(untagged, desc="Reading files"):
            if POPULATE_KEY != key:
                raise PopulateCancelledError("Populate key changed")

            tags = get_tags(file)

            if tags is not None:
                tagged_tracks.append(tags)
                track = Track(**tags)
                track.is_favorite = track.trackhash in fav_tracks

                TrackStore.add_track(track)

                if not AlbumStore.album_exists(track.albumhash):
                    AlbumStore.add_album(AlbumStore.create_album(track))

                for artist in track.artist:
                    if not ArtistStore.artist_exists(artist.artisthash):
                        ArtistStore.add_artist(Artist(artist.name))

                for artist in track.albumartist:
                    if not ArtistStore.artist_exists(artist.artisthash):
                        ArtistStore.add_artist(Artist(artist.name))

                tagged_count += 1
            else:
                log.warning("Could not read file: %s", file)

        if len(tagged_tracks) > 0:
            insert_many_tracks(tagged_tracks)

        log.info("Added %s/%s tracks", tagged_count, len(untagged))


def get_image(album: Album):
    for track in TrackStore.tracks:
        if track.albumhash == album.albumhash:
            extract_thumb(track.filepath, track.image)
            break


class ProcessTrackThumbnails:
    def __init__(self) -> None:
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(
                tqdm(
                    pool.map(get_image, AlbumStore.albums),
                    total=len(AlbumStore.albums),
                    desc="Extracting track images",
                )
            )

            list(results)
