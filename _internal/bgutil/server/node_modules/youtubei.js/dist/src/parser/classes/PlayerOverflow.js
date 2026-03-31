import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class PlayerOverflow extends YTNode {
    static type = 'PlayerOverflow';
    endpoint;
    enable_listen_first;
    constructor(data) {
        super();
        this.endpoint = new NavigationEndpoint(data.endpoint);
        this.enable_listen_first = data.enableListenFirst;
    }
}
//# sourceMappingURL=PlayerOverflow.js.map