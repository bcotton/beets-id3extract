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
        self.mappings = self.config.get('mappings', {}).items()
        
        # Register fields for each mapping
        for id3_tag, beets_field in self.mappings:
            self.add_media_field(id3_tag.lower(), CustomID3Field(id3_tag))
        
        # Register listeners
        self.register_listener('item_imported', self.item_imported)
        self.register_listener('item_written', self.item_written)

    def item_imported(self, item, path):
        """When an item is imported, read ID3 tags and set corresponding beets fields."""
        mediafile = MediaFile(path)
        for id3_tag, beets_field in self.mappings:
            if hasattr(mediafile, id3_tag.lower()) and getattr(mediafile, id3_tag.lower()):
                setattr(item, beets_field, getattr(mediafile, id3_tag.lower()))
        item.store()

    def item_written(self, item, path):
        """When an item is written, update ID3 tags with corresponding beets fields."""
        mediafile = MediaFile(path)
        for id3_tag, beets_field in self.mappings:
            if hasattr(item, beets_field) and getattr(item, beets_field):
                setattr(mediafile, id3_tag.lower(), getattr(item, beets_field))
        mediafile.save() 