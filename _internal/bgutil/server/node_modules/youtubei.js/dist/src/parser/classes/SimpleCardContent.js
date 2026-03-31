import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
export default class SimpleCardContent extends YTNode {
    static type = 'SimpleCardContent';
    image;
    title;
    display_domain;
    show_link_icon;
    call_to_action;
    endpoint;
    constructor(data) {
        super();
        this.image = Thumbnail.fromResponse(data.image);
        this.title = new Text(data.title);
        this.display_domain = new Text(data.displayDomain);
        this.show_link_icon = data.showLinkIcon;
        this.call_to_action = new Text(data.callToAction);
        this.endpoint = new NavigationEndpoint(data.command);
    }
}
//# sourceMappingURL=SimpleCardContent.js.map