import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class WatchCardHeroVideo extends YTNode {
    static type = 'WatchCardHeroVideo';
    endpoint;
    call_to_action_button;
    hero_image;
    label;
    constructor(data) {
        super();
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        this.call_to_action_button = Parser.parseItem(data.callToActionButton);
        this.hero_image = Parser.parseItem(data.heroImage);
        this.label = data.lengthText?.accessibility.accessibilityData.label || '';
    }
}
//# sourceMappingURL=WatchCardHeroVideo.js.map