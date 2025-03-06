# ID3Extract Plugin for beets

A [beets](https://beets.io) plugin that maps arbitrary ID3 tags to beets custom fields. This plugin is particularly useful for preserving custom ID3 tags during your music library management with beets.

## Use Cases

- Extract Spotify track IDs from WOAS (Work Of Art Source) ID3 tags
- Preserve custom ID3 tags in your beets database
- Synchronize ID3 tags with beets fields during import and write operations

## Installation

### Using pip (recommended)

```bash
pip install beets-id3extract
```

### Manual Installation

1. Clone this repository or copy `id3extract.py` to your beets plugin directory:
```bash
cp id3extract.py ~/.config/beets/beetsplug/
```

2. Enable the plugin in your beets config file (`config.yaml`):
```yaml
plugins:
    - id3extract
```

## Configuration

Configure the plugin by adding an `id3extract` section to your `config.yaml`. Define mappings between ID3 tags and beets fields:

```yaml
id3extract:
    mappings:
        WOAS: track_id      # Maps WOAS ID3 tag to track_id field
        CUSTOM: custom_field # Maps any custom ID3 tag to a beets field
```

Each mapping consists of:
- Key: The ID3 tag name (e.g., 'WOAS')
- Value: The beets field to store the tag value in

## Special Features

### Spotify ID Extraction

When mapping the WOAS tag, if the value is a Spotify track URL, the plugin automatically extracts just the Spotify ID:

```
WOAS: "https://open.spotify.com/track/2BOUrjXoRIo2YHVAyZyXVX"
↓
track_id: "2BOUrjXoRIo2YHVAyZyXVX"
```

## Operation

The plugin operates at three key points:

1. **During Import** (both singleton and album imports):
   - Reads configured ID3 tags from the audio files
   - Stores their values in the specified beets fields
   - Handles special cases like Spotify URL extraction

2. **During Write Operations**:
   - When beets writes tags to files
   - Ensures custom fields are written back to their corresponding ID3 tags

3. **Database Storage**:
   - All mapped values are stored in the beets database
   - Preserved across library operations

## Debugging

Run beets with the verbose flag to see detailed logging:

```bash
beet -v import path/to/music
```

This will show:
- Which tags are found/not found
- Values being extracted
- Spotify ID extraction (when applicable)
- Write operations

## Requirements

- beets 1.6.0 or later
- mediafile
- mutagen (for ID3 tag handling)

## Development

To set up a development environment:

```bash
git clone https://github.com/your-username/beets-id3extract.git
cd beets-id3extract
pip install -e .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
