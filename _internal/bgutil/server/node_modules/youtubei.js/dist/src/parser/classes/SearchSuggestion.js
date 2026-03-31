import Text from './misc/Text.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class SearchSuggestion extends YTNode {
    static type = 'SearchSuggestion';
    suggestion;
    endpoint;
    icon_type;
    service_endpoint;
    constructor(data) {
        super();
        this.suggestion = new Text(data.suggestion);
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint);
        if (Reflect.has(data, 'icon')) {
            this.icon_type = data.icon.iconType;
        }
        if (Reflect.has(data, 'serviceEndpoint')) {
            this.service_endpoint = new NavigationEndpoint(data.serviceEndpoint);
        }
    }
}
//# sourceMappingURL=SearchSuggestion.js.map