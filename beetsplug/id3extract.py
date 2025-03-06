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

class CustomID3Field(MediaField):
    """A field for a custom ID3 tag."""
    def __init__(self, tag_name):
        super(CustomID3Field, self).__init__(
            MP3DescStorageStyle(tag_name),
            MP3StorageStyle(tag_name),
            MP4StorageStyle(f'----:com.apple.iTunes:{tag_name}'),
            StorageStyle(tag_name)
        )

class ID3ExtractPlugin(BeetsPlugin):
    def __init__(self):
        super(ID3ExtractPlugin, self).__init__()
        # Get mappings from config
        try:
            config_mappings = dict(self.config['mappings'])
            self._log.debug('Loaded mappings: {}', dict(config_mappings))
        except:
            self._log.warning('No mappings found in config, using empty mapping')
            config_mappings = {}
            
        if not isinstance(config_mappings, dict):
            self._log.warning('Invalid mappings configuration. Expected a dictionary, got {}', type(config_mappings))
            config_mappings = {}
        self.mappings = config_mappings.items()
        self._log.debug('Loaded mappings: {}', dict(self.mappings))
        
        # Register fields for each mapping
        for id3_tag, beets_field in self.mappings:
            self._log.debug('Registering field mapping: {} -> {}', id3_tag, beets_field)
            self.add_media_field(id3_tag.lower(), CustomID3Field(id3_tag))
        
        # Register listeners
        self.register_listener('item_imported', self.item_imported)
        self.register_listener('item_written', self.item_written)

        self._log.debug('ID3ExtractPlugin initialized')

    def item_imported(self, item, path):
        """When an item is imported, read ID3 tags and set corresponding beets fields."""
        self._log.debug('Processing imported item: {}', path)
        mediafile = MediaFile(path)
        for id3_tag, beets_field in self.mappings:
            if hasattr(mediafile, id3_tag.lower()):
                value = getattr(mediafile, id3_tag.lower())
                if value:
                    self._log.debug('Found {} tag: {}', id3_tag, value)
                    setattr(item, beets_field, value)
                else:
                    self._log.debug('{} tag exists but is empty', id3_tag)
            else:
                self._log.debug('No {} tag found', id3_tag)
        item.store()

    def item_written(self, item, path):
        """When an item is written, update ID3 tags with corresponding beets fields."""
        self._log.debug('Processing written item: {}', path)
        mediafile = MediaFile(path)
        for id3_tag, beets_field in self.mappings:
            if hasattr(item, beets_field):
                value = getattr(item, beets_field)
                if value:
                    self._log.debug('Writing {} to {} tag: {}', beets_field, id3_tag, value)
                    setattr(mediafile, id3_tag.lower(), value)
                else:
                    self._log.debug('{} field exists but is empty', beets_field)
            else:
                self._log.debug('No {} field found', beets_field)
        mediafile.save() 