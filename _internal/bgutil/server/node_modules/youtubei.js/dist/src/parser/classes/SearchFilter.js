import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class SearchFilter extends YTNode {
    static type = 'SearchFilter';
    label;
    endpoint;
    tooltip;
    status;
    constructor(data) {
        super();
        this.label = new Text(data.label);
        this.endpoint = new NavigationEndpoint(data.endpoint || data.navigationEndpoint);
        this.tooltip = data.tooltip;
        if (Reflect.has(data, 'status')) {
            this.status = data.status;
        }
    }
    get disabled() {
        return this.status === 'FILTER_STATUS_DISABLED';
    }
    get selected() {
        return this.status === 'FILTER_STATUS_SELECTED';
    }
}
//# sourceMappingURL=SearchFilter.js.map