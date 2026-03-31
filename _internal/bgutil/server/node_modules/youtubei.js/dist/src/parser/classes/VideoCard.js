import Author from './misc/Author.js';
import Text from './misc/Text.js';
import Video from './Video.js';
export default class VideoCard extends Video {
    static type = 'VideoCard';
    metadata_text;
    constructor(data) {
        super(data);
        if (Reflect.has(data, 'metadataText')) {
            this.metadata_text = new Text(data.metadataText);
            if (this.metadata_text.text) {
                this.short_view_count = new Text({ simpleText: this.metadata_text.text.split('·')[0]?.trim() });
                this.published = new Text({ simpleText: this.metadata_text.text.split('·')[1]?.trim() });
            }
        }
        if (Reflect.has(data, 'bylineText')) {
            this.author = new Author(data.bylineText, data.ownerBadges, data.channelThumbnailSupportedRenderers?.channelThumbnailWithLinkRenderer?.thumbnail);
        }
    }
}
//# sourceMappingURL=VideoCard.js.map