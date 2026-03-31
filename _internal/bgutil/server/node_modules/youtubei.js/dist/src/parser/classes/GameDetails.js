import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class GameDetails extends YTNode {
    static type = 'GameDetails';
    title;
    box_art;
    box_art_overlay_text;
    endpoint;
    is_official_box_art;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.box_art = Thumbnail.fromResponse(data.boxArt);
        this.box_art_overlay_text = new Text(data.boxArtOverlayText);
        this.endpoint = new NavigationEndpoint(data.endpoint);
        this.is_official_box_art = !!data.isOfficialBoxArt;
    }
}
//# sourceMappingURL=GameDetails.js.map