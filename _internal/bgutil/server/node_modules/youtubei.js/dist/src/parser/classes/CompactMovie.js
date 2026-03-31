import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Author from './misc/Author.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import Menu from './menus/Menu.js';
import { timeToSeconds } from '../../utils/Utils.js';
export default class CompactMovie extends YTNode {
    static type = 'CompactMovie';
    id;
    title;
    top_metadata_items;
    thumbnails;
    thumbnail_overlays;
    author;
    duration;
    endpoint;
    badges;
    use_vertical_poster;
    menu;
    constructor(data) {
        super();
        const overlay_time_status = data.thumbnailOverlays
            .find((overlay) => overlay.thumbnailOverlayTimeStatusRenderer)
            ?.thumbnailOverlayTimeStatusRenderer.text || 'N/A';
        this.id = data.videoId;
        this.title = new Text(data.title);
        this.top_metadata_items = new Text(data.topMetadataItems);
        this.thumbnails = Thumbnail.fromResponse(data.thumbnail);
        this.thumbnail_overlays = Parser.parseArray(data.thumbnailOverlays);
        this.author = new Author(data.shortBylineText);
        const durationText = data.lengthText ? new Text(data.lengthText).toString() : new Text(overlay_time_status).toString();
        this.duration = {
            text: durationText,
            seconds: timeToSeconds(durationText)
        };
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        this.badges = Parser.parseArray(data.badges);
        this.use_vertical_poster = data.useVerticalPoster;
        this.menu = Parser.parseItem(data.menu, Menu);
    }
}
//# sourceMappingURL=CompactMovie.js.map