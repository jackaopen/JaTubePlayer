import Text from './misc/Text.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class AccountChannel extends YTNode {
    static type = 'AccountChannel';
    title;
    endpoint;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
    }
}
//# sourceMappingURL=AccountChannel.js.map