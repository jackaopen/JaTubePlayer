import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class MacroMarkersListItem extends YTNode {
    static type = 'MacroMarkersListItem';
    title;
    time_description;
    thumbnail;
    on_tap_endpoint;
    layout;
    is_highlighted;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.time_description = new Text(data.timeDescription);
        this.thumbnail = Thumbnail.fromResponse(data.thumbnail);
        this.on_tap_endpoint = new NavigationEndpoint(data.onTap);
        this.layout = data.layout;
        this.is_highlighted = !!data.isHighlighted;
    }
}
//# sourceMappingURL=MacroMarkersListItem.js.map