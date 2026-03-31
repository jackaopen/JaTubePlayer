import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
export default class FeedNudge extends YTNode {
    static type = 'FeedNudge';
    title;
    subtitle;
    endpoint;
    apply_modernized_style;
    trim_style;
    background_style;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.subtitle = new Text(data.subtitle);
        this.endpoint = new NavigationEndpoint(data.impressionEndpoint);
        this.apply_modernized_style = data.applyModernizedStyle;
        this.trim_style = data.trimStyle;
        this.background_style = data.backgroundStyle;
    }
}
//# sourceMappingURL=FeedNudge.js.map