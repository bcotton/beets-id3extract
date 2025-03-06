"""A plugin that maps arbitrary ID3 tags to beets custom fields.

Configuration:
    The plugin is configured through the beets config.yaml file. Add mappings
    under the 'id3extract' section to specify which ID3 tags should be mapped
    to which beets fields.

    Example config:
        plugins:
            - id3extract

        id3extract:
            mappings:
                WOAS: track_id      # Maps WOAS ID3 tag to track_id
                CUSTOM: custom_field # Maps CUSTOM ID3 tag to custom_field
                # Add any other mappings as needed
"""

from beets.plugins import BeetsPlugin
from mediafile import MediaFile, MediaField, MP3DescStorageStyle, MP3StorageStyle, MP4StorageStyle, StorageStyle

class MP3URLStorageStyle(MP3StorageStyle):
    """Storage for ID3 URL frames (like WOAS)."""
    def get(self, mutagen_file):
        try:
            return mutagen_file[self.key].url
        except (KeyError, AttributeError):
            return None

    def set(self, mutagen_file, value):
        from mutagen.id3 import WOAS
        mutagen_file[self.key] = WOAS(encoding=3, url=value)

class CustomID3Field(MediaField):
    """A field for a custom ID3 tag."""
    def __init__(self, tag_name):
        super(CustomID3Field, self).__init__(
            MP3URLStorageStyle(tag_name),
            MP4StorageStyle(f'----:com.apple.iTunes:{tag_name}'),
            StorageStyle(tag_name)
        )

class ID3ExtractPlugin(BeetsPlugin):
    def __init__(self):
        super(ID3ExtractPlugin, self).__init__()
        # Get mappings from config
        try:
            raw_mappings = dict(self.config['mappings'])
            # Convert config values to strings
            config_mappings = {str(k): str(v) for k, v in raw_mappings.items()}
            self._log.debug('Loaded mappings: {}', config_mappings)
        except:
            self._log.warning('No mappings found in config, using empty mapping')
            config_mappings = {}
            
        if not isinstance(config_mappings, dict):
            self._log.warning('Invalid mappings configuration. Expected a dictionary, got {}', type(config_mappings))
            config_mappings = {}
        self.mappings = list(config_mappings.items())
        self._log.debug('Processed mappings: {}', self.mappings)
        
        # Register fields for each mapping
        for id3_tag, beets_field in self.mappings:
            self._log.debug('Registering field mapping: {} -> {}', id3_tag, beets_field)
            self.add_media_field(id3_tag.lower(), CustomID3Field(id3_tag))
        
        # Register listeners
        self.register_listener('item_imported', self.item_imported)  # For singleton imports
        self.register_listener('album_imported', self.album_imported)  # For album imports
        self.register_listener('write', self.on_write)

        self._log.debug('ID3ExtractPlugin initialized')

    def process_item(self, item):
        """Process a single item, reading ID3 tags and setting beets fields."""
        self._log.debug('Processing item: {}', item.path)
        mediafile = MediaFile(item.path)
        for id3_tag, beets_field in self.mappings:
            if hasattr(mediafile, id3_tag.lower()):
                value = getattr(mediafile, id3_tag.lower())
                if value:
                    # Handle Spotify URLs in WOAS field
                    if id3_tag == 'WOAS' and value.startswith('https://open.spotify.com/track/'):
                        spotify_id = value.split('/')[-1].split('?')[0]  # Handle potential query params
                        self._log.debug('Extracted Spotify ID from WOAS: {}', spotify_id)
                        value = spotify_id
                    
                    self._log.debug('Found {} tag: {}', id3_tag, value)
                    setattr(item, beets_field, value)
                else:
                    self._log.debug('{} tag exists but is empty', id3_tag)
            else:
                self._log.debug('No {} tag found', id3_tag)
        item.store()

    def item_imported(self, lib, item):
        """When a singleton item is imported."""
        self._log.debug('Processing singleton import: {}', item.path)
        self.process_item(item)

    def album_imported(self, lib, album):
        """When an album is imported, process all its items."""
        self._log.debug('Processing album import: {}', album.album)
        for item in album.items():
            self.process_item(item)

    def on_write(self, item, path, tags):
        """When an item is about to be written, update the tags dictionary with our custom fields."""
        self._log.debug('Processing write event for: {}', path)
        for id3_tag, beets_field in self.mappings:
            if hasattr(item, beets_field):
                value = getattr(item, beets_field)
                if value:
                    self._log.debug('Adding {} to tags with value: {}', id3_tag.lower(), value)
                    tags[id3_tag.lower()] = value
                else:
                    self._log.debug('{} field exists but is empty', beets_field)
            else:
                self._log.debug('No {} field found', beets_field) 