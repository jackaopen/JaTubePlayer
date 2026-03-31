import { YTNode } from '../../helpers.js';
import NavigationEndpoint from '../NavigationEndpoint.js';
export default class MenuServiceItemDownload extends YTNode {
    static type = 'MenuServiceItemDownload';
    has_separator;
    endpoint;
    constructor(data) {
        super();
        this.has_separator = !!data.hasSeparator;
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint || data.serviceEndpoint);
    }
}
//# sourceMappingURL=MenuServiceItemDownload.js.map