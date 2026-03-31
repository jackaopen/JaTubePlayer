import Thumbnail from './misc/Thumbnail.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
import AccessibilityData from './misc/AccessibilityData.js';
export default class ChannelThumbnailWithLink extends YTNode {
    static type = 'ChannelThumbnailWithLink';
    thumbnails;
    endpoint;
    accessibility;
    constructor(data) {
        super();
        this.thumbnails = Thumbnail.fromResponse(data.thumbnail);
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        if ('accessibility' in data
            && 'accessibilityData' in data.accessibility) {
            this.accessibility = {
                accessibility_data: new AccessibilityData(data.accessibility.accessibilityData)
            };
        }
    }
    get label() {
        return this.accessibility?.accessibility_data?.label;
    }
}
//# sourceMappingURL=ChannelThumbnailWithLink.js.map