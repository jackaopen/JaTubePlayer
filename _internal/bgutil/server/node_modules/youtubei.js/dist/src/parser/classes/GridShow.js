import { YTNode } from '../helpers.js';
import * as Parser from '../parser.js';
import Author from './misc/Author.js';
import Text from './misc/Text.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import ShowCustomThumbnail from './ShowCustomThumbnail.js';
import ThumbnailOverlayBottomPanel from './ThumbnailOverlayBottomPanel.js';
export default class GridShow extends YTNode {
    static type = 'GridShow';
    title;
    thumbnail_renderer;
    endpoint;
    long_byline_text;
    thumbnail_overlays;
    author;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.thumbnail_renderer = Parser.parseItem(data.thumbnailRenderer, ShowCustomThumbnail);
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        this.long_byline_text = new Text(data.longBylineText);
        this.thumbnail_overlays = Parser.parseArray(data.thumbnailOverlays, ThumbnailOverlayBottomPanel);
        this.author = new Author(data.shortBylineText, undefined);
    }
}
//# sourceMappingURL=GridShow.js.map