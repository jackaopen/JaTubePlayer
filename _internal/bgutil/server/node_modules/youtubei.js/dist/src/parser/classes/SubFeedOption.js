import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
export default class SubFeedOption extends YTNode {
    static type = 'SubFeedOption';
    name;
    is_selected;
    endpoint;
    constructor(data) {
        super();
        this.name = new Text(data.name);
        this.is_selected = data.isSelected;
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
    }
}
//# sourceMappingURL=SubFeedOption.js.map